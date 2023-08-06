// Copyright 2023 Datafuse Labs.
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

use std::collections::BTreeMap;
use std::collections::BTreeSet;

use chrono::TimeZone;
use chrono::Utc;
use common_meta_app::share;

use crate::common;

// These bytes are built when a new version in introduced,
// and are kept for backward compatibility test.
//
// *************************************************************
// * These messages should never be updated,                   *
// * only be added when a new version is added,                *
// * or be removed when an old version is no longer supported. *
// *************************************************************
//
// The message bytes are built from the output of `test_build_pb_buf()`
#[test]
fn test_decode_v2_share_meta() -> anyhow::Result<()> {
    let bytes: Vec<u8> = vec![
        10, 43, 10, 8, 8, 1, 160, 6, 2, 168, 6, 1, 16, 1, 26, 23, 50, 48, 49, 52, 45, 49, 49, 45,
        50, 56, 32, 49, 50, 58, 48, 48, 58, 48, 57, 32, 85, 84, 67, 160, 6, 2, 168, 6, 1, 18, 43,
        10, 8, 16, 19, 160, 6, 2, 168, 6, 1, 16, 4, 26, 23, 50, 48, 49, 52, 45, 49, 49, 45, 50, 56,
        32, 49, 50, 58, 48, 48, 58, 48, 57, 32, 85, 84, 67, 160, 6, 2, 168, 6, 1, 26, 1, 97, 26, 1,
        98, 34, 7, 99, 111, 109, 109, 101, 110, 116, 42, 23, 50, 48, 49, 52, 45, 49, 49, 45, 50,
        56, 32, 49, 50, 58, 48, 48, 58, 48, 57, 32, 85, 84, 67, 50, 23, 50, 48, 49, 52, 45, 49, 49,
        45, 50, 57, 32, 49, 50, 58, 48, 48, 58, 48, 57, 32, 85, 84, 67, 160, 6, 2, 168, 6, 1,
    ];

    let want = || {
        let now = Utc.with_ymd_and_hms(2014, 11, 28, 12, 0, 9).unwrap();

        let db_entry = share::ShareGrantEntry::new(
            share::ShareGrantObject::Database(1),
            share::ShareGrantObjectPrivilege::Usage,
            now,
        );
        let mut entries = BTreeMap::new();
        for entry in vec![share::ShareGrantEntry::new(
            share::ShareGrantObject::Table(19),
            share::ShareGrantObjectPrivilege::Select,
            now,
        )] {
            entries.insert(entry.to_string().clone(), entry);
        }

        share::ShareMeta {
            database: Some(db_entry),
            entries,
            accounts: BTreeSet::from_iter(vec![s("a"), s("b")].into_iter()),
            share_from_db_ids: BTreeSet::new(),
            comment: Some(s("comment")),
            share_on: Utc.with_ymd_and_hms(2014, 11, 28, 12, 0, 9).unwrap(),
            update_on: Some(Utc.with_ymd_and_hms(2014, 11, 29, 12, 0, 9).unwrap()),
        }
    };

    common::test_pb_from_to(func_name!(), want())?;
    common::test_load_old(func_name!(), bytes.as_slice(), 2, want())
}

fn s(ss: impl ToString) -> String {
    ss.to_string()
}
