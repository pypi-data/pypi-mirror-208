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

use chrono::NaiveDateTime;
use common_exception::Result;
use common_expression::types::number::NumberScalar;
use common_expression::types::NumberDataType;
use common_expression::ColumnBuilder;
use common_expression::Scalar;
use common_expression::TableDataType;
use common_expression::TableField;
use common_expression::TableSchemaRef;
use common_expression::TableSchemaRefExt;
use serde::Serialize;
use serde::Serializer;
use serde_repr::Serialize_repr;

use crate::SystemLogElement;
use crate::SystemLogQueue;
use crate::SystemLogTable;

#[derive(Clone, Copy, Serialize_repr)]
#[repr(u8)]
pub enum LogType {
    Start = 1,
    Finish = 2,
    Error = 3,
    Aborted = 4,
}

fn date_str<S>(dt: &i32, s: S) -> Result<S::Ok, S::Error>
where S: Serializer {
    let t = NaiveDateTime::from_timestamp_opt(i64::from(*dt) * 24 * 3600, 0).unwrap();
    s.serialize_str(t.format("%Y-%m-%d").to_string().as_str())
}

fn datetime_str<S>(dt: &i64, s: S) -> Result<S::Ok, S::Error>
where S: Serializer {
    let t = NaiveDateTime::from_timestamp_opt(
        dt / 1_000_000,
        TryFrom::try_from((dt % 1_000_000) * 1000).unwrap_or(0),
        // u32::try_from((dt % 1_000_000) * 1000).unwrap_or(0),
    )
    .unwrap();
    s.serialize_str(t.format("%Y-%m-%d %H:%M:%S%.6f").to_string().as_str())
}

#[derive(Clone, Serialize)]
pub struct QueryLogElement {
    // Type.
    pub log_type: LogType,
    pub handler_type: String,

    // User.
    pub tenant_id: String,
    pub cluster_id: String,
    pub sql_user: String,

    #[serde(skip_serializing)]
    pub sql_user_quota: String,
    #[serde(skip_serializing)]
    pub sql_user_privileges: String,

    // Query.
    pub query_id: String,
    pub query_kind: String,
    pub query_text: String,

    #[serde(serialize_with = "date_str")]
    pub event_date: i32,
    #[serde(serialize_with = "datetime_str")]
    pub event_time: i64,
    #[serde(serialize_with = "datetime_str")]
    pub query_start_time: i64,
    pub query_duration_ms: i64,

    // Schema.
    pub current_database: String,
    pub databases: String,
    pub tables: String,
    pub columns: String,
    pub projections: String,

    // Stats.
    pub written_rows: u64,
    pub written_bytes: u64,
    pub written_io_bytes: u64,
    pub written_io_bytes_cost_ms: u64,
    pub scan_rows: u64,
    pub scan_bytes: u64,
    pub scan_io_bytes: u64,
    pub scan_io_bytes_cost_ms: u64,
    pub scan_partitions: u64,
    pub total_partitions: u64,
    pub result_rows: u64,
    pub result_bytes: u64,
    pub cpu_usage: u32,
    pub memory_usage: u64,

    // Client.
    pub client_info: String,
    pub client_address: String,

    // Exception.
    pub exception_code: i32,
    pub exception_text: String,
    pub stack_trace: String,

    // Server.
    pub server_version: String,

    // Session settings
    #[serde(skip_serializing)]
    pub session_settings: String,

    // Extra.
    pub extra: String,
}

impl SystemLogElement for QueryLogElement {
    const TABLE_NAME: &'static str = "query_log";

    fn schema() -> TableSchemaRef {
        TableSchemaRefExt::create(vec![
            // Type.
            TableField::new("log_type", TableDataType::Number(NumberDataType::Int8)),
            TableField::new("handler_type", TableDataType::String),
            // User.
            TableField::new("tenant_id", TableDataType::String),
            TableField::new("cluster_id", TableDataType::String),
            TableField::new("sql_user", TableDataType::String),
            TableField::new("sql_user_quota", TableDataType::String),
            TableField::new("sql_user_privileges", TableDataType::String),
            // Query.
            TableField::new("query_id", TableDataType::String),
            TableField::new("query_kind", TableDataType::String),
            TableField::new("query_text", TableDataType::String),
            TableField::new("event_date", TableDataType::Date),
            TableField::new("event_time", TableDataType::Timestamp),
            TableField::new("query_start_time", TableDataType::Timestamp),
            TableField::new(
                "query_duration_ms",
                TableDataType::Number(NumberDataType::Int64),
            ),
            // Schema.
            TableField::new("current_database", TableDataType::String),
            TableField::new("databases", TableDataType::String),
            TableField::new("tables", TableDataType::String),
            TableField::new("columns", TableDataType::String),
            TableField::new("projections", TableDataType::String),
            // Stats.
            TableField::new(
                "written_rows",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new(
                "written_bytes",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new(
                "written_io_bytes",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new(
                "written_io_bytes_cost_ms",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new("scan_rows", TableDataType::Number(NumberDataType::UInt64)),
            TableField::new("scan_bytes", TableDataType::Number(NumberDataType::UInt64)),
            TableField::new(
                "scan_io_bytes",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new(
                "scan_io_bytes_cost_ms",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new(
                "scan_partitions",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new(
                "total_partitions",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new("result_rows", TableDataType::Number(NumberDataType::UInt64)),
            TableField::new(
                "result_bytes",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new("cpu_usage", TableDataType::Number(NumberDataType::UInt32)),
            TableField::new(
                "memory_usage",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            // Client.
            TableField::new("client_info", TableDataType::String),
            TableField::new("client_address", TableDataType::String),
            // Exception.
            TableField::new(
                "exception_code",
                TableDataType::Number(NumberDataType::Int32),
            ),
            TableField::new("exception_text", TableDataType::String),
            TableField::new("stack_trace", TableDataType::String),
            // Server.
            TableField::new("server_version", TableDataType::String),
            // Session settings
            TableField::new("session_settings", TableDataType::String),
            // Extra.
            TableField::new("extra", TableDataType::String),
        ])
    }

    fn fill_to_data_block(&self, columns: &mut Vec<ColumnBuilder>) -> Result<()> {
        let mut columns = columns.iter_mut();
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::Int8(self.log_type as i8)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.handler_type.as_bytes().to_vec()).as_ref());
        // User.
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.tenant_id.as_bytes().to_vec()).as_ref());

        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.cluster_id.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.sql_user.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.sql_user_quota.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.sql_user_privileges.as_bytes().to_vec()).as_ref());
        // Query.
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.query_id.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.query_kind.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.query_text.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Date(self.event_date).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Timestamp(self.event_time).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Timestamp(self.query_start_time).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::Int64(self.query_duration_ms)).as_ref());
        // Schema.
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.current_database.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.databases.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.tables.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.columns.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.projections.as_bytes().to_vec()).as_ref());
        // Stats.
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.written_rows)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.written_bytes)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.written_io_bytes)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.written_io_bytes_cost_ms)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.scan_rows)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.scan_bytes)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.scan_io_bytes)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.scan_io_bytes_cost_ms)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.scan_partitions)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.total_partitions)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.result_rows)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.result_bytes)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt32(self.cpu_usage)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::UInt64(self.memory_usage)).as_ref());
        // Client.
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.client_info.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.client_address.as_bytes().to_vec()).as_ref());
        // Exception.
        columns
            .next()
            .unwrap()
            .push(Scalar::Number(NumberScalar::Int32(self.exception_code)).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.exception_text.as_bytes().to_vec()).as_ref());
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.stack_trace.as_bytes().to_vec()).as_ref());
        // Server.
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.server_version.as_bytes().to_vec()).as_ref());
        // Session settings
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.session_settings.as_bytes().to_vec()).as_ref());
        // Extra.
        columns
            .next()
            .unwrap()
            .push(Scalar::String(self.extra.as_bytes().to_vec()).as_ref());
        Ok(())
    }
}

pub type QueryLogQueue = SystemLogQueue<QueryLogElement>;
pub type QueryLogTable = SystemLogTable<QueryLogElement>;
