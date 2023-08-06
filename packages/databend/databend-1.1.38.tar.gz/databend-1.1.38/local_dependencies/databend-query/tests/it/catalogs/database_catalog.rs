// Copyright 2022 Datafuse Labs.
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

use chrono::Utc;
use common_base::base::tokio;
use common_exception::Result;
use common_expression::types::NumberDataType;
use common_expression::TableDataType;
use common_expression::TableField;
use common_expression::TableSchema;
use common_meta_app::schema::CreateDatabaseReq;
use common_meta_app::schema::CreateTableReq;
use common_meta_app::schema::DatabaseMeta;
use common_meta_app::schema::DatabaseNameIdent;
use common_meta_app::schema::DropDatabaseReq;
use common_meta_app::schema::DropTableByIdReq;
use common_meta_app::schema::RenameDatabaseReq;
use common_meta_app::schema::TableMeta;
use common_meta_app::schema::TableNameIdent;
use databend_query::catalogs::Catalog;

use crate::tests::create_catalog;

#[tokio::test(flavor = "multi_thread", worker_threads = 1)]
async fn test_catalogs_get_database() -> Result<()> {
    let tenant = "test";
    let catalog = create_catalog().await?;

    // get system database
    let database = catalog.get_database(tenant, "system").await?;
    assert_eq!(database.name(), "system");

    let db_list = catalog.list_databases(tenant).await?;
    assert_eq!(db_list.len(), 3);

    // get default database
    let db_2 = catalog.get_database(tenant, "default").await?;
    assert_eq!(db_2.name(), "default");

    // get non-exist database
    let db_3 = catalog.get_database("test", "test").await;
    assert!(db_3.is_err());

    // tenant is empty.
    let res = catalog.get_database("", "system").await;
    assert!(res.is_err());

    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 1)]
async fn test_catalogs_database() -> Result<()> {
    let tenant = "admin";
    let catalog = create_catalog().await?;

    let db_list = catalog.list_databases(tenant).await?;
    let db_count = db_list.len();

    // Create.
    {
        let mut req = CreateDatabaseReq {
            if_not_exists: false,
            name_ident: DatabaseNameIdent {
                tenant: tenant.to_string(),
                db_name: "db1".to_string(),
            },
            meta: DatabaseMeta {
                engine: "".to_string(),
                ..Default::default()
            },
        };
        let res = catalog.create_database(req.clone()).await;
        assert!(res.is_ok());

        let db_list_1 = catalog.list_databases(tenant).await?;
        assert_eq!(db_list_1.len(), db_count + 1);

        // Tenant empty.
        req.name_ident.tenant = "".to_string();
        let res = catalog.create_database(req).await;
        assert!(res.is_err());
    }

    // Rename.
    {
        let mut req = RenameDatabaseReq {
            if_exists: false,
            name_ident: DatabaseNameIdent {
                tenant: tenant.to_string(),
                db_name: "db1".to_string(),
            },
            new_db_name: "db2".to_string(),
        };
        let res = catalog.rename_database(req.clone()).await;
        assert!(res.is_ok());

        let db_list_1 = catalog.list_databases(tenant).await?;
        assert_eq!(db_list_1.len(), db_count + 1);

        // Tenant empty.
        req.name_ident.tenant = "".to_string();
        let res = catalog.rename_database(req).await;
        assert!(res.is_err());
    }

    // Drop old db.
    {
        let req = DropDatabaseReq {
            if_exists: false,
            name_ident: DatabaseNameIdent {
                tenant: tenant.to_string(),
                db_name: "db1".to_string(),
            },
        };
        let res = catalog.drop_database(req.clone()).await;
        assert!(res.is_err());
    }

    // Drop renamed db.
    {
        let mut req = DropDatabaseReq {
            if_exists: false,
            name_ident: DatabaseNameIdent {
                tenant: tenant.to_string(),
                db_name: "db2".to_string(),
            },
        };
        let res = catalog.drop_database(req.clone()).await;
        assert!(res.is_ok());

        let db_list_drop = catalog.list_databases(tenant).await?;
        assert_eq!(db_list_drop.len(), db_count);

        // Tenant empty.
        req.name_ident.tenant = "".to_string();
        let res = catalog.drop_database(req).await;
        assert!(res.is_err());
    }

    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 1)]
async fn test_catalogs_table() -> Result<()> {
    let tenant = "test";
    let catalog = create_catalog().await?;

    // Check system/default.
    {
        let table_list = catalog.list_tables(tenant, "system").await?;
        assert!(!table_list.is_empty());

        let table_list_1 = catalog.list_tables(tenant, "default").await?;
        assert!(table_list_1.is_empty());
    }

    // Create.
    {
        // Table schema with metadata(due to serde issue).
        let schema = Arc::new(TableSchema::new(vec![TableField::new(
            "number",
            TableDataType::Number(NumberDataType::UInt64),
        )]));

        let options = maplit::btreemap! {"opt‐1".into() => "val-1".into()};
        let created_on = Utc::now();

        let mut req = CreateTableReq {
            if_not_exists: false,
            name_ident: TableNameIdent {
                tenant: tenant.to_string(),
                db_name: "default".to_string(),
                table_name: "test_table".to_string(),
            },
            table_meta: TableMeta {
                schema: schema.clone(),
                engine: "MEMORY".to_string(),
                options: options.clone(),
                created_on,
                ..TableMeta::default()
            },
        };
        let res = catalog.create_table(req.clone()).await;
        assert!(res.is_ok());

        // list tables
        let table_list_3 = catalog.list_tables(tenant, "default").await?;
        assert_eq!(table_list_3.len(), 1);
        let table = catalog.get_table(tenant, "default", "test_table").await?;
        assert_eq!(table.name(), "test_table");
        let table = catalog.get_table_by_info(table.get_table_info())?;
        assert_eq!(table.name(), "test_table");

        // Tenant empty.
        req.name_ident.tenant = "".to_string();
        let res = catalog.create_table(req.clone()).await;
        assert!(res.is_err());
    }

    // Drop.
    {
        let tbl = catalog.get_table(tenant, "default", "test_table").await?;
        let res = catalog
            .drop_table_by_id(DropTableByIdReq {
                if_exists: false,
                tb_id: tbl.get_table_info().ident.table_id,
            })
            .await;
        assert!(res.is_ok());
        let table_list_4 = catalog.list_tables(tenant, "default").await?;
        assert!(table_list_4.is_empty());
    }

    Ok(())
}
