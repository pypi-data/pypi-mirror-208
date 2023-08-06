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

use std::sync::Arc;

use common_exception::Result;
use common_expression::DataBlock;
use common_expression::DataSchema;
use common_storages_fuse::FuseTable;

use crate::procedures::OneBlockProcedure;
use crate::procedures::Procedure;
use crate::procedures::ProcedureFeatures;
use crate::sessions::QueryContext;
use crate::sessions::TableContext;
use crate::storages::fuse::table_functions::FuseSnapshot;

pub struct FuseSnapshotProcedure {}

impl FuseSnapshotProcedure {
    pub fn try_create() -> Result<Box<dyn Procedure>> {
        // Ok(Box::new(FuseSnapshotProcedure {}.to_procedure()))
        Ok(FuseSnapshotProcedure {}.into_procedure())
    }
}

#[async_trait::async_trait]
impl OneBlockProcedure for FuseSnapshotProcedure {
    fn name(&self) -> &str {
        "FUSE_SNAPSHOT"
    }

    fn features(&self) -> ProcedureFeatures {
        ProcedureFeatures::default().variadic_arguments(2, 3)
    }

    #[async_backtrace::framed]
    async fn all_data(&self, ctx: Arc<QueryContext>, args: Vec<String>) -> Result<DataBlock> {
        let database_name = args[0].clone();
        let table_name = args[1].clone();
        let tenant_id = ctx.get_tenant();
        let tbl = ctx
            .get_catalog(&ctx.get_current_catalog())?
            .get_table(
                tenant_id.as_str(),
                database_name.as_str(),
                table_name.as_str(),
            )
            .await?;

        let tbl = FuseTable::try_from_table(tbl.as_ref())?;

        Ok(FuseSnapshot::new(ctx, tbl).get_snapshots(None).await?)
    }

    fn schema(&self) -> Arc<DataSchema> {
        Arc::new(FuseSnapshot::schema().into())
    }
}
