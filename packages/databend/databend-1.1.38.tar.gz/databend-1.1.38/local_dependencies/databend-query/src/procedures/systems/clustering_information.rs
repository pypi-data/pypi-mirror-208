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

use crate::procedures::OneBlockProcedure;
use crate::procedures::Procedure;
use crate::procedures::ProcedureFeatures;
use crate::sessions::QueryContext;
use crate::sessions::TableContext;
use crate::storages::fuse::table_functions::get_cluster_keys;
use crate::storages::fuse::table_functions::ClusteringInformation;
use crate::storages::fuse::FuseTable;

pub struct ClusteringInformationProcedure {}

impl ClusteringInformationProcedure {
    pub fn try_create() -> Result<Box<dyn Procedure>> {
        Ok(ClusteringInformationProcedure {}.into_procedure())
    }
}

#[async_trait::async_trait]
impl OneBlockProcedure for ClusteringInformationProcedure {
    fn name(&self) -> &str {
        "CLUSTERING_INFORMATION"
    }

    fn features(&self) -> ProcedureFeatures {
        // Todo(zhyass): ProcedureFeatures::default().variadic_arguments(2, 3)
        ProcedureFeatures::default().num_arguments(2)
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
        let definition = if args.len() > 2 { &args[2] } else { "" };
        let (cluster_keys, plain) = get_cluster_keys(ctx.clone(), tbl, definition)?;

        Ok(
            ClusteringInformation::new(ctx, tbl, plain.unwrap_or_default(), cluster_keys)
                .get_clustering_info()
                .await?,
        )
    }

    fn schema(&self) -> Arc<DataSchema> {
        Arc::new(ClusteringInformation::schema().into())
    }
}
