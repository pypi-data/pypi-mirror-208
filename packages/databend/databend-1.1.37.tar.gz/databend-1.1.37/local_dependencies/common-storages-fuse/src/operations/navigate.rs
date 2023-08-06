// Copyright 2021 Datafuse Labs
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

use std::sync::Arc;

use chrono::DateTime;
use chrono::Duration;
use chrono::Utc;
use common_catalog::table::NavigationPoint;
use common_catalog::table_context::TableContext;
use common_exception::ErrorCode;
use common_exception::Result;
use common_meta_app::schema::TableStatistics;
use futures::TryStreamExt;
use opendal::EntryMode;
use opendal::Metakey;
use storages_common_cache::LoadParams;
use storages_common_table_meta::meta::TableSnapshot;
use storages_common_table_meta::table::OPT_KEY_SNAPSHOT_LOCATION;
use tracing::warn;

use crate::io::MetaReaders;
use crate::io::SnapshotHistoryReader;
use crate::io::TableMetaLocationGenerator;
use crate::FuseTable;
use crate::FUSE_TBL_SNAPSHOT_PREFIX;

impl FuseTable {
    #[async_backtrace::framed]
    pub async fn navigate_to_time_point(
        &self,
        location: String,
        time_point: DateTime<Utc>,
    ) -> Result<Arc<FuseTable>> {
        self.find(location, |snapshot| {
            if let Some(ts) = snapshot.timestamp {
                ts <= time_point
            } else {
                false
            }
        })
        .await
    }

    #[async_backtrace::framed]
    pub async fn navigate_to_snapshot(
        &self,
        location: String,
        snapshot_id: &str,
    ) -> Result<Arc<FuseTable>> {
        self.find(location, |snapshot| {
            snapshot
                .snapshot_id
                .simple()
                .to_string()
                .as_str()
                .starts_with(snapshot_id)
        })
        .await
    }

    #[async_backtrace::framed]
    pub async fn find<P>(&self, location: String, mut pred: P) -> Result<Arc<FuseTable>>
    where P: FnMut(&TableSnapshot) -> bool {
        let snapshot_version = TableMetaLocationGenerator::snapshot_version(location.as_str());
        let reader = MetaReaders::table_snapshot_reader(self.get_operator());
        // grab the table history as stream
        // snapshots are order by timestamp DESC.
        let mut snapshot_stream = reader.snapshot_history(
            location,
            snapshot_version,
            self.meta_location_generator().clone(),
        );

        // Find the instant which matches the given `time_point`.
        let mut instant = None;
        while let Some(snapshot_with_version) = snapshot_stream.try_next().await? {
            if pred(snapshot_with_version.0.as_ref()) {
                instant = Some(snapshot_with_version);
                break;
            }
        }

        if let Some((snapshot, format_version)) = instant {
            // Load the table instance by the snapshot

            // The `seq` of ident that we cloned here is JUST a place holder
            // we should NOT use it other than a pure place holder.
            let mut table_info = self.table_info.clone();

            // There are more to be kept in snapshot, like engine_options, ordering keys...
            // or we could just keep a clone of TableMeta in the snapshot.
            //
            // currently, here are what we can recovery from the snapshot:

            // 1. the table schema
            table_info.meta.schema = Arc::new(snapshot.schema.clone());

            // 2. the table option `snapshot_location`
            let loc = self
                .meta_location_generator
                .snapshot_location_from_uuid(&snapshot.snapshot_id, format_version)?;
            table_info
                .meta
                .options
                .insert(OPT_KEY_SNAPSHOT_LOCATION.to_owned(), loc);

            // 3. The statistics
            let summary = &snapshot.summary;
            table_info.meta.statistics = TableStatistics {
                number_of_rows: summary.row_count,
                data_bytes: summary.uncompressed_byte_size,
                compressed_data_bytes: summary.compressed_byte_size,
                index_data_bytes: summary.index_size,
            };

            // let's instantiate it
            let table = FuseTable::do_create(table_info)?;
            Ok(table.into())
        } else {
            Err(ErrorCode::TableHistoricalDataNotFound(
                "No historical data found at given point",
            ))
        }
    }

    #[async_backtrace::framed]
    pub async fn navigate_for_purge(
        &self,
        ctx: &Arc<dyn TableContext>,
        instant: Option<NavigationPoint>,
    ) -> Result<(Arc<FuseTable>, Vec<String>)> {
        let retention = Duration::hours(ctx.get_settings().get_retention_period()? as i64);
        let root_snapshot = if let Some(snapshot) = self.read_table_snapshot().await? {
            snapshot
        } else {
            return Err(ErrorCode::TableHistoricalDataNotFound(
                "No historical data found at given point",
            ));
        };

        assert!(root_snapshot.timestamp.is_some());
        let mut time_point = root_snapshot.timestamp.unwrap() - retention;

        let (location, files) = match instant {
            Some(NavigationPoint::TimePoint(point)) => {
                time_point = std::cmp::min(point, time_point);
                self.list_by_time_point(time_point).await
            }
            Some(NavigationPoint::SnapshotID(snapshot_id)) => {
                self.list_by_snapshot_id(snapshot_id.as_str(), time_point)
                    .await
            }
            None => self.list_by_time_point(time_point).await,
        }?;

        let table = self.navigate_to_time_point(location, time_point).await?;

        Ok((table, files))
    }

    #[async_backtrace::framed]
    pub async fn list_by_time_point(
        &self,
        time_point: DateTime<Utc>,
    ) -> Result<(String, Vec<String>)> {
        let prefix = format!(
            "{}/{}/",
            self.meta_location_generator().prefix(),
            FUSE_TBL_SNAPSHOT_PREFIX,
        );

        let files = self
            .list_files(prefix, |_, modified| modified <= time_point)
            .await?;
        if files.is_empty() {
            return Err(ErrorCode::TableHistoricalDataNotFound(
                "No historical data found at given point",
            ));
        }

        let location = files[0].clone();
        let reader = MetaReaders::table_snapshot_reader(self.get_operator());
        let ver = TableMetaLocationGenerator::snapshot_version(location.as_str());
        let load_params = LoadParams {
            location,
            len_hint: None,
            ver,
            put_cache: false,
        };
        let snapshot = reader.read(&load_params).await?;
        // Take the prev snapshot as base snapshot to avoid get orphan snapshot.
        let prev = snapshot.prev_snapshot_id;
        match prev {
            Some((id, v)) => {
                let new_loc = self
                    .meta_location_generator()
                    .snapshot_location_from_uuid(&id, v)?;
                Ok((new_loc, files))
            }
            None => Err(ErrorCode::TableHistoricalDataNotFound(
                "No historical data found at given point",
            )),
        }
    }

    #[async_backtrace::framed]
    pub async fn list_by_snapshot_id(
        &self,
        snapshot_id: &str,
        retention_point: DateTime<Utc>,
    ) -> Result<(String, Vec<String>)> {
        let mut location = None;
        let prefix = format!(
            "{}/{}/",
            self.meta_location_generator().prefix(),
            FUSE_TBL_SNAPSHOT_PREFIX,
        );
        let prefix_loc = format!("{}{}", prefix, snapshot_id);

        let files = self
            .list_files(prefix, |loc, modified| {
                if loc.starts_with(&prefix_loc) {
                    location = Some(loc);
                }
                modified <= retention_point
            })
            .await?;
        let location = location.ok_or(ErrorCode::TableHistoricalDataNotFound(
            "No historical data found at given point",
        ))?;
        Ok((location, files))
    }

    #[async_backtrace::framed]
    pub async fn list_files<F>(&self, prefix: String, mut f: F) -> Result<Vec<String>>
    where F: FnMut(String, DateTime<Utc>) -> bool {
        let mut file_list = vec![];
        let op = self.operator.clone();
        let mut ds = op.list(&prefix).await?;
        while let Some(de) = ds.try_next().await? {
            let meta = op
                .metadata(&de, Metakey::Mode | Metakey::LastModified)
                .await?;
            match meta.mode() {
                EntryMode::FILE => {
                    let modified = meta.last_modified();
                    let location = de.path().to_string();
                    if let Some(modified) = modified {
                        if f(location.clone(), modified) {
                            file_list.push((location, modified));
                        }
                    }
                }
                _ => {
                    warn!("found not snapshot file in {:}, found: {:?}", prefix, de);
                    continue;
                }
            }
        }

        file_list.sort_by(|(_, m1), (_, m2)| m2.cmp(m1));

        Ok(file_list.into_iter().map(|v| v.0).collect())
    }
}
