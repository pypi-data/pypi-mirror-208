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

//! This crate defines data types used in meta data storage service.

use std::fmt::Debug;
use std::fmt::Formatter;

pub type MetaId = u64;

/// An operation that updates a field, delete it, or leave it as is.
#[derive(serde::Serialize, serde::Deserialize, Clone, PartialEq, Eq)]
pub enum Operation<T> {
    Update(T),
    Delete,
    AsIs,
}

impl<T> Debug for Operation<T> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Operation::Update(_) => f.debug_tuple("Update").field(&"[binary]").finish(),
            Operation::Delete => f.debug_tuple("Delete").finish(),
            Operation::AsIs => f.debug_tuple("AsIs").finish(),
        }
    }
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug, PartialEq, Eq)]
pub struct GCDroppedDataReq {
    pub tenant: String,
    // gc at least dropped tables, 0 means donot gc table
    pub table_at_least: u32,
    // gc at most dropped db, 0 means donot gc db
    pub db_at_least: u32,
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug, PartialEq, Eq)]
pub struct GCDroppedDataReply {
    pub gc_table_count: u32,
    pub gc_db_count: u32,
}
