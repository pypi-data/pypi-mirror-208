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

use common_arrow::parquet::metadata::FileMetaData;
use common_arrow::parquet::read::read_metadata_async;
use common_exception::ErrorCode;
use common_exception::Result;
use opendal::Operator;
use storages_common_cache::InMemoryItemCacheReader;
use storages_common_cache::LoadParams;
use storages_common_cache::Loader;
use storages_common_cache_manager::CacheManager;

pub struct LoaderWrapper<T>(T);
pub type FileMetaDataReader = InMemoryItemCacheReader<FileMetaData, LoaderWrapper<Operator>>;
pub struct MetaDataReader;

impl MetaDataReader {
    pub fn meta_data_reader(dal: Operator) -> FileMetaDataReader {
        FileMetaDataReader::new(
            CacheManager::instance().get_file_meta_data_cache(),
            LoaderWrapper(dal),
        )
    }
}

#[async_trait::async_trait]
impl Loader<FileMetaData> for LoaderWrapper<Operator> {
    #[async_backtrace::framed]
    async fn load(&self, params: &LoadParams) -> Result<FileMetaData> {
        let mut reader = if let Some(len) = params.len_hint {
            self.0.range_reader(&params.location, 0..len).await?
        } else {
            self.0.reader(&params.location).await?
        };
        read_metadata_async(&mut reader).await.map_err(|err| {
            ErrorCode::Internal(format!(
                "read file meta failed, {}, {:?}",
                params.location, err
            ))
        })
    }
}
