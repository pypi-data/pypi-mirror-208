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

use std::cmp::max;
use std::sync::Arc;

use common_catalog::table::Table;
use common_catalog::table_context::TableContext;
use common_exception::Result;
use common_expression::types::StringType;
use common_expression::utils::FromData;
use common_expression::DataBlock;
use common_expression::TableDataType;
use common_expression::TableField;
use common_expression::TableSchemaRefExt;
use common_meta_app::schema::TableIdent;
use common_meta_app::schema::TableInfo;
use common_meta_app::schema::TableMeta;

use crate::SyncOneBlockSystemTable;
use crate::SyncSystemTable;

pub struct BuildOptionsTable {
    table_info: TableInfo,
}

impl SyncSystemTable for BuildOptionsTable {
    const NAME: &'static str = "system.build_options";

    fn get_table_info(&self) -> &TableInfo {
        &self.table_info
    }

    fn get_full_data(&self, _: Arc<dyn TableContext>) -> Result<DataBlock> {
        let mut cargo_features: Vec<Vec<u8>>;

        if let Some(features) = option_env!("VERGEN_CARGO_FEATURES") {
            cargo_features = features
                .split_terminator(',')
                .map(|x| x.trim().as_bytes().to_vec())
                .collect();
        } else {
            cargo_features = vec!["not available".as_bytes().to_vec()];
        }

        let mut target_features: Vec<Vec<u8>> = env!("DATABEND_CARGO_CFG_TARGET_FEATURE")
            .split_terminator(',')
            .map(|x| x.trim().as_bytes().to_vec())
            .collect();

        let length = max(cargo_features.len(), target_features.len());

        cargo_features.resize(length, "".as_bytes().to_vec());
        target_features.resize(length, "".as_bytes().to_vec());

        Ok(DataBlock::new_from_columns(vec![
            StringType::from_data(cargo_features),
            StringType::from_data(target_features),
        ]))
    }
}

impl BuildOptionsTable {
    pub fn create(table_id: u64) -> Arc<dyn Table> {
        let schema = TableSchemaRefExt::create(vec![
            TableField::new("cargo_features", TableDataType::String),
            TableField::new("target_features", TableDataType::String),
        ]);

        let table_info = TableInfo {
            desc: "'system'.'build_options'".to_string(),
            name: "build_options".to_string(),
            ident: TableIdent::new(table_id, 0),
            meta: TableMeta {
                schema,
                engine: "SystemBuildOptions".to_string(),
                ..Default::default()
            },
            ..Default::default()
        };

        SyncOneBlockSystemTable::create(BuildOptionsTable { table_info })
    }
}
