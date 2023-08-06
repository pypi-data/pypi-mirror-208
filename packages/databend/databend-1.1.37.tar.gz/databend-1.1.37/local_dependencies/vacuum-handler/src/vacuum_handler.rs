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

use chrono::DateTime;
use chrono::Utc;
use common_base::base::GlobalInstance;
use common_catalog::table_context::TableContext;
use common_exception::Result;
use common_storages_fuse::FuseTable;

#[async_trait::async_trait]
pub trait VacuumHandler: Sync + Send {
    async fn do_vacuum(
        &self,
        fuse_table: &FuseTable,
        ctx: Arc<dyn TableContext>,
        retention_time: DateTime<Utc>,
        dry_run_limit: Option<usize>,
    ) -> Result<Option<Vec<String>>>;
}

pub struct VacuumHandlerWrapper {
    handler: Box<dyn VacuumHandler>,
}

impl VacuumHandlerWrapper {
    pub fn new(handler: Box<dyn VacuumHandler>) -> Self {
        Self { handler }
    }

    #[async_backtrace::framed]
    pub async fn do_vacuum(
        &self,
        fuse_table: &FuseTable,
        ctx: Arc<dyn TableContext>,
        retention_time: DateTime<Utc>,
        dry_run_limit: Option<usize>,
    ) -> Result<Option<Vec<String>>> {
        self.handler
            .do_vacuum(fuse_table, ctx, retention_time, dry_run_limit)
            .await
    }
}

pub fn get_vacuum_handler() -> Arc<VacuumHandlerWrapper> {
    GlobalInstance::get()
}
