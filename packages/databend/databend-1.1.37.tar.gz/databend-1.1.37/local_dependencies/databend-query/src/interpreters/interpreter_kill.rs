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
use common_sql::plans::KillPlan;

use crate::interpreters::Interpreter;
use crate::pipelines::PipelineBuildResult;
use crate::sessions::QueryContext;

pub struct KillInterpreter {
    ctx: Arc<QueryContext>,
    plan: KillPlan,
}

impl KillInterpreter {
    pub fn try_create(ctx: Arc<QueryContext>, plan: KillPlan) -> Result<Self> {
        Ok(KillInterpreter { ctx, plan })
    }

    #[async_backtrace::framed]
    async fn execute_kill(&self, session_id: &String) -> Result<PipelineBuildResult> {
        match self.ctx.get_session_by_id(session_id) {
            None => Err(ErrorCode::UnknownSession(format!(
                "Not found session id {}",
                session_id
            ))),
            Some(kill_session) if self.plan.kill_connection => {
                kill_session.force_kill_session();
                Ok(PipelineBuildResult::create())
            }
            Some(kill_session) => {
                kill_session.force_kill_query(ErrorCode::AbortedQuery(
                    "Aborted query, because the server is shutting down or the query was killed",
                ));
                Ok(PipelineBuildResult::create())
            }
        }
    }
}

#[async_trait::async_trait]
impl Interpreter for KillInterpreter {
    fn name(&self) -> &str {
        "KillInterpreter"
    }

    #[async_backtrace::framed]
    async fn execute2(&self) -> Result<PipelineBuildResult> {
        let id = &self.plan.id;
        // If press Ctrl + C, MySQL Client will create a new session and send query
        // `kill query mysql_connection_id` to server.
        // the type of connection_id is u32, if parse success get session by connection_id,
        // otherwise use the session_id.
        // More info Link to: https://github.com/datafuselabs/databend/discussions/5405.
        match id.parse::<u32>() {
            Ok(mysql_conn_id) => match self.ctx.get_id_by_mysql_conn_id(&Some(mysql_conn_id)) {
                Some(get) => self.execute_kill(&get).await,
                None => Err(ErrorCode::UnknownSession(format!(
                    "MySQL connection id {} not found session id",
                    mysql_conn_id
                ))),
            },
            Err(_) => self.execute_kill(id).await,
        }
    }
}
