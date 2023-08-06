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

use common_exception::ErrorCode;
use common_exception::Result;
use common_expression::ColumnId;
use storages_common_cache::CacheAccessor;
use storages_common_cache::TableDataCache;
use storages_common_cache::TableDataCacheKey;
use storages_common_cache_manager::SizedColumnArray;

pub struct OwnerMemory {
    chunks: HashMap<usize, Vec<u8>>,
}

impl OwnerMemory {
    pub fn create(chunks: Vec<(usize, Vec<u8>)>) -> OwnerMemory {
        let chunks = chunks.into_iter().collect::<HashMap<_, _>>();
        OwnerMemory { chunks }
    }

    pub fn get_chunk(&self, index: usize, path: &str) -> Result<&[u8]> {
        match self.chunks.get(&index) {
            Some(chunk) => Ok(chunk.as_slice()),
            None => Err(ErrorCode::Internal(format!(
                "It's a terrible bug, not found range data, merged_range_idx:{}, path:{}",
                index, path
            ))),
        }
    }
}

type CachedColumnData = Vec<(ColumnId, Arc<Vec<u8>>)>;
type CachedColumnArray = Vec<(ColumnId, Arc<SizedColumnArray>)>;
pub struct MergeIOReadResult {
    block_path: String,
    columns_chunk_offsets: HashMap<ColumnId, (usize, Range<usize>)>,
    owner_memory: OwnerMemory,
    pub cached_column_data: CachedColumnData,
    pub cached_column_array: CachedColumnArray,
    table_data_cache: Option<TableDataCache>,
}

pub enum DataItem<'a> {
    RawData(&'a [u8]),
    ColumnArray(&'a Arc<SizedColumnArray>),
}

impl MergeIOReadResult {
    pub fn create(
        owner_memory: OwnerMemory,
        capacity: usize,
        path: String,
        table_data_cache: Option<TableDataCache>,
    ) -> MergeIOReadResult {
        MergeIOReadResult {
            block_path: path,
            columns_chunk_offsets: HashMap::with_capacity(capacity),
            owner_memory,
            cached_column_data: vec![],
            cached_column_array: vec![],
            table_data_cache,
        }
    }

    pub fn columns_chunks(&self) -> Result<HashMap<ColumnId, DataItem>> {
        let mut res = HashMap::with_capacity(self.columns_chunk_offsets.len());

        // merge column data fetched from object storage
        for (column_id, (chunk_idx, range)) in &self.columns_chunk_offsets {
            let chunk = self.owner_memory.get_chunk(*chunk_idx, &self.block_path)?;
            res.insert(*column_id, DataItem::RawData(&chunk[range.clone()]));
        }

        // merge column data from cache
        for (column_id, data) in &self.cached_column_data {
            res.insert(*column_id, DataItem::RawData(data.as_slice()));
        }

        // merge column array from cache
        for (column_id, data) in &self.cached_column_array {
            res.insert(*column_id, DataItem::ColumnArray(data));
        }

        Ok(res)
    }

    fn get_chunk(&self, index: usize, path: &str) -> Result<&[u8]> {
        self.owner_memory.get_chunk(index, path)
    }

    pub fn add_column_chunk(
        &mut self,
        chunk_index: usize,
        column_id: ColumnId,
        range: Range<usize>,
    ) {
        if let Some(table_data_cache) = &self.table_data_cache {
            // populate raw column data cache (compressed raw bytes)
            if let Ok(chunk_data) = self.get_chunk(chunk_index, &self.block_path) {
                let cache_key = TableDataCacheKey::new(&self.block_path, column_id);
                let data = &chunk_data[range.clone()];
                table_data_cache.put(cache_key.as_ref().to_owned(), Arc::new(data.to_vec()));
            }
        }
        self.columns_chunk_offsets
            .insert(column_id, (chunk_index, range));
    }
}
