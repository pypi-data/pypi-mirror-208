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

use std::collections::HashMap;
use std::sync::Arc;

use common_config::InnerConfig;
use common_exception::ErrorCode;
use common_exception::Result;
use common_meta_types::NodeInfo;

use crate::api::rpc::packets::packet::create_client;
use crate::api::rpc::Packet;
use crate::api::FlightAction;

// Run all query fragments of query in the node
#[derive(Clone, Debug, serde::Serialize, serde::Deserialize)]
pub struct ExecutePartialQueryPacket {
    pub query_id: String,
    pub executor: String,
    // We send nodes info for each node. This is a bad choice
    pub executors_info: HashMap<String, Arc<NodeInfo>>,
}

impl ExecutePartialQueryPacket {
    pub fn create(
        query_id: String,
        executor: String,
        executors_info: HashMap<String, Arc<NodeInfo>>,
    ) -> ExecutePartialQueryPacket {
        ExecutePartialQueryPacket {
            query_id,
            executor,
            executors_info,
        }
    }
}

#[async_trait::async_trait]
impl Packet for ExecutePartialQueryPacket {
    #[async_backtrace::framed]
    async fn commit(&self, config: &InnerConfig, timeout: u64) -> Result<()> {
        if !self.executors_info.contains_key(&self.executor) {
            return Err(ErrorCode::ClusterUnknownNode(format!(
                "Not found {} node in cluster",
                &self.executor
            )));
        }

        let executor = &self.executors_info[&self.executor];
        let mut conn = create_client(config, &executor.flight_address).await?;
        let action = FlightAction::ExecutePartialQuery(self.query_id.clone());
        conn.execute_action(action, timeout).await
    }
}
