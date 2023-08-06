// Copyright 2021 Datafuse Labs.
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
use std::time::Duration;
use std::time::UNIX_EPOCH;

use common_base::base::tokio;
use common_exception::Result;
use common_management::*;
use common_meta_embedded::MetaEmbedded;
use common_meta_kvapi::kvapi::KVApi;
use common_meta_store::MetaStore;
use common_meta_types::MatchSeq;
use common_meta_types::NodeInfo;
use common_meta_types::SeqV;

#[tokio::test(flavor = "multi_thread", worker_threads = 1)]
async fn test_successfully_add_node() -> Result<()> {
    let current_time = current_seconds_time();
    let (kv_api, cluster_api) = new_cluster_api().await?;

    let node_info = create_test_node_info();
    cluster_api.add_node(node_info.clone()).await?;
    let value = kv_api
        .get_kv("__fd_clusters/test%2dtenant%2did/test%2dcluster%2did/databend_query/test_node")
        .await?;

    match value {
        Some(SeqV {
            seq: 1,
            meta,
            data: value,
        }) => {
            assert!(meta.unwrap().expire_at.unwrap() - current_time >= 60);
            assert_eq!(value, serde_json::to_vec(&node_info)?);
        }
        catch => panic!("GetKVActionReply{:?}", catch),
    }

    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 1)]
async fn test_already_exists_add_node() -> Result<()> {
    let (_, cluster_api) = new_cluster_api().await?;

    let node_info = create_test_node_info();
    cluster_api.add_node(node_info.clone()).await?;

    match cluster_api.add_node(node_info.clone()).await {
        Ok(_) => panic!("Already exists add node must be return Err."),
        Err(cause) => assert_eq!(cause.code(), 2402),
    }

    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 1)]
async fn test_successfully_get_nodes() -> Result<()> {
    let (_, cluster_api) = new_cluster_api().await?;

    let nodes = cluster_api.get_nodes().await?;
    assert_eq!(nodes, vec![]);

    let node_info = create_test_node_info();
    cluster_api.add_node(node_info.clone()).await?;

    let nodes = cluster_api.get_nodes().await?;
    assert_eq!(nodes, vec![node_info]);
    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 1)]
async fn test_successfully_drop_node() -> Result<()> {
    let (_, cluster_api) = new_cluster_api().await?;

    let node_info = create_test_node_info();
    cluster_api.add_node(node_info.clone()).await?;

    let nodes = cluster_api.get_nodes().await?;
    assert_eq!(nodes, vec![node_info.clone()]);

    cluster_api.drop_node(node_info.id, MatchSeq::GE(1)).await?;

    let nodes = cluster_api.get_nodes().await?;
    assert_eq!(nodes, vec![]);
    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 1)]
async fn test_unknown_node_drop_node() -> Result<()> {
    let (_, cluster_api) = new_cluster_api().await?;

    match cluster_api
        .drop_node(String::from("UNKNOWN_ID"), MatchSeq::GE(1))
        .await
    {
        Ok(_) => panic!("Unknown node drop node must be return Err."),
        Err(cause) => assert_eq!(cause.code(), 2401),
    }

    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 1)]
async fn test_successfully_heartbeat_node() -> Result<()> {
    let current_time = current_seconds_time();
    let (kv_api, cluster_api) = new_cluster_api().await?;

    let node_info = create_test_node_info();
    cluster_api.add_node(node_info.clone()).await?;

    let value = kv_api
        .get_kv("__fd_clusters/test%2dtenant%2did/test%2dcluster%2did/databend_query/test_node")
        .await?;

    assert!(value.unwrap().meta.unwrap().expire_at.unwrap() - current_time >= 60);

    let current_time = current_seconds_time();
    cluster_api.heartbeat(&node_info, MatchSeq::GE(1)).await?;

    let value = kv_api
        .get_kv("__fd_clusters/test%2dtenant%2did/test%2dcluster%2did/databend_query/test_node")
        .await?;

    assert!(value.unwrap().meta.unwrap().expire_at.unwrap() - current_time >= 60);
    Ok(())
}

fn current_seconds_time() -> u64 {
    let now = std::time::SystemTime::now();
    now.duration_since(UNIX_EPOCH)
        .expect("Time went backwards")
        .as_secs()
}

fn create_test_node_info() -> NodeInfo {
    NodeInfo {
        id: String::from("test_node"),
        cpu_nums: 0,
        version: 0,
        flight_address: String::from("ip:port"),
        binary_version: "binary_version".to_string(),
    }
}

async fn new_cluster_api() -> Result<(MetaStore, ClusterMgr)> {
    let test_api = MetaStore::L(Arc::new(MetaEmbedded::new_temp().await?));
    let cluster_manager = ClusterMgr::create(
        test_api.clone(),
        "test-tenant-id",
        "test-cluster-id",
        Duration::from_secs(60),
    )?;
    Ok((test_api, cluster_manager))
}
