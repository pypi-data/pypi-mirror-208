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

mod cluster;
mod file_format;
mod quota;
mod role;
mod serde;
mod setting;
mod stage;
mod udf;
mod user;

pub use cluster::ClusterApi;
pub use cluster::ClusterMgr;
pub use file_format::FileFormatApi;
pub use file_format::FileFormatMgr;
pub use quota::QuotaApi;
pub use quota::QuotaMgr;
pub use role::RoleApi;
pub use role::RoleMgr;
pub use serde::deserialize_struct;
pub use serde::serialize_struct;
pub use setting::SettingApi;
pub use setting::SettingMgr;
pub use stage::StageApi;
pub use stage::StageMgr;
pub use udf::UdfApi;
pub use udf::UdfMgr;
pub use user::UserApi;
pub use user::UserMgr;
