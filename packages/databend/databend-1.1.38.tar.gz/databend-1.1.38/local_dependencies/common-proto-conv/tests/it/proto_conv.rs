// Copyright 2021 Datafuse Labs.
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
use std::sync::Arc;

use ce::types::decimal::DecimalSize;
use ce::types::DecimalDataType;
use ce::types::NumberDataType;
use chrono::TimeZone;
use chrono::Utc;
use common_expression as ce;
use common_expression::TableDataType;
use common_expression::TableField;
use common_expression::TableSchema;
use common_meta_app::schema as mt;
use common_meta_app::share;
use common_proto_conv::FromToProto;
use common_proto_conv::Incompatible;
use common_proto_conv::VER;
use maplit::btreemap;
use maplit::btreeset;
use pretty_assertions::assert_eq;

fn s(ss: impl ToString) -> String {
    ss.to_string()
}

fn new_db_meta_share() -> mt::DatabaseMeta {
    mt::DatabaseMeta {
        engine: "44".to_string(),
        engine_options: btreemap! {s("abc") => s("def")},
        options: btreemap! {s("xyz") => s("foo")},
        created_on: Utc.with_ymd_and_hms(2014, 11, 28, 12, 0, 9).unwrap(),
        updated_on: Utc.with_ymd_and_hms(2014, 11, 29, 12, 0, 9).unwrap(),
        comment: "foo bar".to_string(),
        drop_on: None,
        shared_by: BTreeSet::new(),
        from_share: Some(share::ShareNameIdent {
            tenant: "tenant".to_string(),
            share_name: "share".to_string(),
        }),
    }
}

fn new_db_meta() -> mt::DatabaseMeta {
    mt::DatabaseMeta {
        engine: "44".to_string(),
        engine_options: btreemap! {s("abc") => s("def")},
        options: btreemap! {s("xyz") => s("foo")},
        created_on: Utc.with_ymd_and_hms(2014, 11, 28, 12, 0, 9).unwrap(),
        updated_on: Utc.with_ymd_and_hms(2014, 11, 29, 12, 0, 9).unwrap(),
        comment: "foo bar".to_string(),
        drop_on: None,
        shared_by: BTreeSet::from_iter(vec![1].into_iter()),
        from_share: None,
    }
}

fn new_share_meta_share_from_db_ids() -> share::ShareMeta {
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
        share_from_db_ids: BTreeSet::from_iter(vec![1, 2].into_iter()),
        comment: Some(s("comment")),
        share_on: Utc.with_ymd_and_hms(2014, 11, 28, 12, 0, 9).unwrap(),
        update_on: Some(Utc.with_ymd_and_hms(2014, 11, 29, 12, 0, 9).unwrap()),
    }
}

fn new_share_meta() -> share::ShareMeta {
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
}

fn new_share_account_meta() -> share::ShareAccountMeta {
    share::ShareAccountMeta {
        account: s("account"),
        share_id: 4,
        share_on: Utc.with_ymd_and_hms(2014, 11, 28, 12, 0, 9).unwrap(),
        accept_on: Some(Utc.with_ymd_and_hms(2014, 11, 29, 12, 0, 9).unwrap()),
    }
}

fn new_table_meta() -> mt::TableMeta {
    mt::TableMeta {
        schema: Arc::new(ce::TableSchema::new_from(
            vec![
                ce::TableField::new(
                    "nullable",
                    ce::TableDataType::Nullable(Box::new(ce::TableDataType::Number(
                        NumberDataType::Int8,
                    ))),
                )
                .with_default_expr(Some("a + 3".to_string())),
                ce::TableField::new("bool", ce::TableDataType::Boolean),
                ce::TableField::new("int8", ce::TableDataType::Number(NumberDataType::Int8)),
                ce::TableField::new("int16", ce::TableDataType::Number(NumberDataType::Int16)),
                ce::TableField::new("int32", ce::TableDataType::Number(NumberDataType::Int32)),
                ce::TableField::new("int64", ce::TableDataType::Number(NumberDataType::Int64)),
                ce::TableField::new("uint8", ce::TableDataType::Number(NumberDataType::UInt8)),
                ce::TableField::new("uint16", ce::TableDataType::Number(NumberDataType::UInt16)),
                ce::TableField::new("uint32", ce::TableDataType::Number(NumberDataType::UInt32)),
                ce::TableField::new("uint64", ce::TableDataType::Number(NumberDataType::UInt64)),
                ce::TableField::new(
                    "float32",
                    ce::TableDataType::Number(NumberDataType::Float32),
                ),
                ce::TableField::new(
                    "float64",
                    ce::TableDataType::Number(NumberDataType::Float64),
                ),
                ce::TableField::new("date", ce::TableDataType::Date),
                ce::TableField::new("timestamp", ce::TableDataType::Timestamp),
                ce::TableField::new("string", ce::TableDataType::String),
                ce::TableField::new("struct", ce::TableDataType::Tuple {
                    fields_name: vec![s("foo"), s("bar")],
                    fields_type: vec![ce::TableDataType::Boolean, ce::TableDataType::String],
                }),
                ce::TableField::new(
                    "array",
                    ce::TableDataType::Array(Box::new(ce::TableDataType::Boolean)),
                ),
                ce::TableField::new("variant", ce::TableDataType::Variant),
                ce::TableField::new("variant_array", ce::TableDataType::Variant),
                ce::TableField::new("variant_object", ce::TableDataType::Variant),
                // NOTE: It is safe to convert Interval to NULL, because `Interval` is never really used.
                ce::TableField::new("interval", ce::TableDataType::Null),
            ],
            btreemap! {s("a") => s("b")},
        )),
        catalog: "default".to_string(),
        engine: "44".to_string(),
        storage_params: None,
        part_prefix: "".to_string(),
        engine_options: btreemap! {s("abc") => s("def")},
        options: btreemap! {s("xyz") => s("foo")},
        default_cluster_key: Some("(a + 2, b)".to_string()),
        cluster_keys: vec!["(a + 2, b)".to_string()],
        default_cluster_key_id: Some(0),
        created_on: Utc.with_ymd_and_hms(2014, 11, 28, 12, 0, 9).unwrap(),
        updated_on: Utc.with_ymd_and_hms(2014, 11, 29, 12, 0, 10).unwrap(),
        comment: s("table_comment"),
        field_comments: vec!["c".to_string(); 21],
        drop_on: None,
        statistics: Default::default(),
        shared_by: btreeset! {1},
    }
}

pub(crate) fn new_latest_schema() -> TableSchema {
    let b1 = TableDataType::Tuple {
        fields_name: vec!["b11".to_string(), "b12".to_string()],
        fields_type: vec![TableDataType::Boolean, TableDataType::String],
    };
    let b = TableDataType::Tuple {
        fields_name: vec!["b1".to_string(), "b2".to_string()],
        fields_type: vec![b1, TableDataType::Number(NumberDataType::Int64)],
    };
    let fields = vec![
        TableField::new("a", TableDataType::Number(NumberDataType::UInt64)),
        TableField::new("b", b),
        TableField::new("c", TableDataType::Number(NumberDataType::UInt64)),
        TableField::new(
            "decimal128",
            TableDataType::Decimal(DecimalDataType::Decimal128(DecimalSize {
                precision: 18,
                scale: 3,
            })),
        ),
        TableField::new(
            "decimal256",
            TableDataType::Decimal(DecimalDataType::Decimal256(DecimalSize {
                precision: 46,
                scale: 6,
            })),
        ),
        TableField::new("empty_map", TableDataType::EmptyMap),
        TableField::new("bitmap", TableDataType::Bitmap),
    ];
    TableSchema::new(fields)
}

pub(crate) fn new_table_copied_file_info_v6() -> mt::TableCopiedFileInfo {
    mt::TableCopiedFileInfo {
        etag: Some("etag".to_string()),
        content_length: 1024,
        last_modified: Some(Utc.with_ymd_and_hms(2014, 11, 29, 12, 0, 9).unwrap()),
    }
}

pub(crate) fn new_table_copied_file_lock_v7() -> mt::TableCopiedFileLock {
    mt::TableCopiedFileLock {}
}

#[test]
fn test_pb_from_to() -> anyhow::Result<()> {
    let db = new_db_meta();
    let p = db.to_pb()?;
    let got = mt::DatabaseMeta::from_pb(p)?;
    assert_eq!(db, got);

    let tbl = new_table_meta();
    let p = tbl.to_pb()?;
    let got = mt::TableMeta::from_pb(p)?;
    assert_eq!(tbl, got);

    let share = new_share_meta();
    let p = share.to_pb()?;
    let got = share::ShareMeta::from_pb(p)?;
    assert_eq!(share, got);

    let share_account_meta = new_share_account_meta();
    let p = share_account_meta.to_pb()?;
    let got = share::ShareAccountMeta::from_pb(p)?;
    assert_eq!(share_account_meta, got);
    Ok(())
}

#[test]
fn test_incompatible() -> anyhow::Result<()> {
    let db_meta = new_db_meta();
    let mut p = db_meta.to_pb()?;
    p.ver = VER + 1;
    p.min_reader_ver = VER + 1;

    let res = mt::DatabaseMeta::from_pb(p);
    assert_eq!(
        Incompatible {
            reason: format!(
                "executable ver={} is smaller than the min reader version({}) that can read this message",
                VER,
                VER + 1
            )
        },
        res.unwrap_err()
    );

    let db_meta = new_db_meta();
    let mut p = db_meta.to_pb()?;
    p.ver = 0;
    p.min_reader_ver = 0;

    let res = mt::DatabaseMeta::from_pb(p);
    assert_eq!(
        Incompatible {
            reason: s(
                "message ver=0 is smaller than executable MIN_MSG_VER(1) that this program can read"
            )
        },
        res.unwrap_err()
    );

    Ok(())
}

#[test]
fn test_build_pb_buf() -> anyhow::Result<()> {
    // build serialized buf of protobuf data, for backward compatibility test with a new version binary.

    // DatabaseMeta
    {
        let db_meta = new_db_meta_share();
        let p = db_meta.to_pb()?;

        let mut buf = vec![];
        common_protos::prost::Message::encode(&p, &mut buf)?;
        println!("db:{:?}", buf);
    }

    // TableMeta
    {
        let tbl = new_table_meta();

        let p = tbl.to_pb()?;

        let mut buf = vec![];
        common_protos::prost::Message::encode(&p, &mut buf)?;
        println!("table:{:?}", buf);
    }

    // ShareMeta
    {
        let tbl = new_share_meta_share_from_db_ids();

        let p = tbl.to_pb()?;

        let mut buf = vec![];
        common_protos::prost::Message::encode(&p, &mut buf)?;
        println!("share:{:?}", buf);
    }

    // ShareAccountMeta
    {
        let share_account_meta = new_share_account_meta();

        let p = share_account_meta.to_pb()?;

        let mut buf = vec![];
        common_protos::prost::Message::encode(&p, &mut buf)?;
        println!("share account:{:?}", buf);
    }

    // TableCopiedFileInfo
    {
        let copied_file = new_table_copied_file_info_v6();
        let p = copied_file.to_pb()?;

        let mut buf = vec![];
        common_protos::prost::Message::encode(&p, &mut buf)?;
        println!("copied_file:{:?}", buf);
    }

    // TableCopiedFileLock
    {
        let copied_file_lock = new_table_copied_file_lock_v7();
        let p = copied_file_lock.to_pb()?;

        let mut buf = vec![];
        common_protos::prost::Message::encode(&p, &mut buf)?;
        println!("copied_file_lock:{:?}", buf);
    }

    // schema
    {
        let schema = new_latest_schema();
        let p = schema.to_pb()?;

        let mut buf = vec![];
        common_protos::prost::Message::encode(&p, &mut buf)?;
        println!("schema:{:?}", buf);
    }

    Ok(())
}
