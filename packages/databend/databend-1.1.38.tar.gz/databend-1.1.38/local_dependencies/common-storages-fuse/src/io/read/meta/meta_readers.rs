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

use std::io::SeekFrom;

use common_arrow::parquet::metadata::ThriftFileMetaData;
use common_cache::DefaultHashBuilder;
use common_exception::ErrorCode;
use common_exception::Result;
use common_expression::TableSchemaRef;
use futures::AsyncRead;
use futures::AsyncSeek;
use futures_util::AsyncReadExt;
use futures_util::AsyncSeekExt;
use opendal::Operator;
use opendal::Reader;
use storages_common_cache::InMemoryItemCacheReader;
use storages_common_cache::LoadParams;
use storages_common_cache::Loader;
use storages_common_cache_manager::CacheManager;
use storages_common_cache_manager::CompactSegmentInfoMeter;
use storages_common_index::BloomIndexMeta;
use storages_common_table_meta::meta::CompactSegmentInfo;
use storages_common_table_meta::meta::SegmentInfoVersion;
use storages_common_table_meta::meta::SnapshotVersion;
use storages_common_table_meta::meta::TableSnapshot;
use storages_common_table_meta::meta::TableSnapshotStatistics;
use storages_common_table_meta::meta::TableSnapshotStatisticsVersion;

use super::versioned_reader::VersionedReader;
use crate::io::read::meta::meta_readers::thrift_file_meta_read::read_thrift_file_metadata;

pub type TableSnapshotStatisticsReader =
    InMemoryItemCacheReader<TableSnapshotStatistics, LoaderWrapper<Operator>>;
pub type BloomIndexMetaReader = InMemoryItemCacheReader<BloomIndexMeta, LoaderWrapper<Operator>>;
pub type TableSnapshotReader = InMemoryItemCacheReader<TableSnapshot, LoaderWrapper<Operator>>;
pub type CompactSegmentInfoReader = InMemoryItemCacheReader<
    CompactSegmentInfo,
    LoaderWrapper<(Operator, TableSchemaRef)>,
    DefaultHashBuilder,
    CompactSegmentInfoMeter,
>;

pub struct MetaReaders;

impl MetaReaders {
    pub fn segment_info_reader(dal: Operator, schema: TableSchemaRef) -> CompactSegmentInfoReader {
        CompactSegmentInfoReader::new(
            CacheManager::instance().get_table_segment_cache(),
            LoaderWrapper((dal, schema)),
        )
    }

    pub fn table_snapshot_reader(dal: Operator) -> TableSnapshotReader {
        TableSnapshotReader::new(
            CacheManager::instance().get_table_snapshot_cache(),
            LoaderWrapper(dal),
        )
    }

    pub fn table_snapshot_statistics_reader(dal: Operator) -> TableSnapshotStatisticsReader {
        TableSnapshotStatisticsReader::new(
            CacheManager::instance().get_table_snapshot_statistics_cache(),
            LoaderWrapper(dal),
        )
    }

    pub fn bloom_index_meta_reader(dal: Operator) -> BloomIndexMetaReader {
        BloomIndexMetaReader::new(
            CacheManager::instance().get_bloom_index_meta_cache(),
            LoaderWrapper(dal),
        )
    }
}

// workaround for the orphan rules
// Loader and types of table meta data are all defined outside (of this crate)
pub struct LoaderWrapper<T>(T);

#[async_trait::async_trait]
impl Loader<TableSnapshot> for LoaderWrapper<Operator> {
    #[async_backtrace::framed]
    async fn load(&self, params: &LoadParams) -> Result<TableSnapshot> {
        let reader = bytes_reader(&self.0, params.location.as_str(), params.len_hint).await?;
        let version = SnapshotVersion::try_from(params.ver)?;
        version.read(reader).await
    }
}

#[async_trait::async_trait]
impl Loader<TableSnapshotStatistics> for LoaderWrapper<Operator> {
    #[async_backtrace::framed]
    async fn load(&self, params: &LoadParams) -> Result<TableSnapshotStatistics> {
        let version = TableSnapshotStatisticsVersion::try_from(params.ver)?;
        let reader = bytes_reader(&self.0, params.location.as_str(), params.len_hint).await?;
        version.read(reader).await
    }
}

#[async_trait::async_trait]
impl Loader<CompactSegmentInfo> for LoaderWrapper<(Operator, TableSchemaRef)> {
    #[async_backtrace::framed]
    async fn load(&self, params: &LoadParams) -> Result<CompactSegmentInfo> {
        let version = SegmentInfoVersion::try_from(params.ver)?;
        let LoaderWrapper((operator, schema)) = &self;
        let reader = bytes_reader(operator, params.location.as_str(), params.len_hint).await?;
        (version, schema.clone()).read(reader).await
    }
}

#[async_trait::async_trait]
impl Loader<BloomIndexMeta> for LoaderWrapper<Operator> {
    #[async_backtrace::framed]
    async fn load(&self, params: &LoadParams) -> Result<BloomIndexMeta> {
        let mut reader = bytes_reader(&self.0, params.location.as_str(), params.len_hint).await?;
        // read the ThriftFileMetaData, omit unnecessary conversions
        let meta = read_thrift_file_metadata(&mut reader)
            .await
            .map_err(|err| {
                ErrorCode::StorageOther(format!(
                    "read file meta failed, {}, {:?}",
                    params.location, err
                ))
            })?;

        BloomIndexMeta::try_from(meta)
    }
}

async fn bytes_reader(op: &Operator, path: &str, len_hint: Option<u64>) -> Result<Reader> {
    let reader = if let Some(len) = len_hint {
        op.range_reader(path, 0..len).await?
    } else {
        op.reader(path).await?
    };
    Ok(reader)
}

mod thrift_file_meta_read {
    use common_arrow::parquet::error::Error;
    use parquet_format_safe::thrift::protocol::TCompactInputProtocol;

    use super::*;

    // the following code is copied from crate `parquet2`, with slight modification:
    // return a ThriftFileMetaData instead of FileMetaData while reading parquet metadata,
    // to avoid unnecessary conversions.

    const HEADER_SIZE: u64 = PARQUET_MAGIC.len() as u64;
    const FOOTER_SIZE: u64 = 8;
    const PARQUET_MAGIC: [u8; 4] = [b'P', b'A', b'R', b'1'];

    /// The number of bytes read at the end of the parquet file on first read
    const DEFAULT_FOOTER_READ_SIZE: u64 = 64 * 1024;

    #[async_backtrace::framed]
    async fn stream_len(
        seek: &mut (impl AsyncSeek + std::marker::Unpin),
    ) -> std::result::Result<u64, std::io::Error> {
        let old_pos = seek.seek(SeekFrom::Current(0)).await?;
        let len = seek.seek(SeekFrom::End(0)).await?;

        // Avoid seeking a third time when we were already at the end of the
        // stream. The branch is usually way cheaper than a seek operation.
        if old_pos != len {
            seek.seek(SeekFrom::Start(old_pos)).await?;
        }

        Ok(len)
    }

    fn metadata_len(buffer: &[u8], len: usize) -> i32 {
        i32::from_le_bytes(buffer[len - 8..len - 4].try_into().unwrap())
    }

    #[async_backtrace::framed]
    pub async fn read_thrift_file_metadata<R: AsyncRead + AsyncSeek + Send + std::marker::Unpin>(
        reader: &mut R,
    ) -> common_arrow::parquet::error::Result<ThriftFileMetaData> {
        let file_size = stream_len(reader).await?;

        if file_size < HEADER_SIZE + FOOTER_SIZE {
            return Err(Error::OutOfSpec(
                "A parquet file must contain a header and footer with at least 12 bytes".into(),
            ));
        }

        // read and cache up to DEFAULT_FOOTER_READ_SIZE bytes from the end and process the footer
        let default_end_len = std::cmp::min(DEFAULT_FOOTER_READ_SIZE, file_size) as usize;
        reader
            .seek(SeekFrom::End(-(default_end_len as i64)))
            .await?;

        let mut buffer = vec![];
        buffer.try_reserve(default_end_len)?;
        reader
            .take(default_end_len as u64)
            .read_to_end(&mut buffer)
            .await?;

        // check this is indeed a parquet file
        if buffer[default_end_len - 4..] != PARQUET_MAGIC {
            return Err(Error::OutOfSpec(
                "Invalid Parquet file. Corrupt footer".into(),
            ));
        }

        let metadata_len = metadata_len(&buffer, default_end_len);
        let metadata_len: u64 = metadata_len.try_into()?;

        let footer_len = FOOTER_SIZE + metadata_len;
        if footer_len > file_size {
            return Err(Error::OutOfSpec(
                "The footer size must be smaller or equal to the file's size".into(),
            ));
        }

        let reader = if (footer_len as usize) < buffer.len() {
            // the whole metadata is in the bytes we already read
            let remaining = buffer.len() - footer_len as usize;
            &buffer[remaining..]
        } else {
            // the end of file read by default is not long enough, read again including the metadata.
            reader.seek(SeekFrom::End(-(footer_len as i64))).await?;

            buffer.clear();
            buffer.try_reserve(footer_len as usize)?;
            reader.take(footer_len).read_to_end(&mut buffer).await?;

            &buffer
        };

        // a highly nested but sparse struct could result in many allocations
        let max_size = reader.len() * 2 + 1024;

        let mut prot = TCompactInputProtocol::new(reader, max_size);
        let meta = ThriftFileMetaData::read_from_in_protocol(&mut prot)?;
        Ok(meta)
    }
}
