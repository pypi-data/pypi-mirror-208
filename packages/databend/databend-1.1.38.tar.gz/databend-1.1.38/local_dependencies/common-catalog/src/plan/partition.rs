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
use std::collections::HashMap;
use std::collections::VecDeque;
use std::fmt::Debug;
use std::fmt::Formatter;
use std::sync::Arc;

use common_exception::Result;
use parking_lot::RwLock;
use rand::prelude::SliceRandom;
use rand::thread_rng;
use sha2::Digest;

use crate::table_context::TableContext;

#[typetag::serde(tag = "type")]
pub trait PartInfo: Send + Sync {
    fn as_any(&self) -> &dyn Any;

    #[allow(clippy::borrowed_box)]
    fn equals(&self, info: &Box<dyn PartInfo>) -> bool;

    /// Used for partition distributed.
    fn hash(&self) -> u64;
}

impl Debug for Box<dyn PartInfo> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match serde_json::to_string(self) {
            Ok(str) => write!(f, "{}", str),
            Err(_cause) => Err(std::fmt::Error {}),
        }
    }
}

impl PartialEq for Box<dyn PartInfo> {
    fn eq(&self, other: &Self) -> bool {
        let this_type_id = self.as_any().type_id();
        let other_type_id = other.as_any().type_id();

        match this_type_id == other_type_id {
            true => self.equals(other),
            false => false,
        }
    }
}

#[allow(dead_code)]
pub type PartInfoPtr = Arc<Box<dyn PartInfo>>;

/// For cache affinity, we consider some strategies when reshuffle partitions.
/// For example:
/// Under PartitionsShuffleKind::Mod, the same partition is always routed to the same executor.
#[derive(serde::Serialize, serde::Deserialize, Debug, Clone, PartialEq)]
pub enum PartitionsShuffleKind {
    // Bind the Partition to executor one by one with order.
    Seq,
    // Bind the Partition to executor by partition.hash()%executor_nums order.
    Mod,
    // Bind the Partition to executor by partition.rand() order.
    Rand,
}
#[derive(serde::Serialize, serde::Deserialize, Debug, Clone, PartialEq)]
pub struct Partitions {
    pub kind: PartitionsShuffleKind,
    pub partitions: Vec<PartInfoPtr>,
    pub is_lazy: bool,
}

impl Partitions {
    pub fn create(
        kind: PartitionsShuffleKind,
        partitions: Vec<PartInfoPtr>,
        is_lazy: bool,
    ) -> Self {
        Partitions {
            kind,
            partitions,
            is_lazy,
        }
    }

    pub fn create_nolazy(kind: PartitionsShuffleKind, partitions: Vec<PartInfoPtr>) -> Self {
        Partitions {
            kind,
            partitions,
            is_lazy: false,
        }
    }

    pub fn len(&self) -> usize {
        self.partitions.len()
    }

    pub fn is_empty(&self) -> bool {
        self.partitions.is_empty()
    }

    pub fn reshuffle(&self, executors: Vec<String>) -> Result<HashMap<String, Partitions>> {
        let mut executors_sorted = executors;
        executors_sorted.sort();

        let num_executors = executors_sorted.len();
        let partitions = match self.kind {
            PartitionsShuffleKind::Seq => self.partitions.clone(),
            PartitionsShuffleKind::Mod => {
                // Sort by hash%executor_nums.
                let mut parts = self
                    .partitions
                    .iter()
                    .map(|p| (p.hash() % num_executors as u64, p.clone()))
                    .collect::<Vec<_>>();
                parts.sort_by(|a, b| a.0.cmp(&b.0));
                parts.into_iter().map(|x| x.1).collect()
            }
            PartitionsShuffleKind::Rand => {
                let mut rng = thread_rng();
                let mut parts = self.partitions.clone();
                parts.shuffle(&mut rng);
                parts
            }
        };

        let num_parts = partitions.len();
        let mut executor_part = HashMap::default();
        // the first num_parts % num_executors get parts_per_node parts
        // the remaining get parts_per_node - 1 parts
        let parts_per_node = (num_parts + num_executors - 1) / num_executors;
        for (idx, executor) in executors_sorted.iter().enumerate() {
            let begin = parts_per_node * idx;
            let end = num_parts.min(parts_per_node * (idx + 1));
            let parts = partitions[begin..end].to_vec();
            executor_part.insert(
                executor.clone(),
                Partitions::create(PartitionsShuffleKind::Seq, parts.to_vec(), self.is_lazy),
            );
            if end == num_parts && idx < num_executors - 1 {
                // reach here only when num_executors > num_parts
                executors_sorted[(idx + 1)..].iter().for_each(|executor| {
                    executor_part.insert(
                        executor.clone(),
                        Partitions::create(PartitionsShuffleKind::Seq, vec![], self.is_lazy),
                    );
                });
                break;
            }
        }
        Ok(executor_part)
    }

    pub fn compute_sha256(&self) -> Result<String> {
        let buf = serde_json::to_vec(&self.partitions)?;
        let sha = sha2::Sha256::digest(buf);
        Ok(format!("{:x}", sha))
    }
}

impl Default for Partitions {
    fn default() -> Self {
        Self {
            kind: PartitionsShuffleKind::Seq,
            partitions: vec![],
            is_lazy: false,
        }
    }
}

/// StealablePartitions is used for cache affinity
/// that is, the same partition is always routed to the same executor as possible.
#[derive(Clone)]
pub struct StealablePartitions {
    pub partitions: Arc<RwLock<Vec<VecDeque<PartInfoPtr>>>>,
    pub ctx: Arc<dyn TableContext>,
    // In some cases, we need to disable steal.
    // Such as topk queries, this is suitable that topk will respect all the pagecache and reduce false sharing between threads.
    pub disable_steal: bool,
}

impl StealablePartitions {
    pub fn new(partitions: Vec<VecDeque<PartInfoPtr>>, ctx: Arc<dyn TableContext>) -> Self {
        StealablePartitions {
            partitions: Arc::new(RwLock::new(partitions)),
            ctx,
            disable_steal: false,
        }
    }

    pub fn disable_steal(&mut self) {
        self.disable_steal = true;
    }

    pub fn steal_one(&self, idx: usize) -> Option<PartInfoPtr> {
        let mut partitions = self.partitions.write();
        if partitions.is_empty() {
            return self.ctx.get_partition();
        }

        let idx = if idx >= partitions.len() {
            idx % partitions.len()
        } else {
            idx
        };

        for step in 0..partitions.len() {
            let index = (idx + step) % partitions.len();
            if !partitions[index].is_empty() {
                return partitions[index].pop_front();
            }

            if self.disable_steal {
                break;
            }
        }

        drop(partitions);
        self.ctx.get_partition()
    }

    pub fn steal(&self, idx: usize, max_size: usize) -> Vec<PartInfoPtr> {
        let mut partitions = self.partitions.write();
        if partitions.is_empty() {
            return self.ctx.get_partitions(max_size);
        }

        let idx = if idx >= partitions.len() {
            idx % partitions.len()
        } else {
            idx
        };

        for step in 0..partitions.len() {
            let index = (idx + step) % partitions.len();

            if !partitions[index].is_empty() {
                let ps = &mut partitions[index];
                let size = ps.len().min(max_size);
                return ps.drain(..size).collect();
            }

            if self.disable_steal {
                break;
            }
        }

        drop(partitions);
        self.ctx.get_partitions(max_size)
    }
}
