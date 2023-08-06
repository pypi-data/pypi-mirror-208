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

use common_arrow::parquet::metadata::ThriftFileMetaData;
use common_exception::Result;
use common_expression::DataBlock;
use common_expression::FunctionContext;
use common_expression::TableSchemaRef;
use common_io::constants::DEFAULT_BLOCK_BUFFER_SIZE;
use common_io::constants::DEFAULT_BLOCK_INDEX_BUFFER_SIZE;
use common_storages_fuse::io::serialize_block;
use common_storages_fuse::io::TableMetaLocationGenerator;
use common_storages_fuse::io::WriteSettings;
use common_storages_fuse::FuseStorageFormat;
use opendal::Operator;
use storages_common_blocks::blocks_to_parquet;
use storages_common_index::BloomIndex;
use storages_common_table_meta::meta::BlockMeta;
use storages_common_table_meta::meta::ClusterStatistics;
use storages_common_table_meta::meta::Compression;
use storages_common_table_meta::meta::Location;
use storages_common_table_meta::meta::StatisticsOfColumns;
use storages_common_table_meta::table::TableCompression;
use uuid::Uuid;

pub struct BlockWriter<'a> {
    location_generator: &'a TableMetaLocationGenerator,
    data_accessor: &'a Operator,
}

impl<'a> BlockWriter<'a> {
    pub fn new(
        data_accessor: &'a Operator,
        location_generator: &'a TableMetaLocationGenerator,
    ) -> Self {
        Self {
            location_generator,
            data_accessor,
        }
    }

    pub async fn write(
        &self,
        storage_format: FuseStorageFormat,
        schema: &TableSchemaRef,
        block: DataBlock,
        col_stats: StatisticsOfColumns,
        cluster_stats: Option<ClusterStatistics>,
    ) -> Result<(BlockMeta, Option<ThriftFileMetaData>)> {
        let (location, block_id) = self.location_generator.gen_block_location();

        let data_accessor = &self.data_accessor;
        let row_count = block.num_rows() as u64;
        let block_size = block.memory_size() as u64;
        let (bloom_filter_index_size, bloom_filter_index_location, meta) = self
            .build_block_index(data_accessor, schema.clone(), &block, block_id)
            .await?;

        let write_settings = WriteSettings {
            storage_format,
            ..Default::default()
        };

        let mut buf = Vec::with_capacity(DEFAULT_BLOCK_BUFFER_SIZE);
        let (file_size, col_metas) = serialize_block(&write_settings, schema, block, &mut buf)?;

        data_accessor.write(&location.0, buf).await?;

        let block_meta = BlockMeta::new(
            row_count,
            block_size,
            file_size,
            col_stats,
            col_metas,
            cluster_stats,
            location,
            bloom_filter_index_location,
            bloom_filter_index_size,
            Compression::Lz4Raw,
        );
        Ok((block_meta, meta))
    }

    pub async fn build_block_index(
        &self,
        data_accessor: &Operator,
        schema: TableSchemaRef,
        block: &DataBlock,
        block_id: Uuid,
    ) -> Result<(u64, Option<Location>, Option<ThriftFileMetaData>)> {
        let location = self
            .location_generator
            .block_bloom_index_location(&block_id);

        let maybe_bloom_index =
            BloomIndex::try_create(FunctionContext::default(), schema, location.1, &[block])?;
        if let Some(bloom_index) = maybe_bloom_index {
            let index_block = bloom_index.serialize_to_data_block()?;
            let filter_schema = bloom_index.filter_schema;
            let mut data = Vec::with_capacity(DEFAULT_BLOCK_INDEX_BUFFER_SIZE);
            let index_block_schema = &filter_schema;
            let (size, meta) = blocks_to_parquet(
                index_block_schema,
                vec![index_block],
                &mut data,
                TableCompression::None,
            )?;
            data_accessor.write(&location.0, data).await?;
            Ok((size, Some(location), Some(meta)))
        } else {
            Ok((0u64, None, None))
        }
    }
}
