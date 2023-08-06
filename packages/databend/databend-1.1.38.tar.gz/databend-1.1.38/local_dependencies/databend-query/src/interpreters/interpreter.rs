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
use std::time::SystemTime;

use common_catalog::table_context::TableContext;
use common_exception::ErrorCode;
use common_exception::Result;
use common_expression::DataSchemaRef;
use common_expression::DataSchemaRefExt;
use common_expression::SendableDataBlockStream;

use crate::interpreters::InterpreterMetrics;
use crate::interpreters::InterpreterQueryLog;
use crate::pipelines::executor::ExecutorSettings;
use crate::pipelines::executor::PipelineCompleteExecutor;
use crate::pipelines::executor::PipelinePullingExecutor;
use crate::pipelines::PipelineBuildResult;
use crate::pipelines::SourcePipeBuilder;
use crate::sessions::QueryContext;
use crate::sessions::SessionManager;
use crate::stream::DataBlockStream;
use crate::stream::ProgressStream;
use crate::stream::PullingExecutorStream;

#[async_trait::async_trait]
/// Interpreter is a trait for different PlanNode
/// Each type of planNode has its own corresponding interpreter
pub trait Interpreter: Sync + Send {
    /// Return the name of Interpreter, such as "CreateDatabaseInterpreter"
    fn name(&self) -> &str;

    /// Return the schema of Interpreter
    fn schema(&self) -> DataSchemaRef {
        DataSchemaRefExt::create(vec![])
    }

    /// The core of the databend processor which will execute the logical plan and get the DataBlock
    #[async_backtrace::framed]
    async fn execute(&self, ctx: Arc<QueryContext>) -> Result<SendableDataBlockStream> {
        InterpreterMetrics::record_query_start(&ctx);
        log_query_start(&ctx);

        if let Err(err) = ctx.check_aborting() {
            log_query_finished(&ctx, Some(err.clone()));
            return Err(err);
        }

        let mut build_res = match self.execute2().await {
            Ok(build_res) => build_res,
            Err(build_error) => {
                InterpreterMetrics::record_query_error(&ctx);
                log_query_finished(&ctx, Some(build_error.clone()));
                return Err(build_error);
            }
        };

        if build_res.main_pipeline.is_empty() {
            InterpreterMetrics::record_query_finished(&ctx, None);
            log_query_finished(&ctx, None);

            return Ok(Box::pin(DataBlockStream::create(None, vec![])));
        }

        let query_ctx = ctx.clone();
        build_res.main_pipeline.set_on_finished(move |may_error| {
            InterpreterMetrics::record_query_finished(&query_ctx, may_error.clone());
            log_query_finished(&query_ctx, may_error.clone());

            match may_error {
                None => Ok(()),
                Some(error) => Err(error.clone()),
            }
        });

        let settings = ctx.get_settings();
        let query_id = ctx.get_id();
        build_res.set_max_threads(settings.get_max_threads()? as usize);
        let settings = ExecutorSettings::try_create(&settings, query_id)?;

        if build_res.main_pipeline.is_complete_pipeline()? {
            let mut pipelines = build_res.sources_pipelines;
            pipelines.push(build_res.main_pipeline);

            let complete_executor = PipelineCompleteExecutor::from_pipelines(pipelines, settings)?;

            ctx.set_executor(complete_executor.get_inner())?;
            complete_executor.execute()?;
            Ok(Box::pin(DataBlockStream::create(None, vec![])))
        } else {
            let pulling_executor = PipelinePullingExecutor::from_pipelines(build_res, settings)?;

            ctx.set_executor(pulling_executor.get_inner())?;
            Ok(Box::pin(ProgressStream::try_create(
                Box::pin(PullingExecutorStream::create(pulling_executor)?),
                ctx.get_result_progress(),
            )?))
        }
    }

    /// The core of the databend processor which will execute the logical plan and build the pipeline
    async fn execute2(&self) -> Result<PipelineBuildResult>;

    fn set_source_pipe_builder(&self, _builder: Option<SourcePipeBuilder>) -> Result<()> {
        Err(ErrorCode::Unimplemented(format!(
            "UnImplement set_source_pipe_builder method for {:?}",
            self.name()
        )))
    }
}

pub type InterpreterPtr = Arc<dyn Interpreter>;

fn log_query_start(ctx: &QueryContext) {
    let now = SystemTime::now();
    let session = ctx.get_current_session();

    if session.get_type().is_user_session() {
        SessionManager::instance().status.write().query_start(now);
    }

    if let Err(error) = InterpreterQueryLog::log_start(ctx, now, None) {
        tracing::error!("interpreter.start.error: {:?}", error)
    }
}

fn log_query_finished(ctx: &QueryContext, error: Option<ErrorCode>) {
    let now = SystemTime::now();
    let session = ctx.get_current_session();

    session.get_status().write().query_finish();
    if session.get_type().is_user_session() {
        SessionManager::instance().status.write().query_finish(now)
    }

    if let Err(error) = InterpreterQueryLog::log_finish(ctx, now, error) {
        tracing::error!("interpreter.finish.error: {:?}", error)
    }
}
