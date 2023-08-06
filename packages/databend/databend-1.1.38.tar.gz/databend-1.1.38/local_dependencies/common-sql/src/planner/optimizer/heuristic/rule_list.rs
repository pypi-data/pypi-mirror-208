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

use crate::optimizer::rule::RulePtr;

#[allow(dead_code)]
// Ordered list of rules, may contain duplicated rules.
pub struct RuleList {
    rules: Vec<RulePtr>,
}

impl RuleList {
    // pub fn create(ids: Vec<RuleID>, metadata: Option<MetadataRef>) -> Result<Self> {
    //     let factory = RuleFactory::create();
    //     let mut rules = vec![];
    //     for id in ids {
    //         rules.push(factory.create_rule(id, metadata.clone())?);
    //     }
    //     Ok(RuleList { rules })
    // }

    // pub fn iter(&self) -> impl Iterator<Item = &RulePtr> {
    //     self.rules.iter()
    // }
}
