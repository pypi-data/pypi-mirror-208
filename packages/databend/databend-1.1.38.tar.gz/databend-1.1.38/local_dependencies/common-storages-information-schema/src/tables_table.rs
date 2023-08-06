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

use std::collections::BTreeMap;
use std::sync::Arc;

use common_catalog::table::Table;
use common_meta_app::schema::TableIdent;
use common_meta_app::schema::TableInfo;
use common_meta_app::schema::TableMeta;
use common_storages_view::view_table::ViewTable;
use common_storages_view::view_table::QUERY;

pub struct TablesTable {}

impl TablesTable {
    pub fn create(table_id: u64) -> Arc<dyn Table> {
        let query = "SELECT
            database AS table_catalog,
            database AS table_schema,
            name AS table_name,
            'BASE TABLE' AS table_type,
            engine AS engine,
            created_on AS create_time,
            dropped_on AS drop_time,
            data_size AS data_length,
            index_size AS index_length,
            '' AS table_comment
        FROM system.tables;";

        let mut options = BTreeMap::new();
        options.insert(QUERY.to_string(), query.to_string());
        let table_info = TableInfo {
            desc: "'information_schema'.'tables'".to_string(),
            name: "tables".to_string(),
            ident: TableIdent::new(table_id, 0),
            meta: TableMeta {
                options,
                engine: "VIEW".to_string(),
                ..Default::default()
            },
            ..Default::default()
        };

        ViewTable::create(table_info)
    }
}
