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

use std::fmt;

use common_meta_sled_store::sled;
use common_meta_sled_store::SledBytesError;
use common_meta_sled_store::SledOrderedSerde;
use common_meta_types::anyerror::AnyError;
use common_meta_types::LogId;
use serde::Deserialize;
use serde::Serialize;
use sled::IVec;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum LogMetaKey {
    /// The last purged log id in the log.
    ///
    /// Log entries are purged after being applied to state machine.
    /// Even when all logs are purged the last purged log id has to be stored.
    /// Because raft replication requires logs to be consecutive.
    LastPurged,
}
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, derive_more::TryInto)]
pub enum LogMetaValue {
    LogId(LogId),
}

impl fmt::Display for LogMetaKey {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            LogMetaKey::LastPurged => {
                write!(f, "last-purged")
            }
        }
    }
}

impl SledOrderedSerde for LogMetaKey {
    fn ser(&self) -> Result<IVec, SledBytesError> {
        let i = match self {
            LogMetaKey::LastPurged => 1,
        };

        Ok(IVec::from(&[i]))
    }

    fn de<V: AsRef<[u8]>>(v: V) -> Result<Self, SledBytesError>
    where Self: Sized {
        let slice = v.as_ref();
        if slice[0] == 1 {
            return Ok(LogMetaKey::LastPurged);
        }

        Err(SledBytesError::new(&AnyError::error("invalid key IVec")))
    }
}

pub(crate) mod compat_with_07 {
    use common_meta_sled_store::SledBytesError;
    use common_meta_sled_store::SledSerde;
    use common_meta_types::compat07;
    use openraft::compat::Upgrade;

    use super::LogMetaValue;

    #[derive(Debug, serde::Serialize, serde::Deserialize)]
    pub enum LogMetaValueCompat {
        LogId(compat07::LogId),
    }

    impl Upgrade<LogMetaValue> for LogMetaValueCompat {
        #[rustfmt::skip]
        fn upgrade(self) -> LogMetaValue {
            let Self::LogId(lid) = self;
            LogMetaValue::LogId(lid.upgrade())
        }
    }

    impl SledSerde for LogMetaValue {
        fn de<T: AsRef<[u8]>>(v: T) -> Result<Self, SledBytesError>
        where Self: Sized {
            let s: LogMetaValueCompat = serde_json::from_slice(v.as_ref())?;
            let LogMetaValueCompat::LogId(log_id) = s;
            Ok(LogMetaValue::LogId(log_id.upgrade()))
        }
    }
}
