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

use std::net::SocketAddr;
use std::sync::Arc;
use std::time::Duration;

use common_catalog::table::Table;
use common_catalog::table_context::TableContext;
use common_exception::Result;
use common_expression::types::number::Int64Type;
use common_expression::types::number::UInt32Type;
use common_expression::types::number::UInt64Type;
use common_expression::types::NumberDataType;
use common_expression::types::StringType;
use common_expression::utils::FromData;
use common_expression::DataBlock;
use common_expression::FromOptData;
use common_expression::TableDataType;
use common_expression::TableField;
use common_expression::TableSchemaRefExt;
use common_meta_app::schema::TableIdent;
use common_meta_app::schema::TableInfo;
use common_meta_app::schema::TableMeta;

use crate::SyncOneBlockSystemTable;
use crate::SyncSystemTable;

pub struct ProcessesTable {
    table_info: TableInfo,
}

#[async_trait::async_trait]
impl SyncSystemTable for ProcessesTable {
    const NAME: &'static str = "system.processes";

    fn get_table_info(&self) -> &TableInfo {
        &self.table_info
    }

    fn get_full_data(&self, ctx: Arc<dyn TableContext>) -> Result<DataBlock> {
        let processes_info = ctx.get_processes_info();

        let mut processes_id = Vec::with_capacity(processes_info.len());
        let mut processes_type = Vec::with_capacity(processes_info.len());
        let mut processes_host = Vec::with_capacity(processes_info.len());
        let mut processes_user = Vec::with_capacity(processes_info.len());
        let mut processes_state = Vec::with_capacity(processes_info.len());
        let mut processes_database = Vec::with_capacity(processes_info.len());
        let mut processes_extra_info = Vec::with_capacity(processes_info.len());
        let mut processes_memory_usage = Vec::with_capacity(processes_info.len());
        let mut processes_data_read_bytes = Vec::with_capacity(processes_info.len());
        let mut processes_data_write_bytes = Vec::with_capacity(processes_info.len());
        let mut processes_scan_progress_read_rows = Vec::with_capacity(processes_info.len());
        let mut processes_scan_progress_read_bytes = Vec::with_capacity(processes_info.len());
        let mut processes_mysql_connection_id = Vec::with_capacity(processes_info.len());
        let mut processes_time = Vec::with_capacity(processes_info.len());
        let mut processes_status = Vec::with_capacity(processes_info.len());

        for process_info in &processes_info {
            let data_metrics = &process_info.data_metrics;
            let scan_progress = process_info.scan_progress_value.clone().unwrap_or_default();
            let time = process_info
                .created_time
                .elapsed()
                .unwrap_or(Duration::from_secs(0))
                .as_secs();

            processes_id.push(process_info.id.clone().into_bytes());
            processes_type.push(process_info.typ.clone().into_bytes());
            processes_state.push(process_info.state.clone().into_bytes());
            processes_database.push(process_info.database.clone().into_bytes());
            processes_host.push(ProcessesTable::process_host(&process_info.client_address));
            processes_user.push(
                ProcessesTable::process_option_value(process_info.user.clone())
                    .name
                    .into_bytes(),
            );
            processes_extra_info.push(
                ProcessesTable::process_option_value(process_info.session_extra_info.clone())
                    .into_bytes(),
            );
            processes_memory_usage.push(process_info.memory_usage);
            processes_scan_progress_read_rows.push(scan_progress.rows as u64);
            processes_scan_progress_read_bytes.push(scan_progress.bytes as u64);
            processes_mysql_connection_id.push(process_info.mysql_connection_id);
            processes_time.push(time);

            if let Some(data_metrics) = data_metrics {
                processes_data_read_bytes.push(data_metrics.get_read_bytes() as u64);
                processes_data_write_bytes.push(data_metrics.get_write_bytes() as u64);
            } else {
                processes_data_read_bytes.push(0);
                processes_data_write_bytes.push(0);
            }

            // Status info.
            processes_status.push(
                process_info
                    .status_info
                    .clone()
                    .unwrap_or("".to_owned())
                    .into_bytes(),
            );
        }

        Ok(DataBlock::new_from_columns(vec![
            StringType::from_data(processes_id),
            StringType::from_data(processes_type),
            StringType::from_opt_data(processes_host),
            StringType::from_data(processes_user),
            StringType::from_data(processes_state),
            StringType::from_data(processes_database),
            StringType::from_data(processes_extra_info),
            Int64Type::from_data(processes_memory_usage),
            UInt64Type::from_data(processes_data_read_bytes),
            UInt64Type::from_data(processes_data_write_bytes),
            UInt64Type::from_data(processes_scan_progress_read_rows),
            UInt64Type::from_data(processes_scan_progress_read_bytes),
            UInt32Type::from_opt_data(processes_mysql_connection_id),
            UInt64Type::from_data(processes_time),
            StringType::from_data(processes_status),
        ]))
    }
}

impl ProcessesTable {
    pub fn create(table_id: u64) -> Arc<dyn Table> {
        let schema = TableSchemaRefExt::create(vec![
            TableField::new("id", TableDataType::String),
            TableField::new("type", TableDataType::String),
            TableField::new(
                "host",
                TableDataType::Nullable(Box::new(TableDataType::String)),
            ),
            TableField::new("user", TableDataType::String),
            TableField::new("command", TableDataType::String),
            TableField::new("database", TableDataType::String),
            TableField::new("extra_info", TableDataType::String),
            TableField::new("memory_usage", TableDataType::Number(NumberDataType::Int64)),
            TableField::new(
                "data_read_bytes",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new(
                "data_write_bytes",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new(
                "scan_progress_read_rows",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new(
                "scan_progress_read_bytes",
                TableDataType::Number(NumberDataType::UInt64),
            ),
            TableField::new(
                "mysql_connection_id",
                TableDataType::Nullable(Box::new(TableDataType::Number(NumberDataType::UInt32))),
            ),
            TableField::new("time", TableDataType::Number(NumberDataType::UInt64)),
            TableField::new("status", TableDataType::String),
        ]);

        let table_info = TableInfo {
            desc: "'system'.'processes'".to_string(),
            name: "processes".to_string(),
            ident: TableIdent::new(table_id, 0),
            meta: TableMeta {
                schema,
                engine: "SystemProcesses".to_string(),

                ..Default::default()
            },
            ..Default::default()
        };

        SyncOneBlockSystemTable::create(ProcessesTable { table_info })
    }

    fn process_host(client_address: &Option<SocketAddr>) -> Option<Vec<u8>> {
        client_address.as_ref().map(|s| s.to_string().into_bytes())
    }

    fn process_option_value<T>(opt: Option<T>) -> T
    where T: Default {
        opt.unwrap_or_default()
    }
}
