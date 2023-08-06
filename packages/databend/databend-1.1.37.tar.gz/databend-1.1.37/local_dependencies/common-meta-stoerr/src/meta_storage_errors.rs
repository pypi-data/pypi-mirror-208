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

use anyerror::AnyError;
use serde::Deserialize;
use serde::Serialize;
use sled::transaction::UnabortableTransactionError;

use crate::MetaBytesError;

/// Storage level error that is raised by meta service.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, thiserror::Error)]
pub enum MetaStorageError {
    /// An error raised when encode/decode data to/from underlying storage.
    #[error(transparent)]
    BytesError(MetaBytesError),

    /// An AnyError built from sled::Error.
    #[error(transparent)]
    SledError(AnyError),

    /// Error that is related to snapshot
    #[error(transparent)]
    SnapshotError(AnyError),

    /// An internal error that inform txn to retry.
    #[error("Conflict when execute transaction, just retry")]
    TransactionConflict,
}

impl From<std::string::FromUtf8Error> for MetaStorageError {
    fn from(error: std::string::FromUtf8Error) -> Self {
        MetaStorageError::BytesError(MetaBytesError::new(&error))
    }
}

impl From<serde_json::Error> for MetaStorageError {
    fn from(error: serde_json::Error) -> MetaStorageError {
        MetaStorageError::BytesError(MetaBytesError::new(&error))
    }
}

impl From<sled::Error> for MetaStorageError {
    fn from(e: sled::Error) -> MetaStorageError {
        MetaStorageError::SledError(AnyError::new(&e))
    }
}

impl From<UnabortableTransactionError> for MetaStorageError {
    fn from(error: UnabortableTransactionError) -> Self {
        match error {
            UnabortableTransactionError::Storage(e) => {
                MetaStorageError::SledError(AnyError::new(&e))
            }
            UnabortableTransactionError::Conflict => MetaStorageError::TransactionConflict,
        }
    }
}
