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

mod aggregator_groups_builder;
mod aggregator_keys_builder;
mod aggregator_keys_iter;
mod aggregator_polymorphic_keys;
mod aggregator_state;
mod aggregator_state_entity;
mod large_number;

pub use aggregator_groups_builder::GroupColumnsBuilder;
pub use aggregator_keys_builder::KeysColumnBuilder;
pub use aggregator_keys_iter::KeysColumnIter;
pub use aggregator_polymorphic_keys::HashMethodBounds;
pub use aggregator_polymorphic_keys::PartitionedHashMethod;
pub use aggregator_polymorphic_keys::PolymorphicKeysHelper;
pub use aggregator_state::Area;
pub use aggregator_state::ArenaHolder;
pub use aggregator_state_entity::StateEntityMutRef;
pub use aggregator_state_entity::StateEntityRef;

pub const BUCKETS_LG2: u32 = 8;
