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

use common_config::InnerConfig;
use common_exception::Result;
use common_meta_types::NodeInfo;

use crate::api::rpc::flight_actions::InitNodesChannel;
use crate::api::rpc::packets::packet::create_client;
use crate::api::rpc::Packet;
use crate::api::FlightAction;

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct ConnectionInfo {
    pub source: Arc<NodeInfo>,
    pub fragments: Vec<usize>,
}

impl ConnectionInfo {
    pub fn create(source: Arc<NodeInfo>, fragments: Vec<usize>) -> ConnectionInfo {
        ConnectionInfo { source, fragments }
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct InitNodesChannelPacket {
    pub query_id: String,
    pub executor: Arc<NodeInfo>,
    pub fragment_connections_info: Vec<ConnectionInfo>,
    pub statistics_connections_info: Vec<ConnectionInfo>,
}

impl InitNodesChannelPacket {
    pub fn create(
        query_id: String,
        executor: Arc<NodeInfo>,
        fragment_connections_info: Vec<ConnectionInfo>,
        statistics_connections_info: Vec<ConnectionInfo>,
    ) -> InitNodesChannelPacket {
        InitNodesChannelPacket {
            query_id,
            executor,
            fragment_connections_info,
            statistics_connections_info,
        }
    }
}

#[async_trait::async_trait]
impl Packet for InitNodesChannelPacket {
    #[async_backtrace::framed]
    async fn commit(&self, config: &InnerConfig, timeout: u64) -> Result<()> {
        let executor_info = &self.executor;
        let mut conn = create_client(config, &executor_info.flight_address).await?;
        let action = FlightAction::InitNodesChannel(InitNodesChannel {
            init_nodes_channel_packet: self.clone(),
        });
        conn.execute_action(action, timeout).await
    }
}
