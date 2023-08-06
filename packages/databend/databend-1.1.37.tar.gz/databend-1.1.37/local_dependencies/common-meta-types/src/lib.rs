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

#![allow(clippy::uninlined_format_args)]
#![feature(provide_any)]
#![feature(no_sanitize)]

//! This crate defines data types used in meta data storage service.

mod applied_state;
mod change;
mod cluster;
mod cmd;
pub mod config;
mod endpoint;
pub mod errors;
mod grpc_config;
mod log_entry;
mod match_seq;
mod message;
mod operation;
mod raft_txid;
mod raft_types;
mod seq_errors;
mod seq_num;
mod seq_value;
mod with;

mod proto_display;

// reexport

pub use anyerror;

// ProtoBuf generated files.
#[allow(clippy::all)]
pub mod protobuf {
    tonic::include_proto!("meta");

    pub const FILE_DESCRIPTOR_SET: &[u8] = tonic::include_file_descriptor_set!("meta_descriptor");
}
pub use applied_state::AppliedState;
pub use change::Change;
pub use cluster::Node;
pub use cluster::NodeInfo;
pub use cmd::Cmd;
pub use cmd::UpsertKV;
pub use endpoint::Endpoint;
pub use errors::meta_api_errors::MetaAPIError;
pub use errors::meta_api_errors::MetaDataError;
pub use errors::meta_api_errors::MetaDataReadError;
pub use errors::meta_api_errors::MetaOperationError;
pub use errors::meta_client_errors::MetaClientError;
pub use errors::meta_errors::MetaError;
pub use errors::meta_handshake_errors::MetaHandshakeError;
pub use errors::meta_management_error::MetaManagementError;
pub use errors::meta_network_errors::ConnectionError;
pub use errors::meta_network_errors::InvalidArgument;
pub use errors::meta_network_errors::InvalidReply;
pub use errors::meta_network_errors::MetaNetworkError;
pub use errors::meta_network_errors::MetaNetworkResult;
pub use errors::meta_startup_errors::MetaStartupError;
pub use errors::rpc_errors::ForwardRPCError;
pub use grpc_config::GrpcConfig;
pub use log_entry::LogEntry;
pub use match_seq::MatchSeq;
pub use match_seq::MatchSeqExt;
pub use operation::GCDroppedDataReply;
pub use operation::GCDroppedDataReq;
pub use operation::MetaId;
pub use operation::Operation;
pub use protobuf::txn_condition;
pub use protobuf::txn_condition::ConditionResult;
pub use protobuf::txn_op;
pub use protobuf::txn_op_response;
pub use protobuf::TxnCondition;
pub use protobuf::TxnDeleteByPrefixRequest;
pub use protobuf::TxnDeleteByPrefixResponse;
pub use protobuf::TxnDeleteRequest;
pub use protobuf::TxnDeleteResponse;
pub use protobuf::TxnGetRequest;
pub use protobuf::TxnGetResponse;
pub use protobuf::TxnOp;
pub use protobuf::TxnOpResponse;
pub use protobuf::TxnPutRequest;
pub use protobuf::TxnPutResponse;
pub use protobuf::TxnReply;
pub use protobuf::TxnRequest;
pub use raft_txid::RaftTxId;
pub use seq_errors::ConflictSeq;
pub use seq_num::SeqNum;
pub use seq_value::IntoSeqV;
pub use seq_value::KVMeta;
pub use seq_value::SeqV;
pub use with::With;

pub use crate::raft_types::compat07;
pub use crate::raft_types::new_log_id;
pub use crate::raft_types::AppendEntriesRequest;
pub use crate::raft_types::AppendEntriesResponse;
pub use crate::raft_types::ChangeMembershipError;
pub use crate::raft_types::ClientWriteError;
pub use crate::raft_types::CommittedLeaderId;
pub use crate::raft_types::Entry;
pub use crate::raft_types::EntryPayload;
pub use crate::raft_types::ErrorSubject;
pub use crate::raft_types::Fatal;
pub use crate::raft_types::ForwardToLeader;
pub use crate::raft_types::InstallSnapshotError;
pub use crate::raft_types::InstallSnapshotRequest;
pub use crate::raft_types::InstallSnapshotResponse;
pub use crate::raft_types::LogId;
pub use crate::raft_types::LogIndex;
pub use crate::raft_types::Membership;
pub use crate::raft_types::MembershipNode;
pub use crate::raft_types::NetworkError;
pub use crate::raft_types::NodeId;
pub use crate::raft_types::RPCError;
pub use crate::raft_types::RaftError;
pub use crate::raft_types::RaftMetrics;
pub use crate::raft_types::Snapshot;
pub use crate::raft_types::SnapshotData;
pub use crate::raft_types::SnapshotMeta;
pub use crate::raft_types::StorageError;
pub use crate::raft_types::StorageIOError;
pub use crate::raft_types::StoredMembership;
pub use crate::raft_types::Term;
pub use crate::raft_types::TypeConfig;
pub use crate::raft_types::Vote;
pub use crate::raft_types::VoteRequest;
pub use crate::raft_types::VoteResponse;
// pub use crate::raft_types::InitializeError;
// pub use crate::raft_types::RaftChangeMembershipError;
// pub use crate::raft_types::RaftWriteError;

impl TxnCondition {
    /// Create a txn condition that checks if the `seq` matches.
    pub fn eq_seq(key: impl ToString, seq: u64) -> Self {
        Self {
            key: key.to_string(),
            expected: ConditionResult::Eq as i32,
            target: Some(txn_condition::Target::Seq(seq)),
        }
    }
}

impl TxnOp {
    /// Create a txn operation that puts a record.
    pub fn put(key: impl ToString, value: Vec<u8>) -> TxnOp {
        Self::put_with_expire(key, value, None)
    }

    /// Create a txn operation that puts a record with expiration time.
    pub fn put_with_expire(key: impl ToString, value: Vec<u8>, expire_at: Option<u64>) -> TxnOp {
        TxnOp {
            request: Some(txn_op::Request::Put(TxnPutRequest {
                key: key.to_string(),
                value,
                prev_value: true,
                expire_at,
            })),
        }
    }

    /// Create a new `TxnOp` with a `Delete` operation.
    pub fn delete(key: impl ToString) -> Self {
        Self::delete_exact(key, None)
    }

    /// Create a new `TxnOp` with a `Delete` operation that will be executed only when the `seq` matches.
    pub fn delete_exact(key: impl ToString, seq: Option<u64>) -> Self {
        TxnOp {
            request: Some(txn_op::Request::Delete(TxnDeleteRequest {
                key: key.to_string(),
                prev_value: true,
                match_seq: seq,
            })),
        }
    }
}

impl TxnOpResponse {
    /// Create a new `TxnOpResponse` of a `Delete` operation.
    pub fn delete(key: impl ToString, success: bool, prev_value: Option<protobuf::SeqV>) -> Self {
        TxnOpResponse {
            response: Some(txn_op_response::Response::Delete(TxnDeleteResponse {
                key: key.to_string(),
                success,
                prev_value,
            })),
        }
    }

    /// Create a new `TxnOpResponse` of a `Put` operation.
    pub fn put(key: impl ToString, prev_value: Option<protobuf::SeqV>) -> Self {
        TxnOpResponse {
            response: Some(txn_op_response::Response::Put(TxnPutResponse {
                key: key.to_string(),
                prev_value,
            })),
        }
    }
}
