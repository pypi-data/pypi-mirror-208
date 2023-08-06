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

use std::collections::HashSet;

use once_cell::sync::Lazy;
pub const OPT_KEY_DATABASE_ID: &str = "database_id";
pub const OPT_KEY_SNAPSHOT_LOCATION: &str = "snapshot_location";
pub const OPT_KEY_STORAGE_FORMAT: &str = "storage_format";
pub const OPT_KEY_TABLE_COMPRESSION: &str = "compression";
pub const OPT_KEY_COMMENT: &str = "comment";
pub const OPT_KEY_EXTERNAL_LOCATION: &str = "external_location";
pub const OPT_KEY_ENGINE: &str = "engine";

/// Legacy table snapshot location key
///
/// # Deprecated
///
/// For backward compatibility, this option key can still be recognized,
/// but use can no longer use this key in DDLs
///
/// If both OPT_KEY_SNAPSHOT_LOC and OPT_KEY_SNAPSHOT_LOCATION exist, the latter will be used
pub const OPT_KEY_LEGACY_SNAPSHOT_LOC: &str = "snapshot_loc";

/// Table option keys that reserved for internal usage only
/// - Users are not allowed to specified this option keys in DDL
/// - Should not be shown in `show create table` statement
pub static RESERVED_TABLE_OPTION_KEYS: Lazy<HashSet<&'static str>> = Lazy::new(|| {
    let mut r = HashSet::new();
    r.insert(OPT_KEY_DATABASE_ID);
    r.insert(OPT_KEY_LEGACY_SNAPSHOT_LOC);
    r
});

/// Table option keys that Should not be shown in `show create table` statement
pub static INTERNAL_TABLE_OPTION_KEYS: Lazy<HashSet<&'static str>> = Lazy::new(|| {
    let mut r = HashSet::new();
    r.insert(OPT_KEY_LEGACY_SNAPSHOT_LOC);
    r.insert(OPT_KEY_DATABASE_ID);
    r
});

pub fn is_reserved_opt_key<S: AsRef<str>>(opt_key: S) -> bool {
    RESERVED_TABLE_OPTION_KEYS.contains(opt_key.as_ref().to_lowercase().as_str())
}

pub fn is_internal_opt_key<S: AsRef<str>>(opt_key: S) -> bool {
    INTERNAL_TABLE_OPTION_KEYS.contains(opt_key.as_ref().to_lowercase().as_str())
}
