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

use std::any::Any;
use std::sync::Arc;

use common_catalog::catalog_kind::CATALOG_DEFAULT;
use common_catalog::plan::DataSourcePlan;
use common_catalog::plan::PartStatistics;
use common_catalog::plan::Partitions;
use common_catalog::plan::PushDownInfo;
use common_exception::Result;
use common_expression::DataBlock;
use common_meta_app::schema::TableIdent;
use common_meta_app::schema::TableInfo;
use common_meta_app::schema::TableMeta;
use common_pipeline_core::processors::processor::ProcessorPtr;
use common_pipeline_sources::AsyncSource;
use common_pipeline_sources::AsyncSourcer;

use super::fuse_snapshot::FuseSnapshot;
use super::table_args::parse_func_history_args;
use crate::pipelines::processors::port::OutputPort;
use crate::pipelines::Pipeline;
use crate::sessions::TableContext;
use crate::table_functions::string_literal;
use crate::table_functions::TableArgs;
use crate::table_functions::TableFunction;
use crate::FuseTable;
use crate::Table;

const FUSE_FUNC_SNAPSHOT: &str = "fuse_snapshot";

pub struct FuseSnapshotTable {
    table_info: TableInfo,
    arg_database_name: String,
    arg_table_name: String,
}

impl FuseSnapshotTable {
    pub fn create(
        database_name: &str,
        table_func_name: &str,
        table_id: u64,
        table_args: TableArgs,
    ) -> Result<Arc<dyn TableFunction>> {
        let (arg_database_name, arg_table_name) = parse_func_history_args(&table_args)?;

        let engine = FUSE_FUNC_SNAPSHOT.to_owned();

        let table_info = TableInfo {
            ident: TableIdent::new(table_id, 0),
            desc: format!("'{}'.'{}'", database_name, table_func_name),
            name: table_func_name.to_string(),
            meta: TableMeta {
                schema: FuseSnapshot::schema(),
                engine,
                ..Default::default()
            },
            ..Default::default()
        };

        Ok(Arc::new(FuseSnapshotTable {
            table_info,
            arg_database_name,
            arg_table_name,
        }))
    }
}

#[async_trait::async_trait]
impl Table for FuseSnapshotTable {
    fn as_any(&self) -> &dyn Any {
        self
    }

    fn get_table_info(&self) -> &TableInfo {
        &self.table_info
    }

    #[async_backtrace::framed]
    async fn read_partitions(
        &self,
        _ctx: Arc<dyn TableContext>,
        _push_downs: Option<PushDownInfo>,
    ) -> Result<(PartStatistics, Partitions)> {
        Ok((PartStatistics::default(), Partitions::default()))
    }

    fn table_args(&self) -> Option<TableArgs> {
        Some(TableArgs::new_positioned(vec![
            string_literal(self.arg_database_name.as_str()),
            string_literal(self.arg_table_name.as_str()),
        ]))
    }

    fn read_data(
        &self,
        ctx: Arc<dyn TableContext>,
        plan: &DataSourcePlan,
        pipeline: &mut Pipeline,
    ) -> Result<()> {
        pipeline.add_source(
            |output| {
                FuseSnapshotSource::create(
                    ctx.clone(),
                    output,
                    self.arg_database_name.to_owned(),
                    self.arg_table_name.to_owned(),
                    plan.push_downs.as_ref().and_then(|extras| extras.limit),
                )
            },
            1,
        )?;

        Ok(())
    }
}

impl TableFunction for FuseSnapshotTable {
    fn function_name(&self) -> &str {
        self.name()
    }

    fn as_table<'a>(self: Arc<Self>) -> Arc<dyn Table + 'a>
    where Self: 'a {
        self
    }
}

struct FuseSnapshotSource {
    finish: bool,
    ctx: Arc<dyn TableContext>,
    arg_database_name: String,
    arg_table_name: String,
    limit: Option<usize>,
}

impl FuseSnapshotSource {
    pub fn create(
        ctx: Arc<dyn TableContext>,
        output: Arc<OutputPort>,
        arg_database_name: String,
        arg_table_name: String,
        limit: Option<usize>,
    ) -> Result<ProcessorPtr> {
        AsyncSourcer::create(ctx.clone(), output, FuseSnapshotSource {
            ctx,
            finish: false,
            arg_table_name,
            arg_database_name,
            limit,
        })
    }
}

#[async_trait::async_trait]
impl AsyncSource for FuseSnapshotSource {
    const NAME: &'static str = "fuse_snapshot";

    #[async_trait::unboxed_simple]
    #[async_backtrace::framed]
    async fn generate(&mut self) -> Result<Option<DataBlock>> {
        if self.finish {
            return Ok(None);
        }

        self.finish = true;
        let tenant_id = self.ctx.get_tenant();
        let tbl = self
            .ctx
            .get_catalog(CATALOG_DEFAULT)?
            .get_table(
                tenant_id.as_str(),
                self.arg_database_name.as_str(),
                self.arg_table_name.as_str(),
            )
            .await?;

        let tbl = FuseTable::try_from_table(tbl.as_ref())?;
        Ok(Some(
            FuseSnapshot::new(self.ctx.clone(), tbl)
                .get_snapshots(self.limit)
                .await?,
        ))
    }
}
