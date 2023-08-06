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

use common_meta_sled_store::sled;
use common_meta_sled_store::AsKeySpace;
use common_meta_sled_store::SledTree;
use common_meta_stoerr::MetaStorageError;
use common_meta_types::MetaStartupError;
use common_meta_types::NodeId;
use common_meta_types::Vote;
use tracing::debug;
use tracing::info;

use crate::config::RaftConfig;
use crate::key_spaces::RaftStateKV;
use crate::state::RaftStateKey;
use crate::state::RaftStateValue;

/// Raft state stores everything else other than log and state machine, which includes:
/// id: NodeId,
/// vote:
///      term,
///      node_id,
#[derive(Debug)]
pub struct RaftState {
    pub id: NodeId,

    /// If the instance is opened(true) from an existent state(e.g. load from fs) or created(false).
    is_open: bool,

    /// A sled tree with key space support.
    pub inner: SledTree,
}

pub const TREE_RAFT_STATE: &str = "raft_state";

impl RaftState {
    pub fn is_open(&self) -> bool {
        self.is_open
    }
}

impl RaftState {
    /// Open/create a raft state in a sled db.
    /// 1. If `open` is `Some`,  it tries to open an existent RaftState if there is one.
    /// 2. If `create` is `Some`, it tries to initialize a new RaftState if there is not one.
    /// If none of them is `Some`, it is a programming error and will panic.
    #[tracing::instrument(level = "debug", skip(db,config,open,create), fields(config_id=%config.config_id))]
    pub async fn open_create(
        db: &sled::Db,
        config: &RaftConfig,
        open: Option<()>,
        create: Option<()>,
    ) -> Result<RaftState, MetaStartupError> {
        info!(?config);
        info!("open: {:?}, create: {:?}", open, create);

        let tree_name = config.tree_name(TREE_RAFT_STATE);
        let inner = SledTree::open(db, &tree_name, config.is_sync())?;

        let state = inner.key_space::<RaftStateKV>();
        let curr_id = state.get(&RaftStateKey::Id)?.map(NodeId::from);

        debug!("get curr_id: {:?}", curr_id);

        let (id, is_open) = if let Some(curr_id) = curr_id {
            match (open, create) {
                (Some(_), _) => (curr_id, true),
                (None, Some(_)) => {
                    return Err(MetaStartupError::MetaStoreAlreadyExists(curr_id));
                }
                (None, None) => panic!("no open no create"),
            }
        } else {
            match (open, create) {
                (Some(_), Some(_)) => (config.id, false),
                (Some(_), None) => {
                    return Err(MetaStartupError::MetaStoreNotFound);
                }
                (None, Some(_)) => (config.id, false),
                (None, None) => panic!("no open no create"),
            }
        };

        let rs = RaftState { id, is_open, inner };

        if !rs.is_open() {
            rs.init().await?;
        }

        Ok(rs)
    }

    #[tracing::instrument(level = "debug", skip(self))]
    pub async fn set_node_id(&self, id: NodeId) -> Result<(), MetaStorageError> {
        let state = self.state();
        state
            .insert(&RaftStateKey::Id, &RaftStateValue::NodeId(id))
            .await?;
        Ok(())
    }

    /// Initialize a raft state. The only thing to do is to persist the node id
    /// so that next time opening it the caller knows it is initialized.
    #[tracing::instrument(level = "debug", skip(self))]
    async fn init(&self) -> Result<(), MetaStorageError> {
        self.set_node_id(self.id).await
    }

    pub async fn save_vote(&self, vote: &Vote) -> Result<(), MetaStorageError> {
        let state = self.state();
        state
            .insert(&RaftStateKey::HardState, &RaftStateValue::HardState(*vote))
            .await?;
        Ok(())
    }

    pub fn read_vote(&self) -> Result<Option<Vote>, MetaStorageError> {
        let state = self.state();
        let hs = state.get(&RaftStateKey::HardState)?;
        let hs = hs.map(Vote::from);
        Ok(hs)
    }

    #[tracing::instrument(level = "debug", skip(self))]
    pub async fn write_state_machine_id(&self, id: &(u64, u64)) -> Result<(), MetaStorageError> {
        let state = self.state();
        state
            .insert(
                &RaftStateKey::StateMachineId,
                &RaftStateValue::StateMachineId(*id),
            )
            .await?;
        Ok(())
    }

    #[tracing::instrument(level = "debug", skip(self))]
    pub fn read_state_machine_id(&self) -> Result<(u64, u64), MetaStorageError> {
        let state = self.state();
        let smid = state.get(&RaftStateKey::StateMachineId)?;
        let smid: (u64, u64) = smid.map_or((0, 0), |v| v.into());
        Ok(smid)
    }

    /// Returns a borrowed sled tree key space to store meta of raft log
    pub fn state(&self) -> AsKeySpace<RaftStateKV> {
        self.inner.key_space()
    }
}
