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
use common_expression::types::StringType;
use common_expression::DataBlock;
use common_expression::DataSchemaRef;
use common_expression::FromData;
use common_meta_api::ShareApi;
use common_meta_app::share::GetObjectGrantPrivilegesReq;
use common_users::UserApiProvider;

use crate::interpreters::Interpreter;
use crate::pipelines::PipelineBuildResult;
use crate::sessions::QueryContext;
use crate::sessions::TableContext;
use crate::sql::plans::share::ShowObjectGrantPrivilegesPlan;

pub struct ShowObjectGrantPrivilegesInterpreter {
    ctx: Arc<QueryContext>,
    plan: ShowObjectGrantPrivilegesPlan,
}

impl ShowObjectGrantPrivilegesInterpreter {
    pub fn try_create(ctx: Arc<QueryContext>, plan: ShowObjectGrantPrivilegesPlan) -> Result<Self> {
        Ok(ShowObjectGrantPrivilegesInterpreter { ctx, plan })
    }
}

#[async_trait::async_trait]
impl Interpreter for ShowObjectGrantPrivilegesInterpreter {
    fn name(&self) -> &str {
        "ShowObjectGrantPrivilegesInterpreter"
    }

    fn schema(&self) -> DataSchemaRef {
        self.plan.schema()
    }

    #[async_backtrace::framed]
    async fn execute2(&self) -> Result<PipelineBuildResult> {
        let meta_api = UserApiProvider::instance().get_meta_store_client();
        let req = GetObjectGrantPrivilegesReq {
            tenant: self.ctx.get_tenant(),
            object: self.plan.object.clone(),
        };
        let resp = meta_api.get_grant_privileges_of_object(req).await?;
        if resp.privileges.is_empty() {
            return Ok(PipelineBuildResult::create());
        }
        let mut share_names: Vec<Vec<u8>> = vec![];
        let mut privileges: Vec<Vec<u8>> = vec![];
        let mut created_owns: Vec<Vec<u8>> = vec![];

        for privilege in resp.privileges {
            share_names.push(privilege.share_name.as_bytes().to_vec());
            privileges.push(privilege.privileges.to_string().as_bytes().to_vec());
            created_owns.push(privilege.grant_on.to_string().as_bytes().to_vec());
        }

        PipelineBuildResult::from_blocks(vec![DataBlock::new_from_columns(vec![
            StringType::from_data(created_owns),
            StringType::from_data(privileges),
            StringType::from_data(share_names),
        ])])
    }
}
