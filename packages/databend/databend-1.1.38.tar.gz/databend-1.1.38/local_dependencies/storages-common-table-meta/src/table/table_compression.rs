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

use common_arrow::native;
use common_arrow::parquet;
use common_exception::ErrorCode;

use crate::meta;

#[derive(Clone, Copy, Debug, Default)]
pub enum TableCompression {
    None,
    LZ4,
    Snappy,
    #[default]
    Zstd,
}

/// Convert from str.
impl TryFrom<&str> for TableCompression {
    type Error = ErrorCode;

    fn try_from(value: &str) -> Result<Self, Self::Error> {
        match value.to_lowercase().as_str() {
            "" => Ok(TableCompression::default()),
            "none" => Ok(TableCompression::None),
            "zstd" => Ok(TableCompression::Zstd),
            "lz4" => Ok(TableCompression::LZ4),
            "snappy" => Ok(TableCompression::Snappy),
            other => Err(ErrorCode::UnknownFormat(format!(
                "unsupported table compression: {}",
                other
            ))),
        }
    }
}

/// Convert to parquet CompressionOptions.
impl From<TableCompression> for parquet::compression::CompressionOptions {
    fn from(value: TableCompression) -> Self {
        match value {
            TableCompression::None => parquet::compression::CompressionOptions::Uncompressed,
            TableCompression::LZ4 => parquet::compression::CompressionOptions::Lz4Raw,
            TableCompression::Snappy => parquet::compression::CompressionOptions::Snappy,
            TableCompression::Zstd => parquet::compression::CompressionOptions::Zstd(None),
        }
    }
}

/// Convert to native Compression.
impl From<TableCompression> for native::Compression {
    fn from(value: TableCompression) -> Self {
        match value {
            TableCompression::None => native::Compression::None,
            TableCompression::LZ4 => native::Compression::LZ4,
            TableCompression::Snappy => native::Compression::SNAPPY,
            TableCompression::Zstd => native::Compression::ZSTD,
        }
    }
}

/// Convert to meta Compression.
impl From<TableCompression> for meta::Compression {
    fn from(value: TableCompression) -> Self {
        match value {
            TableCompression::None => meta::Compression::None,
            // Map to meta Lz4Raw.
            TableCompression::LZ4 => meta::Compression::Lz4Raw,
            TableCompression::Snappy => meta::Compression::Snappy,
            TableCompression::Zstd => meta::Compression::Zstd,
        }
    }
}
