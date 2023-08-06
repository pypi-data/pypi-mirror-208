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

use std::any::Any;

use common_expression::BlockMetaInfo;
use common_expression::BlockMetaInfoDowncast;
use common_expression::BlockMetaInfoPtr;
use storages_common_table_meta::meta::ClusterStatistics;

use crate::operations::merge_into::mutation_meta::BlockMetaIndex;

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug, PartialEq)]
pub struct SerializeDataMeta {
    pub index: BlockMetaIndex,
    pub cluster_stats: Option<ClusterStatistics>,
}

#[typetag::serde(name = "serialize_data_meta")]
impl BlockMetaInfo for SerializeDataMeta {
    fn as_any(&self) -> &dyn Any {
        self
    }

    fn equals(&self, info: &Box<dyn BlockMetaInfo>) -> bool {
        match SerializeDataMeta::downcast_ref_from(info) {
            None => false,
            Some(other) => self == other,
        }
    }

    fn clone_self(&self) -> Box<dyn BlockMetaInfo> {
        Box::new(self.clone())
    }
}

impl SerializeDataMeta {
    pub fn create(
        index: BlockMetaIndex,
        cluster_stats: Option<ClusterStatistics>,
    ) -> BlockMetaInfoPtr {
        Box::new(SerializeDataMeta {
            index,
            cluster_stats,
        })
    }
}
