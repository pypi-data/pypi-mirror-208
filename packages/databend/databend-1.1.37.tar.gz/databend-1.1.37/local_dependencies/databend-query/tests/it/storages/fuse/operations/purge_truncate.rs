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
use common_base::base::tokio;
use common_exception::Result;
use databend_query::test_kits::table_test_fixture::append_sample_data;
use databend_query::test_kits::table_test_fixture::check_data_dir;
use databend_query::test_kits::table_test_fixture::execute_command;
use databend_query::test_kits::table_test_fixture::history_should_have_item;
use databend_query::test_kits::table_test_fixture::TestFixture;

#[tokio::test(flavor = "multi_thread")]
async fn test_fuse_truncate_purge_stmt() -> Result<()> {
    let fixture = TestFixture::new().await;
    let db = fixture.default_db_name();
    let tbl = fixture.default_table_name();
    let ctx = fixture.ctx();
    fixture.create_default_table().await?;

    // ingests some 2 blocks
    append_sample_data(1, &fixture).await?;
    append_sample_data(1, &fixture).await?;

    let expected_index_count = 2;
    // there should be some data there: 2 snapshot, 2 segment, 2 block
    check_data_dir(
        &fixture,
        "truncate_purge",
        2,
        0,
        2,
        2,
        expected_index_count,
        Some(()),
        None,
    )
    .await?;

    // let's truncate
    let qry = format!("truncate table {}.{} purge", db, tbl);
    execute_command(ctx.clone(), qry.as_str()).await?;

    // one history item left there
    history_should_have_item(
        &fixture,
        "after_truncate_there_should_be_one_history_item_left",
        1,
    )
    .await?;

    // there should be only a snapshot file left there, no segments or blocks
    check_data_dir(
        &fixture,
        "truncate_after_purge_check_file_items",
        1,
        0,
        0,
        0,
        0,
        Some(()),
        None,
    )
    .await?;
    Ok(())
}
