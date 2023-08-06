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

use std::collections::HashMap;
use std::sync::Arc;

use common_catalog::table_args::TableArgs;
use common_exception::ErrorCode;
use common_exception::Result;
use common_meta_types::MetaId;
use itertools::Itertools;
use parking_lot::RwLock;

use crate::catalogs::SYS_TBL_FUC_ID_END;
use crate::catalogs::SYS_TBL_FUNC_ID_BEGIN;
use crate::storages::fuse::table_functions::ClusteringInformationTable;
use crate::storages::fuse::table_functions::FuseBlockTable;
use crate::storages::fuse::table_functions::FuseSegmentTable;
use crate::storages::fuse::table_functions::FuseSnapshotTable;
use crate::storages::fuse::table_functions::FuseStatisticTable;
use crate::table_functions::async_crash_me::AsyncCrashMeTable;
use crate::table_functions::infer_schema::InferSchemaTable;
use crate::table_functions::list_stage::ListStageTable;
use crate::table_functions::numbers::NumbersTable;
use crate::table_functions::srf::RangeTable;
use crate::table_functions::sync_crash_me::SyncCrashMeTable;
use crate::table_functions::GPT2SQLTable;
use crate::table_functions::TableFunction;

type TableFunctionCreators = RwLock<HashMap<String, (MetaId, Arc<dyn TableFunctionCreator>)>>;

pub trait TableFunctionCreator: Send + Sync {
    fn try_create(
        &self,
        db_name: &str,
        tbl_func_name: &str,
        tbl_id: MetaId,
        arg: TableArgs,
    ) -> Result<Arc<dyn TableFunction>>;
}

impl<T> TableFunctionCreator for T
where
    T: Fn(&str, &str, MetaId, TableArgs) -> Result<Arc<dyn TableFunction>>,
    T: Send + Sync,
{
    fn try_create(
        &self,
        db_name: &str,
        tbl_func_name: &str,
        tbl_id: MetaId,
        arg: TableArgs,
    ) -> Result<Arc<dyn TableFunction>> {
        self(db_name, tbl_func_name, tbl_id, arg)
    }
}

#[derive(Default)]
pub struct TableFunctionFactory {
    creators: TableFunctionCreators,
}

impl TableFunctionFactory {
    pub fn create() -> Self {
        let mut id = SYS_TBL_FUNC_ID_BEGIN;
        let mut next_id = || -> MetaId {
            if id >= SYS_TBL_FUC_ID_END {
                panic!("function table id used up")
            } else {
                let r = id;
                id += 1;
                r
            }
        };

        let mut creators: HashMap<String, (MetaId, Arc<dyn TableFunctionCreator>)> =
            Default::default();

        let number_table_func_creator: Arc<dyn TableFunctionCreator> =
            Arc::new(NumbersTable::create);

        creators.insert(
            "numbers".to_string(),
            (next_id(), number_table_func_creator.clone()),
        );
        creators.insert(
            "numbers_mt".to_string(),
            (next_id(), number_table_func_creator.clone()),
        );
        creators.insert(
            "numbers_local".to_string(),
            (next_id(), number_table_func_creator),
        );

        creators.insert(
            "fuse_snapshot".to_string(),
            (next_id(), Arc::new(FuseSnapshotTable::create)),
        );
        creators.insert(
            "fuse_segment".to_string(),
            (next_id(), Arc::new(FuseSegmentTable::create)),
        );
        creators.insert(
            "fuse_block".to_string(),
            (next_id(), Arc::new(FuseBlockTable::create)),
        );
        creators.insert(
            "fuse_statistic".to_string(),
            (next_id(), Arc::new(FuseStatisticTable::create)),
        );

        creators.insert(
            "clustering_information".to_string(),
            (next_id(), Arc::new(ClusteringInformationTable::create)),
        );

        creators.insert(
            "sync_crash_me".to_string(),
            (next_id(), Arc::new(SyncCrashMeTable::create)),
        );

        creators.insert(
            "async_crash_me".to_string(),
            (next_id(), Arc::new(AsyncCrashMeTable::create)),
        );

        creators.insert(
            "infer_schema".to_string(),
            (next_id(), Arc::new(InferSchemaTable::create)),
        );

        creators.insert(
            "list_stage".to_string(),
            (next_id(), Arc::new(ListStageTable::create)),
        );

        creators.insert(
            "generate_series".to_string(),
            (next_id(), Arc::new(RangeTable::create)),
        );

        creators.insert(
            "range".to_string(),
            (next_id(), Arc::new(RangeTable::create)),
        );

        creators.insert(
            "ai_to_sql".to_string(),
            (next_id(), Arc::new(GPT2SQLTable::create)),
        );

        TableFunctionFactory {
            creators: RwLock::new(creators),
        }
    }

    pub fn get(&self, func_name: &str, tbl_args: TableArgs) -> Result<Arc<dyn TableFunction>> {
        let lock = self.creators.read();
        let func_name = func_name.to_lowercase();
        let (id, factory) = lock.get(&func_name).ok_or_else(|| {
            ErrorCode::UnknownTable(format!("Unknown table function {}", func_name))
        })?;
        let func = factory.try_create("", &func_name, *id, tbl_args)?;
        Ok(func)
    }

    pub fn list(&self) -> Vec<String> {
        self.creators
            .read()
            .iter()
            .map(|(name, (id, _))| (name, id))
            .sorted_by(|a, b| Ord::cmp(a.1, b.1))
            .map(|(name, _)| name.clone())
            .collect()
    }
}
