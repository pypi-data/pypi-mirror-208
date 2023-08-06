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
use common_meta_app::principal::StageType;
use common_meta_types::MatchSeq;
use common_sql::plans::CreateStagePlan;
use common_users::UserApiProvider;

use crate::interpreters::Interpreter;
use crate::pipelines::PipelineBuildResult;
use crate::sessions::QueryContext;
use crate::sessions::TableContext;

#[derive(Debug)]
pub struct CreateUserStageInterpreter {
    ctx: Arc<QueryContext>,
    plan: CreateStagePlan,
}

impl CreateUserStageInterpreter {
    pub fn try_create(ctx: Arc<QueryContext>, plan: CreateStagePlan) -> Result<Self> {
        Ok(CreateUserStageInterpreter { ctx, plan })
    }
}

#[async_trait::async_trait]
impl Interpreter for CreateUserStageInterpreter {
    fn name(&self) -> &str {
        "CreateUserStageInterpreter"
    }

    #[tracing::instrument(level = "info", skip(self), fields(ctx.id = self.ctx.get_id().as_str()))]
    #[async_backtrace::framed]
    async fn execute2(&self) -> Result<PipelineBuildResult> {
        let plan = self.plan.clone();
        let user_mgr = UserApiProvider::instance();
        let user_stage = plan.stage_info;

        // Check user stage.
        if user_stage.stage_type == StageType::User {
            return Err(ErrorCode::StagePermissionDenied(
                "user stage is not allowed to be created",
            ));
        }

        let quota_api = user_mgr.get_tenant_quota_api_client(&plan.tenant)?;
        let quota = quota_api.get_quota(MatchSeq::GE(0)).await?.data;
        let stages = user_mgr.get_stages(&plan.tenant).await?;
        if quota.max_stages != 0 && stages.len() >= quota.max_stages as usize {
            return Err(ErrorCode::TenantQuotaExceeded(format!(
                "Max stages quota exceeded {}",
                quota.max_stages
            )));
        };

        if user_stage.stage_type != StageType::External {
            let op = self.ctx.get_data_operator()?.operator();
            op.create_dir(&user_stage.stage_prefix()).await?
        }

        let mut user_stage = user_stage;
        user_stage.creator = Some(self.ctx.get_current_user()?.identity());
        let _create_stage = user_mgr
            .add_stage(&plan.tenant, user_stage, plan.if_not_exists)
            .await?;

        Ok(PipelineBuildResult::create())
    }
}
