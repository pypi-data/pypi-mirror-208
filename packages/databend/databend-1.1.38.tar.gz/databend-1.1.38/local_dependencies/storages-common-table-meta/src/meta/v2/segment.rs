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

use std::collections::HashMap;
use std::ops::Range;
use std::sync::Arc;

use common_arrow::native::ColumnMeta as NativeColumnMeta;
use common_expression::ColumnId;
use common_expression::TableField;
use enum_as_inner::EnumAsInner;
use serde::Deserialize;
use serde::Serialize;

use crate::meta::statistics::ClusterStatistics;
use crate::meta::statistics::ColumnStatistics;
use crate::meta::statistics::FormatVersion;
use crate::meta::v0;
use crate::meta::v1;
use crate::meta::Compression;
use crate::meta::Location;
use crate::meta::Statistics;
use crate::meta::Versioned;

/// A segment comprises one or more blocks
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq)]
pub struct SegmentInfo {
    /// format version
    pub format_version: FormatVersion,
    /// blocks belong to this segment
    pub blocks: Vec<Arc<BlockMeta>>,
    /// summary statistics
    pub summary: Statistics,
}

impl SegmentInfo {
    // for test.
    pub fn new(blocks: Vec<Arc<BlockMeta>>, summary: Statistics) -> Self {
        Self {
            format_version: SegmentInfo::VERSION,
            blocks,
            summary,
        }
    }
}

/// Meta information of a block
/// Part of and kept inside the [SegmentInfo]
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq)]
pub struct BlockMeta {
    pub row_count: u64,
    pub block_size: u64,
    pub file_size: u64,
    pub col_stats: HashMap<ColumnId, ColumnStatistics>,
    pub col_metas: HashMap<ColumnId, ColumnMeta>,
    pub cluster_stats: Option<ClusterStatistics>,
    /// location of data block
    pub location: Location,
    /// location of bloom filter index
    pub bloom_filter_index_location: Option<Location>,

    #[serde(default)]
    pub bloom_filter_index_size: u64,
    pub compression: Compression,
}

impl BlockMeta {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        row_count: u64,
        block_size: u64,
        file_size: u64,
        col_stats: HashMap<ColumnId, ColumnStatistics>,
        col_metas: HashMap<ColumnId, ColumnMeta>,
        cluster_stats: Option<ClusterStatistics>,
        location: Location,
        bloom_filter_index_location: Option<Location>,
        bloom_filter_index_size: u64,
        compression: Compression,
    ) -> Self {
        Self {
            row_count,
            block_size,
            file_size,
            col_stats,
            col_metas,
            cluster_stats,
            location,
            bloom_filter_index_location,
            bloom_filter_index_size,
            compression,
        }
    }

    pub fn compression(&self) -> Compression {
        self.compression
    }

    /// Get the page size of the block.
    /// - If the format is parquet, its page size is its row count.
    /// - If the format is native, its page size is the row count of each page.
    /// (The row count of the last page may be smaller than the page size)
    pub fn page_size(&self) -> u64 {
        if let Some((_, ColumnMeta::Native(meta))) = self.col_metas.iter().next() {
            meta.pages.first().unwrap().num_values
        } else {
            self.row_count
        }
    }
}

impl SegmentInfo {
    pub fn from_v0(s: v0::SegmentInfo, fields: &[TableField]) -> Self {
        let summary = Statistics::from_v0(s.summary, fields);
        Self {
            // the is no version before v0, and no versions other then 0 can be converted into v0
            format_version: v0::SegmentInfo::VERSION,
            blocks: s
                .blocks
                .into_iter()
                .map(|b| Arc::new(BlockMeta::from_v0(&b, fields)))
                .collect::<_>(),
            summary,
        }
    }

    pub fn from_v1(s: v1::SegmentInfo, fields: &[TableField]) -> Self {
        let summary = Statistics::from_v0(s.summary, fields);
        Self {
            // NOTE: it is important to let the format_version return from here
            // carries the format_version of segment info being converted.
            format_version: s.format_version,
            blocks: s
                .blocks
                .into_iter()
                .map(|b| Arc::new(BlockMeta::from_v1(b.as_ref(), fields)))
                .collect::<_>(),
            summary,
        }
    }
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug, Eq, PartialEq, EnumAsInner)]
pub enum ColumnMeta {
    Parquet(v0::ColumnMeta),
    Native(NativeColumnMeta),
}

impl ColumnMeta {
    pub fn total_rows(&self) -> usize {
        match self {
            ColumnMeta::Parquet(v) => v.num_values as usize,
            ColumnMeta::Native(v) => v.pages.iter().map(|page| page.num_values as usize).sum(),
        }
    }

    pub fn offset_length(&self) -> (u64, u64) {
        match self {
            ColumnMeta::Parquet(v) => (v.offset, v.len),
            ColumnMeta::Native(v) => (v.offset, v.pages.iter().map(|page| page.length).sum()),
        }
    }

    pub fn read_rows(&self, range: Option<&Range<usize>>) -> u64 {
        match self {
            ColumnMeta::Parquet(v) => v.num_values,
            ColumnMeta::Native(v) => match range {
                Some(range) => v
                    .pages
                    .iter()
                    .skip(range.start)
                    .take(range.end - range.start)
                    .map(|page| page.num_values)
                    .sum(),
                None => v.pages.iter().map(|page| page.num_values).sum(),
            },
        }
    }

    pub fn read_bytes(&self, range: &Option<Range<usize>>) -> u64 {
        match self {
            ColumnMeta::Parquet(v) => v.len,
            ColumnMeta::Native(v) => match range {
                Some(range) => v
                    .pages
                    .iter()
                    .skip(range.start)
                    .take(range.end - range.start)
                    .map(|page| page.length)
                    .sum(),
                None => v.pages.iter().map(|page| page.length).sum(),
            },
        }
    }
}

impl BlockMeta {
    pub fn from_v0(s: &v0::BlockMeta, fields: &[TableField]) -> Self {
        let col_stats = s
            .col_stats
            .iter()
            .map(|(k, v)| {
                let data_type = fields[*k as usize].data_type();
                (*k, ColumnStatistics::from_v0(v, data_type))
            })
            .collect();

        let col_metas = s
            .col_metas
            .iter()
            .map(|(k, v)| (*k, ColumnMeta::Parquet(v.clone())))
            .collect();

        Self {
            row_count: s.row_count,
            block_size: s.block_size,
            file_size: s.file_size,
            col_stats,
            col_metas,
            cluster_stats: None,
            location: (s.location.path.clone(), 0),
            bloom_filter_index_location: None,
            bloom_filter_index_size: 0,
            compression: Compression::Lz4,
        }
    }

    pub fn from_v1(s: &v1::BlockMeta, fields: &[TableField]) -> Self {
        let col_stats = s
            .col_stats
            .iter()
            .map(|(k, v)| {
                let data_type = fields[*k as usize].data_type();
                (*k, ColumnStatistics::from_v0(v, data_type))
            })
            .collect();

        let col_metas = s
            .col_metas
            .iter()
            .map(|(k, v)| (*k, ColumnMeta::Parquet(v.clone())))
            .collect();

        Self {
            row_count: s.row_count,
            block_size: s.block_size,
            file_size: s.file_size,
            col_stats,
            col_metas,
            cluster_stats: None,
            location: s.location.clone(),
            bloom_filter_index_location: s.bloom_filter_index_location.clone(),
            bloom_filter_index_size: s.bloom_filter_index_size,
            compression: s.compression,
        }
    }
}
