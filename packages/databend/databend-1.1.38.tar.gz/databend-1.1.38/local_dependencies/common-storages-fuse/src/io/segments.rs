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

use common_base::runtime::execute_futures_in_parallel;
use common_catalog::table_context::TableContext;
use common_exception::Result;
use common_expression::TableSchemaRef;
use opendal::Operator;
use storages_common_cache::CacheAccessor;
use storages_common_cache::LoadParams;
use storages_common_cache_manager::CacheManager;
use storages_common_table_meta::meta::CompactSegmentInfo;
use storages_common_table_meta::meta::Location;
use storages_common_table_meta::meta::SegmentInfo;
use storages_common_table_meta::meta::Versioned;
use tracing::Instrument;

use crate::io::MetaReaders;

#[derive(Clone)]
pub struct SerializedSegment {
    pub path: String,
    pub segment: Arc<SegmentInfo>,
}

// Read segment related operations.
pub struct SegmentsIO {
    ctx: Arc<dyn TableContext>,
    operator: Operator,
    schema: TableSchemaRef,
}

impl SegmentsIO {
    pub fn create(ctx: Arc<dyn TableContext>, operator: Operator, schema: TableSchemaRef) -> Self {
        Self {
            ctx,
            operator,
            schema,
        }
    }

    // Read one segment file by location.
    // The index is the index of the segment_location in segment_locations.
    #[async_backtrace::framed]
    pub async fn read_segment(
        dal: Operator,
        segment_location: Location,
        table_schema: TableSchemaRef,
        put_cache: bool,
    ) -> Result<SegmentInfo> {
        let (path, ver) = segment_location;
        let reader = MetaReaders::segment_info_reader(dal, table_schema);

        // Keep in mind that segment_info_read must need a schema
        let load_params = LoadParams {
            location: path,
            len_hint: None,
            ver,
            put_cache,
        };

        let raw_bytes = reader.read(&load_params).await?;
        SegmentInfo::try_from(raw_bytes.as_ref())
    }

    // Read all segments information from s3 in concurrently.
    #[tracing::instrument(level = "debug", skip_all)]
    #[async_backtrace::framed]
    pub async fn read_segments<T>(
        &self,
        segment_locations: &[Location],
        put_cache: bool,
    ) -> Result<Vec<Result<T>>>
    where
        T: From<SegmentInfo> + Send + 'static,
    {
        // combine all the tasks.
        let mut iter = segment_locations.iter();
        let tasks = std::iter::from_fn(|| {
            iter.next().map(|location| {
                let dal = self.operator.clone();
                let table_schema = self.schema.clone();
                let segment_location = location.clone();
                async move {
                    let segment =
                        Self::read_segment(dal, segment_location, table_schema, put_cache).await?;
                    Ok(segment.into())
                }
                .instrument(tracing::debug_span!("read_segments"))
            })
        });

        let threads_nums = self.ctx.get_settings().get_max_threads()? as usize;
        let permit_nums = self.ctx.get_settings().get_max_storage_io_requests()? as usize;
        execute_futures_in_parallel(
            tasks,
            threads_nums,
            permit_nums,
            "fuse-req-segments-worker".to_owned(),
        )
        .await
    }

    #[async_backtrace::framed]
    pub async fn write_segment(dal: Operator, serialized_segment: SerializedSegment) -> Result<()> {
        assert_eq!(
            serialized_segment.segment.format_version,
            SegmentInfo::VERSION
        );
        let raw_bytes = serialized_segment.segment.to_bytes()?;
        let compact_segment_info = CompactSegmentInfo::from_slice(&raw_bytes)?;
        dal.write(&serialized_segment.path, raw_bytes).await?;
        if let Some(segment_cache) = CacheManager::instance().get_table_segment_cache() {
            segment_cache.put(serialized_segment.path, Arc::new(compact_segment_info));
        }
        Ok(())
    }

    // TODO use batch_meta_writer
    #[async_backtrace::framed]
    pub async fn write_segments(&self, segments: Vec<SerializedSegment>) -> Result<()> {
        let mut iter = segments.into_iter();
        let tasks = std::iter::from_fn(move || {
            iter.next().map(|segment| {
                Self::write_segment(self.operator.clone(), segment)
                    .instrument(tracing::debug_span!("write_segment"))
            })
        });

        let threads_nums = self.ctx.get_settings().get_max_threads()? as usize;
        let permit_nums = self.ctx.get_settings().get_max_storage_io_requests()? as usize;
        execute_futures_in_parallel(
            tasks,
            threads_nums,
            permit_nums,
            "write-segments-worker".to_owned(),
        )
        .await?
        .into_iter()
        .collect::<Result<Vec<_>>>()?;
        Ok(())
    }
}
