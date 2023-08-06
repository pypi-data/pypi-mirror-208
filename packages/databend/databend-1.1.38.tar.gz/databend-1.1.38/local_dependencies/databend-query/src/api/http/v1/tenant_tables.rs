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

use chrono::DateTime;
use chrono::Utc;
use common_catalog::catalog::CatalogManager;
use common_catalog::catalog_kind::CATALOG_DEFAULT;
use common_config::GlobalConfig;
use common_exception::Result;
use poem::web::Json;
use poem::web::Path;
use poem::IntoResponse;
use serde::Deserialize;
use serde::Serialize;

#[derive(Serialize, Deserialize, Eq, PartialEq, Debug, Default)]
pub struct TenantTablesResponse {
    pub tables: Vec<TenantTableInfo>,
    pub warnings: Vec<String>,
}

#[derive(Serialize, Deserialize, Eq, PartialEq, Debug, Default)]
pub struct TenantTableInfo {
    pub table: String,
    pub database: String,
    pub engine: String,
    pub created_on: DateTime<Utc>,
    pub updated_on: DateTime<Utc>,
    pub rows: u64,
    pub data_bytes: u64,
    pub compressed_data_bytes: u64,
    pub index_bytes: u64,
}

async fn load_tenant_tables(tenant: &str) -> Result<TenantTablesResponse> {
    let catalog = CatalogManager::instance().get_catalog(CATALOG_DEFAULT)?;
    let databases = catalog.list_databases(tenant).await?;

    let mut table_infos: Vec<TenantTableInfo> = vec![];
    let mut warnings: Vec<String> = vec![];
    for database in databases {
        let tables = match catalog.list_tables(tenant, database.name()).await {
            Ok(v) => v,
            Err(err) => {
                warnings.push(format!(
                    "failed to list tables of database {}.{}: {}",
                    tenant,
                    database.name(),
                    err
                ));
                continue;
            }
        };
        for table in tables {
            let stats = &table.get_table_info().meta.statistics;
            table_infos.push(TenantTableInfo {
                table: table.name().to_string(),
                database: database.name().to_string(),
                engine: table.engine().to_string(),
                created_on: table.get_table_info().meta.created_on,
                updated_on: table.get_table_info().meta.updated_on,
                rows: stats.number_of_rows,
                data_bytes: stats.data_bytes,
                compressed_data_bytes: stats.compressed_data_bytes,
                index_bytes: stats.index_data_bytes,
            });
        }
    }
    Ok(TenantTablesResponse {
        tables: table_infos,
        warnings,
    })
}

// This handler returns the statistics about the tables of a tenant. It's only enabled in management mode.
#[poem::handler]
#[async_backtrace::framed]
pub async fn list_tenant_tables_handler(
    Path(tenant): Path<String>,
) -> poem::Result<impl IntoResponse> {
    let resp = load_tenant_tables(&tenant)
        .await
        .map_err(poem::error::InternalServerError)?;
    Ok(Json(resp))
}

// This handler returns the statistics about the tables of the current tenant.
#[poem::handler]
#[async_backtrace::framed]
pub async fn list_tables_handler() -> poem::Result<impl IntoResponse> {
    let tenant = &GlobalConfig::instance().query.tenant_id;
    if tenant.is_empty() {
        return Ok(Json(TenantTablesResponse {
            tables: vec![],
            warnings: vec![],
        }));
    }

    let resp = load_tenant_tables(tenant)
        .await
        .map_err(poem::error::InternalServerError)?;
    Ok(Json(resp))
}
