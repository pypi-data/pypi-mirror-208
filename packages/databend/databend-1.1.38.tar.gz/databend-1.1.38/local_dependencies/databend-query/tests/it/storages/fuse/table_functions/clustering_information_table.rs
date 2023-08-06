//  Copyright 2021 Datafuse Labs.
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

use std::sync::Arc;

use common_base::base::tokio;
use common_catalog::plan::PushDownInfo;
use common_catalog::table_args::TableArgs;
use common_catalog::table_context::TableContext;
use common_exception::ErrorCode;
use common_exception::Result;
use common_expression::DataBlock;
use common_expression::Scalar;
use common_expression::SendableDataBlockStream;
use common_sql::executor::table_read_plan::ToReadDataSourcePlan;
use common_storages_fuse::table_functions::ClusteringInformationTable;
use databend_query::sessions::QueryContext;
use databend_query::stream::ReadDataBlockStream;
use databend_query::test_kits::table_test_fixture::*;
use tokio_stream::StreamExt;

#[tokio::test(flavor = "multi_thread")]
async fn test_clustering_information_table_read() -> Result<()> {
    let fixture = TestFixture::new().await;
    let db = fixture.default_db_name();
    let tbl = fixture.default_table_name();
    let ctx = fixture.ctx();

    // test db & table
    fixture.create_default_table().await?;

    // func args
    let arg_db = Scalar::String(db.as_bytes().to_vec());
    let arg_tbl = Scalar::String(tbl.as_bytes().to_vec());

    {
        let expected = vec![
            "+----------+----------+----------+----------+----------+----------+",
            "| Column 0 | Column 1 | Column 2 | Column 3 | Column 4 | Column 5 |",
            "+----------+----------+----------+----------+----------+----------+",
            "| '(id)'   | 0        | 0        | 0        | 0        | {}       |",
            "+----------+----------+----------+----------+----------+----------+",
        ];

        expects_ok(
            "empty_data_set",
            test_drive_clustering_information(
                TableArgs::new_positioned(vec![arg_db.clone(), arg_tbl.clone()]),
                ctx.clone(),
            )
            .await,
            expected,
        )
        .await?;
    }

    {
        let qry = format!("insert into {}.{} values(1, (2, 3)),(2, (4, 6))", db, tbl);
        execute_query(ctx.clone(), qry.as_str()).await?;
        let expected = vec![
            "+----------+----------+----------+----------+----------+-------------+",
            "| Column 0 | Column 1 | Column 2 | Column 3 | Column 4 | Column 5    |",
            "+----------+----------+----------+----------+----------+-------------+",
            "| '(id)'   | 1        | 0        | 0        | 1        | {\"00001\":1} |",
            "+----------+----------+----------+----------+----------+-------------+",
        ];

        let qry = format!("select * from clustering_information('{}', '{}')", db, tbl);

        expects_ok(
            "clustering_information",
            execute_query(ctx.clone(), qry.as_str()).await,
            expected,
        )
        .await?;
    }

    {
        // incompatible table engine
        let qry = format!("create table {}.in_mem (a int) engine =Memory", db);
        execute_query(ctx.clone(), qry.as_str()).await?;

        let qry = format!(
            "select * from clustering_information('{}', '{}')",
            db, "in_mem"
        );
        let output_stream = execute_query(ctx.clone(), qry.as_str()).await?;
        // TODO(xuanwo): assign a new error code
        expects_err(
            "unsupported_table_engine",
            ErrorCode::INTERNAL,
            output_stream.collect::<Result<Vec<DataBlock>>>().await,
        );
    }

    Ok(())
}

async fn test_drive_clustering_information(
    tbl_args: TableArgs,
    ctx: Arc<QueryContext>,
) -> Result<SendableDataBlockStream> {
    let func = ClusteringInformationTable::create("system", "clustering_information", 1, tbl_args)?;
    let source_plan = func
        .clone()
        .as_table()
        .read_plan(ctx.clone(), Some(PushDownInfo::default()))
        .await?;
    ctx.set_partitions(source_plan.parts.clone())?;
    func.as_table()
        .read_data_block_stream(ctx, &source_plan)
        .await
}
