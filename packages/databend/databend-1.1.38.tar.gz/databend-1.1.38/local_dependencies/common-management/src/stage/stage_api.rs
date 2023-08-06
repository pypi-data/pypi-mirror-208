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

use common_exception::Result;
use common_meta_app::principal::StageFile;
use common_meta_app::principal::StageInfo;
use common_meta_types::MatchSeq;
use common_meta_types::SeqV;

#[async_trait::async_trait]
pub trait StageApi: Sync + Send {
    // Add a stage info to /tenant/stage-name.
    async fn add_stage(&self, stage: StageInfo) -> Result<u64>;

    async fn get_stage(&self, name: &str, seq: MatchSeq) -> Result<SeqV<StageInfo>>;

    // Get all the stages for a tenant.
    async fn get_stages(&self) -> Result<Vec<StageInfo>>;

    // Drop the tenant's stage by name.
    async fn drop_stage(&self, name: &str) -> Result<()>;

    async fn add_file(&self, name: &str, file: StageFile) -> Result<u64>;

    async fn list_files(&self, name: &str) -> Result<Vec<StageFile>>;

    async fn remove_files(&self, name: &str, paths: Vec<String>) -> Result<()>;
}
