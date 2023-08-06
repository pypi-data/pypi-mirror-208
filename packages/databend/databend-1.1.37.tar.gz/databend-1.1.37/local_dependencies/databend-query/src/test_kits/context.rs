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
use common_config::DATABEND_COMMIT_VERSION;
use common_exception::Result;
use common_meta_app::principal::AuthInfo;
use common_meta_app::principal::GrantObject;
use common_meta_app::principal::PasswordHashMethod;
use common_meta_app::principal::UserInfo;
use common_meta_app::principal::UserPrivilegeSet;
use common_meta_types::NodeInfo;

use crate::clusters::Cluster;
use crate::clusters::ClusterHelper;
use crate::sessions::QueryContext;
use crate::sessions::QueryContextShared;
use crate::sessions::SessionManager;
use crate::sessions::SessionType;
use crate::sessions::TableContext;
use crate::test_kits::ConfigBuilder;
use crate::test_kits::TestGlobalServices;
use crate::test_kits::TestGuard;

pub async fn create_query_context() -> Result<(TestGuard, Arc<QueryContext>)> {
    create_query_context_with_session(SessionType::Dummy, None).await
}

pub async fn create_query_context_with_session(
    typ: SessionType,
    guard: Option<TestGuard>,
) -> Result<(TestGuard, Arc<QueryContext>)> {
    let guard = match guard {
        None => TestGlobalServices::setup(ConfigBuilder::create().build()).await?,
        Some(g) => g,
    };
    let dummy_session = SessionManager::instance().create_session(typ).await?;

    // Set user with all privileges
    let mut user_info = UserInfo::new("root", "127.0.0.1", AuthInfo::Password {
        hash_method: PasswordHashMethod::Sha256,
        hash_value: Vec::from("pass"),
    });
    user_info.grants.grant_privileges(
        &GrantObject::Global,
        UserPrivilegeSet::available_privileges_on_global(),
    );

    dummy_session.set_authed_user(user_info, None).await?;

    let dummy_query_context = dummy_session.create_query_context().await?;
    dummy_query_context.get_settings().set_max_threads(8)?;
    dummy_query_context
        .get_settings()
        .set_max_memory_usage(16 * 1024 * 1024 * 1024)?;
    Ok((guard, dummy_query_context))
}

pub async fn create_query_context_with_config(
    config: InnerConfig,
    mut current_user: Option<UserInfo>,
) -> Result<(TestGuard, Arc<QueryContext>)> {
    let guard = TestGlobalServices::setup(config).await?;

    let dummy_session = SessionManager::instance()
        .create_session(SessionType::Dummy)
        .await?;

    if current_user.is_none() {
        let mut user_info = UserInfo::new("root", "127.0.0.1", AuthInfo::Password {
            hash_method: PasswordHashMethod::Sha256,
            hash_value: Vec::from("pass"),
        });

        user_info.grants.grant_privileges(
            &GrantObject::Global,
            UserPrivilegeSet::available_privileges_on_global(),
        );

        current_user = Some(user_info);
    }

    dummy_session
        .set_authed_user(current_user.unwrap(), None)
        .await?;
    let dummy_query_context = dummy_session.create_query_context().await?;

    dummy_query_context.get_settings().set_max_threads(8)?;
    Ok((guard, dummy_query_context))
}

#[allow(dead_code)]
pub struct ClusterDescriptor {
    local_node_id: String,
    cluster_nodes_list: Vec<Arc<NodeInfo>>,
}

#[allow(dead_code)]
impl ClusterDescriptor {
    pub fn new() -> ClusterDescriptor {
        ClusterDescriptor {
            local_node_id: String::from(""),
            cluster_nodes_list: vec![],
        }
    }

    pub fn with_node(self, id: impl Into<String>, addr: impl Into<String>) -> ClusterDescriptor {
        let mut new_nodes = self.cluster_nodes_list.clone();
        new_nodes.push(Arc::new(NodeInfo::create(
            id.into(),
            0,
            addr.into(),
            DATABEND_COMMIT_VERSION.to_string(),
        )));
        ClusterDescriptor {
            cluster_nodes_list: new_nodes,
            local_node_id: self.local_node_id,
        }
    }

    pub fn with_local_id(self, id: impl Into<String>) -> ClusterDescriptor {
        ClusterDescriptor {
            local_node_id: id.into(),
            cluster_nodes_list: self.cluster_nodes_list,
        }
    }
}

impl Default for ClusterDescriptor {
    fn default() -> Self {
        Self::new()
    }
}

#[allow(dead_code)]
pub async fn create_query_context_with_cluster(
    desc: ClusterDescriptor,
) -> Result<(TestGuard, Arc<QueryContext>)> {
    let config = ConfigBuilder::create().build();
    let guard = TestGlobalServices::setup(config.clone()).await?;
    let dummy_session = SessionManager::instance()
        .create_session(SessionType::Dummy)
        .await?;
    let local_id = desc.local_node_id;
    let nodes = desc.cluster_nodes_list;

    let dummy_query_context = QueryContext::create_from_shared(QueryContextShared::try_create(
        dummy_session,
        Cluster::create(nodes, local_id),
    )?);

    dummy_query_context.get_settings().set_max_threads(8)?;
    Ok((guard, dummy_query_context))
}
