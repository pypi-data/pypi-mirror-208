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

//! This mod wraps openraft types that have generics parameter with concrete types.

use std::io::Cursor;

use crate::AppliedState;
use crate::LogEntry;

pub type NodeId = u64;
pub type MembershipNode = openraft::EmptyNode;
pub type LogIndex = u64;
pub type Term = u64;

openraft::declare_raft_types!(
    pub TypeConfig:
        D = LogEntry,
        R = AppliedState,
        NodeId = NodeId,
        Node = MembershipNode,
        Entry = openraft::entry::Entry<TypeConfig>,
        SnapshotData = Cursor<Vec<u8>>
);

pub type CommittedLeaderId = openraft::CommittedLeaderId<NodeId>;
pub type LogId = openraft::LogId<NodeId>;
pub type Vote = openraft::Vote<NodeId>;

pub type Membership = openraft::Membership<NodeId, MembershipNode>;
pub type StoredMembership = openraft::StoredMembership<NodeId, MembershipNode>;

pub type EntryPayload = openraft::EntryPayload<TypeConfig>;
pub type Entry = openraft::Entry<TypeConfig>;

pub type SnapshotMeta = openraft::SnapshotMeta<NodeId, MembershipNode>;
pub type SnapshotData = Cursor<Vec<u8>>;
pub type Snapshot = openraft::Snapshot<TypeConfig>;

pub type RaftMetrics = openraft::RaftMetrics<NodeId, MembershipNode>;

pub type ErrorSubject = openraft::ErrorSubject<NodeId>;

pub type RPCError<E> = openraft::error::RPCError<NodeId, MembershipNode, E>;
pub type RaftError<E = openraft::error::Infallible> = openraft::error::RaftError<NodeId, E>;
pub type NetworkError = openraft::error::NetworkError;

pub type StorageError = openraft::StorageError<NodeId>;
pub type StorageIOError = openraft::StorageIOError<NodeId>;
pub type ForwardToLeader = openraft::error::ForwardToLeader<NodeId, MembershipNode>;
pub type Fatal = openraft::error::Fatal<NodeId>;
pub type ChangeMembershipError = openraft::error::ChangeMembershipError<NodeId>;
pub type ClientWriteError = openraft::error::ClientWriteError<NodeId, MembershipNode>;
pub type InitializeError = openraft::error::InitializeError<NodeId, MembershipNode>;

pub type AppendEntriesRequest = openraft::raft::AppendEntriesRequest<TypeConfig>;
pub type AppendEntriesResponse = openraft::raft::AppendEntriesResponse<NodeId>;
pub type InstallSnapshotRequest = openraft::raft::InstallSnapshotRequest<TypeConfig>;
pub type InstallSnapshotResponse = openraft::raft::InstallSnapshotResponse<NodeId>;
pub type InstallSnapshotError = openraft::error::InstallSnapshotError;
pub type VoteRequest = openraft::raft::VoteRequest<NodeId>;
pub type VoteResponse = openraft::raft::VoteResponse<NodeId>;

pub fn new_log_id(term: u64, node_id: NodeId, index: u64) -> LogId {
    LogId::new(CommittedLeaderId::new(term, node_id), index)
}

/// This mod defines data types that are compatible with openraft v0.7
pub mod compat07 {
    use crate::raft_types::TypeConfig;

    pub type LogId = openraft::compat::compat07::LogId;
    pub type Vote = openraft::compat::compat07::Vote;
    pub type Membership = openraft::compat::compat07::Membership;
    pub type StoredMembership = openraft::compat::compat07::StoredMembership;

    pub type EntryPayload = openraft::compat::compat07::EntryPayload<TypeConfig>;
    pub type Entry = openraft::compat::compat07::Entry<TypeConfig>;

    pub type SnapshotMeta = openraft::compat::compat07::SnapshotMeta;
}
