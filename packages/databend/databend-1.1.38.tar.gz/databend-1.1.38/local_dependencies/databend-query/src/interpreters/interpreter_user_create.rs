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
use common_meta_app::principal::UserGrantSet;
use common_meta_app::principal::UserInfo;
use common_meta_app::principal::UserQuota;
use common_meta_types::MatchSeq;
use common_sql::plans::CreateUserPlan;
use common_users::UserApiProvider;

use crate::interpreters::Interpreter;
use crate::pipelines::PipelineBuildResult;
use crate::sessions::QueryContext;
use crate::sessions::TableContext;

#[derive(Debug)]
pub struct CreateUserInterpreter {
    ctx: Arc<QueryContext>,
    plan: CreateUserPlan,
}

impl CreateUserInterpreter {
    pub fn try_create(ctx: Arc<QueryContext>, plan: CreateUserPlan) -> Result<Self> {
        Ok(CreateUserInterpreter { ctx, plan })
    }
}

#[async_trait::async_trait]
impl Interpreter for CreateUserInterpreter {
    fn name(&self) -> &str {
        "CreateUserInterpreter"
    }

    #[tracing::instrument(level = "debug", skip(self), fields(ctx.id = self.ctx.get_id().as_str()))]
    #[async_backtrace::framed]
    async fn execute2(&self) -> Result<PipelineBuildResult> {
        let plan = self.plan.clone();
        let tenant = self.ctx.get_tenant();

        let user_mgr = UserApiProvider::instance();
        let users = user_mgr.get_users(&tenant).await?;

        let quota_api = UserApiProvider::instance().get_tenant_quota_api_client(&tenant)?;
        let quota = quota_api.get_quota(MatchSeq::GE(0)).await?.data;
        if quota.max_users != 0 && users.len() >= quota.max_users as usize {
            return Err(ErrorCode::TenantQuotaExceeded(format!(
                "Max users quota exceeded: {}",
                quota.max_users
            )));
        };

        let user_info = UserInfo {
            auth_info: plan.auth_info.clone(),
            name: plan.user.username,
            hostname: plan.user.hostname,
            grants: UserGrantSet::empty(),
            quota: UserQuota::no_limit(),
            option: plan.user_option,
        };
        user_mgr
            .add_user(&tenant, user_info, plan.if_not_exists)
            .await?;

        Ok(PipelineBuildResult::create())
    }
}
