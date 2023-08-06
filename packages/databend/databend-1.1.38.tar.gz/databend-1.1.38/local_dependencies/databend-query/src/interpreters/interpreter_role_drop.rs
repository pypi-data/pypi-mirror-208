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
use common_sql::plans::DropRolePlan;
use common_users::RoleCacheManager;
use common_users::UserApiProvider;

use crate::interpreters::Interpreter;
use crate::pipelines::PipelineBuildResult;
use crate::sessions::QueryContext;
use crate::sessions::TableContext;

#[derive(Debug)]
pub struct DropRoleInterpreter {
    ctx: Arc<QueryContext>,
    plan: DropRolePlan,
}

impl DropRoleInterpreter {
    pub fn try_create(ctx: Arc<QueryContext>, plan: DropRolePlan) -> Result<Self> {
        Ok(DropRoleInterpreter { ctx, plan })
    }
}

#[async_trait::async_trait]
impl Interpreter for DropRoleInterpreter {
    fn name(&self) -> &str {
        "DropRoleInterpreter"
    }

    #[tracing::instrument(level = "debug", skip(self), fields(ctx.id = self.ctx.get_id().as_str()))]
    #[async_backtrace::framed]
    async fn execute2(&self) -> Result<PipelineBuildResult> {
        // TODO: add privilege check about DROP role
        let plan = self.plan.clone();
        let role_name = plan.role_name.clone();
        let tenant = self.ctx.get_tenant();
        UserApiProvider::instance()
            .drop_role(&tenant, plan.role_name, plan.if_exists)
            .await?;

        let session = self.ctx.get_current_session();
        if let Some(current_role) = session.get_current_role() {
            if current_role.name == role_name {
                session.unset_current_role();
            }
        }

        RoleCacheManager::instance().force_reload(&tenant).await?;
        Ok(PipelineBuildResult::create())
    }
}
