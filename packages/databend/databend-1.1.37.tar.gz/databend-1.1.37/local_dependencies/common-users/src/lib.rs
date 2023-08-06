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

#![feature(let_chains)]
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
#![allow(clippy::uninlined_format_args)]

extern crate core;

mod jwt;
mod role_mgr;
mod user;
mod user_api;
mod user_mgr;
mod user_setting;
mod user_stage;
mod user_udf;

pub mod file_format;
pub mod idm_config;
pub mod role_cache_mgr;
pub mod role_util;

pub use jwt::*;
pub use role_cache_mgr::RoleCacheManager;
pub use role_mgr::BUILTIN_ROLE_ACCOUNT_ADMIN;
pub use role_mgr::BUILTIN_ROLE_PUBLIC;
pub use user::CertifiedInfo;
pub use user_api::UserApiProvider;
