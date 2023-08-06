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

use crate::Incompatible;

/// Describes metadata changes.
///
/// This is a list of every `VER` and the corresponding change it introduces.
///
/// ## For developers
///
/// Every time fields are added/removed into/from data types in this crate:
/// - Add a new line to this list to describe what changed.
/// - Add a test case to ensure protobuf message serialized by this version can be loaded,
///   similar to: test_user_stage_fs_v6() in tests/it/user_stage.rs;
///
/// `VER` is the current metadata version and is automatically set to the last version.
/// `MIN_READER_VER` is the oldest compatible version.
#[rustfmt::skip]
const META_CHANGE_LOG: &[(u64, &str)] = &[
    //
    ( 1, "----------: Initial"),
    ( 2, "2022-07-13: Add: share.proto"),
    ( 3, "2022-07-29: Add: user.proto/UserOption::default_role"),
    ( 4, "2022-08-22: Add: config.proto/GcsStorageConfig"),
    ( 5, "2022-08-25: Add: ShareMeta::share_from_db_ids; DatabaseMeta::from_share", ),
    ( 6, "2022-09-08: Add: users.proto/CopyOptions::purge"),
    ( 7, "2022-09-09: Add: table.proto/{TableCopiedFileInfo,TableCopiedFileLock} type", ),
    ( 8, "2022-09-16: Add: users.proto/StageFile::entity_tag"),
    ( 9, "2022-09-20: Add: config.proto/S3StorageConfig::security_token", ),
    (10, "2022-09-23: Add: table.proto/TableMeta::catalog"),
    (11, "2022-09-29: Add: users.proto/CopyOptions::single and CopyOptions::max_file_size", ),
    (12, "2022-09-29: Add: table.proto/TableMeta::storage_params"),
    (13, "2022-10-09: Add: config.proto/OssStorageConfig and user.proto/StageStorage::oss", ),
    (14, "2022-10-11: Add: role_arn and external_id in config.proto/OssStorageConfig, Remove role_arn and oidc_token from config.proto/OssStorageConfig", ),
    (15, "2022-10-12: Remove: precision in TimestampType"),
    (16, "2022-09-29: Add: CopyOptions::split_size"),
    (17, "2022-10-28: Add: StageType::LegacyInternal"),
    (18, "2022-10-28: Add: FILEFormatOptions::escape"),
    (19, "2022-10-31: Add: StageType::UserStage"),
    (20, "2022-11-02: Add: users.proto/FileFormatOptions::row_tag", ),
    (21, "2022-11-24: Add: users.proto/FileFormatOptions::nan_display", ),
    (22, "2022-12-13: Add: users.proto/FileFormatOptions::quote"),
    (23, "2022-12-28: Add: table.proto/TableMeta::part_prefix"),
    (24, "2023-01-07: Add: new-schema pb::DataType to/from TableDataType", ),
    (25, "2023-01-05: Add: user.proto/OnErrorMode::AbortNum"),
    (26, "2023-01-16: Add: metadata.proto/DataSchema::next_column_id", ),
    (27, "2023-02-10: Add: metadata.proto/DataType Decimal types"),
    (28, "2023-02-13: Add: user.proto/UserDefinedFileFormat"),
    (29, "2023-02-23: Add: metadata.proto/DataType EmptyMap types", ),
    (30, "2023-02-21: Add: config.proto/WebhdfsStorageConfig; Modify: user.proto/UserStageInfo::StageStorage", ),
    (31, "2023-02-21: Add: CopyOptions::max_files", ),
    (32, "2023-04-05: Add: file_format.proto/FileFormatParams", ),
    (33, "2023-04-13: Update: add `shared_by` field into TableMeta", ),
    (34, "2023-04-23: Add: metadata.proto/DataType Bitmap type", ),
    (35, "2023-05-08: Add: CopyOptions::disable_variant_check", ),
    // Dear developer:
    //      If you're gonna add a new metadata version, you'll have to add a test for it.
    //      You could just copy an existing test file(e.g., `../tests/it/v024_table_meta.rs`)
    //      and replace two of the variable `bytes` and `want`.
];

/// Attribute of both a reader and a message:
/// The version to write into a message and it is also the version of the message reader.
pub const VER: u64 = META_CHANGE_LOG.last().unwrap().0;

/// Attribute of a message:
/// The minimal reader version that can read message of version `VER`, i.e. `message.ver=VER`.
///
/// This is written to every message that needs to be serialized independently.
pub const MIN_READER_VER: u64 = 24;

/// Attribute of a reader:
/// The minimal message version(`message.ver`) that a reader can read.
pub const MIN_MSG_VER: u64 = 1;

pub fn reader_check_msg(msg_ver: u64, msg_min_reader_ver: u64) -> Result<(), Incompatible> {
    // The reader version must be big enough
    if VER < msg_min_reader_ver {
        return Err(Incompatible {
            reason: format!(
                "executable ver={} is smaller than the min reader version({}) that can read this message",
                VER, msg_min_reader_ver
            ),
        });
    }

    // The message version must be big enough
    if msg_ver < MIN_MSG_VER {
        return Err(Incompatible {
            reason: format!(
                "message ver={} is smaller than executable MIN_MSG_VER({}) that this program can read",
                msg_ver, MIN_MSG_VER
            ),
        });
    }
    Ok(())
}

pub fn missing(reason: impl ToString) -> impl FnOnce() -> Incompatible {
    let s = reason.to_string();
    move || Incompatible { reason: s }
}
