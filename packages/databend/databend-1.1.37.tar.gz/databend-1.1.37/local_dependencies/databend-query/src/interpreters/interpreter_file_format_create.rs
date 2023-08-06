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
use common_meta_app::principal::UserDefinedFileFormat;
use common_sql::plans::CreateFileFormatPlan;
use common_users::UserApiProvider;

use crate::interpreters::Interpreter;
use crate::pipelines::PipelineBuildResult;
use crate::sessions::QueryContext;
use crate::sessions::TableContext;

#[derive(Debug)]
pub struct CreateFileFormatInterpreter {
    ctx: Arc<QueryContext>,
    plan: CreateFileFormatPlan,
}

impl CreateFileFormatInterpreter {
    pub fn try_create(ctx: Arc<QueryContext>, plan: CreateFileFormatPlan) -> Result<Self> {
        Ok(Self { ctx, plan })
    }
}

#[async_trait::async_trait]
impl Interpreter for CreateFileFormatInterpreter {
    fn name(&self) -> &str {
        "CreateFileFormatInterpreter"
    }

    #[tracing::instrument(level = "info", skip(self), fields(ctx.id = self.ctx.get_id().as_str()))]
    #[async_backtrace::framed]
    async fn execute2(&self) -> Result<PipelineBuildResult> {
        let plan = self.plan.clone();
        let user_mgr = UserApiProvider::instance();
        let user_defined_file_format = UserDefinedFileFormat::new(
            &plan.name,
            plan.file_format_params.clone(),
            self.ctx.get_current_user()?.identity(),
        );

        let tenant = self.ctx.get_tenant();
        let _create_file_format = user_mgr
            .add_file_format(&tenant, user_defined_file_format, plan.if_not_exists)
            .await?;

        Ok(PipelineBuildResult::create())
    }
}
