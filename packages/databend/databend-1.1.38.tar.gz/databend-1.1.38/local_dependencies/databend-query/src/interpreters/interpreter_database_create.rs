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

use common_exception::ErrorCode;
use common_exception::Result;
use common_meta_app::share::ShareGrantObjectPrivilege;
use common_meta_app::share::ShareNameIdent;
use common_meta_types::MatchSeq;
use common_sharing::ShareEndpointManager;
use common_sql::plans::CreateDatabasePlan;
use common_users::UserApiProvider;

use crate::interpreters::Interpreter;
use crate::pipelines::PipelineBuildResult;
use crate::sessions::QueryContext;
use crate::sessions::TableContext;

#[derive(Debug)]
pub struct CreateDatabaseInterpreter {
    ctx: Arc<QueryContext>,
    plan: CreateDatabasePlan,
}

impl CreateDatabaseInterpreter {
    pub fn try_create(ctx: Arc<QueryContext>, plan: CreateDatabasePlan) -> Result<Self> {
        Ok(CreateDatabaseInterpreter { ctx, plan })
    }

    async fn check_create_database_from_share(
        &self,
        tenant: &String,
        share_name: &ShareNameIdent,
    ) -> Result<()> {
        let share_specs = ShareEndpointManager::instance()
            .get_inbound_shares(
                tenant,
                Some(share_name.tenant.clone()),
                Some(share_name.clone()),
            )
            .await?;
        match share_specs.get(0) {
            Some((_, share_spec)) => {
                if !share_spec.tenants.contains(tenant) {
                    return Err(ErrorCode::UnknownShareAccounts(format!(
                        "share {} has not granted privilege to {}",
                        share_name, tenant
                    )));
                }
                match share_spec.db_privileges {
                    Some(db_privileges) => {
                        if !db_privileges.contains(ShareGrantObjectPrivilege::Usage) {
                            return Err(ErrorCode::ShareHasNoGrantedPrivilege(format!(
                                "share {} has not granted privilege to {}",
                                share_name, tenant
                            )));
                        }
                    }
                    None => {
                        return Err(ErrorCode::ShareHasNoGrantedPrivilege(format!(
                            "share {} has not granted privilege to {}",
                            share_name, tenant
                        )));
                    }
                }
            }
            None => {
                return Err(ErrorCode::UnknownShare(format!(
                    "UnknownShare {:?}",
                    share_name
                )));
            }
        }
        Ok(())
    }
}

#[async_trait::async_trait]
impl Interpreter for CreateDatabaseInterpreter {
    fn name(&self) -> &str {
        "CreateDatabaseInterpreter"
    }

    #[tracing::instrument(level = "debug", skip(self), fields(ctx.id = self.ctx.get_id().as_str()))]
    #[async_backtrace::framed]
    async fn execute2(&self) -> Result<PipelineBuildResult> {
        let tenant = self.plan.tenant.clone();
        let quota_api = UserApiProvider::instance().get_tenant_quota_api_client(&tenant)?;
        let quota = quota_api.get_quota(MatchSeq::GE(0)).await?.data;
        let catalog = self.ctx.get_catalog(&self.plan.catalog)?;
        let databases = catalog.list_databases(&tenant).await?;
        if quota.max_databases != 0 && databases.len() >= quota.max_databases as usize {
            return Err(ErrorCode::TenantQuotaExceeded(format!(
                "Max databases quota exceeded {}",
                quota.max_databases
            )));
        };
        // if create from other tenant, check from share endpoint
        if let Some(ref share_name) = self.plan.meta.from_share {
            self.check_create_database_from_share(&tenant, share_name)
                .await?;
        }
        catalog.create_database(self.plan.clone().into()).await?;

        Ok(PipelineBuildResult::create())
    }
}
