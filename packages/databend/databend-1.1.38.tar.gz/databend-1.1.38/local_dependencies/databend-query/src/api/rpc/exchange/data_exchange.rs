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

use common_expression::RemoteExpr;

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub enum DataExchange {
    Merge(MergeExchange),
    Broadcast(BroadcastExchange),
    ShuffleDataExchange(ShuffleDataExchange),
}

impl DataExchange {
    pub fn get_destinations(&self) -> Vec<String> {
        match self {
            DataExchange::Merge(exchange) => vec![exchange.destination_id.clone()],
            DataExchange::Broadcast(exchange) => exchange.destination_ids.clone(),
            DataExchange::ShuffleDataExchange(exchange) => exchange.destination_ids.clone(),
        }
    }

    pub fn from_multiple_nodes(&self) -> bool {
        match self {
            DataExchange::Merge(_) => true,
            DataExchange::ShuffleDataExchange(_) => true,
            DataExchange::Broadcast(exchange) => exchange.from_multiple_nodes,
        }
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct ShuffleDataExchange {
    pub destination_ids: Vec<String>,
    pub shuffle_keys: Vec<RemoteExpr>,
}

impl ShuffleDataExchange {
    pub fn create(destination_ids: Vec<String>, shuffle_keys: Vec<RemoteExpr>) -> DataExchange {
        DataExchange::ShuffleDataExchange(ShuffleDataExchange {
            destination_ids,
            shuffle_keys,
        })
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct MergeExchange {
    pub destination_id: String,
}

impl MergeExchange {
    pub fn create(destination_id: String) -> DataExchange {
        DataExchange::Merge(MergeExchange { destination_id })
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct BroadcastExchange {
    pub from_multiple_nodes: bool,
    pub destination_ids: Vec<String>,
}

impl BroadcastExchange {
    pub fn create(from_multiple_nodes: bool, destination_ids: Vec<String>) -> DataExchange {
        DataExchange::Broadcast(BroadcastExchange {
            from_multiple_nodes,
            destination_ids,
        })
    }
}
