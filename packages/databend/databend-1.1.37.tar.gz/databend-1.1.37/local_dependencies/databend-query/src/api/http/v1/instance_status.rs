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

use std::time::SystemTime;

use poem::web::Json;
use poem::IntoResponse;
use serde::Deserialize;
use serde::Serialize;

use crate::sessions::SessionManager;

#[derive(Serialize, Deserialize, Eq, PartialEq, Debug)]
pub struct InstanceStatus {
    pub running_queries_count: u64,
    // secs since epoch
    pub last_query_started_at: Option<u64>,
    // secs since epoch
    pub last_query_finished_at: Option<u64>,
    // secs since epoch
    instance_started_at: u64,
}

fn secs_since_epoch(t: SystemTime) -> u64 {
    t.duration_since(SystemTime::UNIX_EPOCH)
        .expect("Time went backwards")
        .as_secs()
}

// lightweight way to get status
// return Status in json
#[poem::handler]
#[async_backtrace::framed]
pub async fn instance_status_handler() -> poem::Result<impl IntoResponse> {
    let session_manager = SessionManager::instance();
    let status = session_manager.get_current_session_status();
    let status = InstanceStatus {
        running_queries_count: status.running_queries_count,
        last_query_started_at: status.last_query_started_at.map(secs_since_epoch),
        last_query_finished_at: status.last_query_finished_at.map(secs_since_epoch),
        instance_started_at: secs_since_epoch(status.instance_started_at),
    };
    Ok(Json(status))
}
