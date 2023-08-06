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

use common_arrow::arrow::datatypes::DataType;
use common_arrow::arrow::datatypes::Field as ArrowField;
use common_arrow::arrow::io::parquet::read::column_iter_to_arrays;
use common_arrow::parquet::compression::Compression;
use common_arrow::parquet::metadata::ColumnDescriptor;
use common_arrow::parquet::metadata::Descriptor;
use common_arrow::parquet::read::BasicDecompressor;
use common_arrow::parquet::read::PageMetaData;
use common_arrow::parquet::read::PageReader;
use common_arrow::parquet::schema::types::FieldInfo;
use common_arrow::parquet::schema::types::ParquetType;
use common_arrow::parquet::schema::types::PhysicalType;
use common_arrow::parquet::schema::types::PrimitiveType;
use common_arrow::parquet::schema::Repetition;
use common_exception::ErrorCode;
use common_exception::Result;
use common_expression::Column;
use common_expression::ColumnId;
use opendal::Operator;
use storages_common_cache::CacheKey;
use storages_common_cache::InMemoryItemCacheReader;
use storages_common_cache::LoadParams;
use storages_common_cache::Loader;
use storages_common_cache_manager::CachedObject;
use storages_common_index::filters::Filter;
use storages_common_index::filters::Xor8Filter;
use storages_common_table_meta::meta::SingleColumnMeta;

use crate::metrics::metrics_inc_block_index_read_bytes;

type CachedReader = InMemoryItemCacheReader<Xor8Filter, Xor8FilterLoader>;

/// Load the filter of a given bloom index column. Also
/// - generates the proper cache key
/// - takes cares of getting the correct cache instance from [CacheManager]
pub struct BloomColumnFilterReader {
    cached_reader: CachedReader,
    param: LoadParams,
}

impl BloomColumnFilterReader {
    pub fn new(
        index_path: String,
        column_id: ColumnId,
        column_name: String,
        column_chunk_meta: &SingleColumnMeta,
        operator: Operator,
    ) -> Self {
        let meta = column_chunk_meta;
        let cache_key = format!("{index_path}-{column_id}");

        // the schema of bloom filter block is fixed, as following
        let base_type = PrimitiveType {
            field_info: FieldInfo {
                name: column_name.clone(),
                repetition: Repetition::Required,
                id: None,
            },
            logical_type: None,
            converted_type: None,
            physical_type: PhysicalType::ByteArray,
        };

        let descriptor = Descriptor {
            primitive_type: base_type.clone(),
            max_def_level: 0,
            max_rep_level: 0,
        };

        let base_parquet_type = ParquetType::PrimitiveType(base_type);
        let loader = Xor8FilterLoader {
            offset: meta.offset,
            len: meta.len,
            cache_key,
            operator,
            column_descriptor: ColumnDescriptor::new(
                descriptor,
                vec![column_name],
                base_parquet_type,
            ),
        };

        let cached_reader = CachedReader::new(Xor8Filter::cache(), loader);

        let param = LoadParams {
            location: index_path,
            len_hint: None,
            ver: 0,
            put_cache: true,
        };

        BloomColumnFilterReader {
            cached_reader,
            param,
        }
    }

    #[async_backtrace::framed]
    pub async fn read(&self) -> Result<Arc<Xor8Filter>> {
        self.cached_reader.read(&self.param).await
    }
}

/// Loader that fetch range of the target object with customized cache key
pub struct Xor8FilterLoader {
    pub offset: u64,
    pub len: u64,
    pub cache_key: String,
    pub operator: Operator,
    pub column_descriptor: ColumnDescriptor,
}

#[async_trait::async_trait]
impl Loader<Xor8Filter> for Xor8FilterLoader {
    #[async_backtrace::framed]
    async fn load(&self, params: &LoadParams) -> Result<Xor8Filter> {
        let bytes = self
            .operator
            .range_read(&params.location, self.offset..self.offset + self.len)
            .await?;

        let page_meta_data = PageMetaData {
            column_start: 0,
            num_values: 1,
            compression: Compression::Uncompressed,
            descriptor: self.column_descriptor.descriptor.clone(),
        };

        let page_reader = PageReader::new_with_page_meta(
            std::io::Cursor::new(bytes),
            page_meta_data,
            Arc::new(|_, _| true),
            vec![],
            usize::MAX,
        );

        let decompressor = BasicDecompressor::new(page_reader, vec![]);
        let column_type = self.column_descriptor.descriptor.primitive_type.clone();
        let filed_name = self.column_descriptor.path_in_schema[0].to_owned();
        let field = ArrowField::new(filed_name, DataType::Binary, false);
        let mut array_iter =
            column_iter_to_arrays(vec![decompressor], vec![&column_type], field, None, 1)?;
        if let Some(array) = array_iter.next() {
            let array = array?;
            let col =
                Column::from_arrow(array.as_ref(), &common_expression::types::DataType::String);

            let filter_bytes = col
                .as_string()
                .map(|str| unsafe { str.index_unchecked(0) })
                .ok_or_else(|| {
                    // BloomPruner will log and handle this exception
                    ErrorCode::Internal(
                        "unexpected exception: load bloom filter raw data as string failed",
                    )
                })?;
            metrics_inc_block_index_read_bytes(filter_bytes.len() as u64);
            let (filter, _size) = Xor8Filter::from_bytes(filter_bytes)?;
            Ok(filter)
        } else {
            Err(ErrorCode::StorageOther(
                "bloom index data not available as expected",
            ))
        }
    }

    fn cache_key(&self, _params: &LoadParams) -> CacheKey {
        self.cache_key.clone()
    }
}
