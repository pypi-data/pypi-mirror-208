// Copyright 2022 Datafuse Labs.
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
use std::collections::hash_map::DefaultHasher;
use std::hash::Hash;
use std::hash::Hasher;
use std::io::Write;
use std::sync::Arc;

use common_catalog::plan::PartInfo;
use common_catalog::plan::PartInfoPtr;
use common_catalog::plan::Partitions;
use common_catalog::plan::PartitionsShuffleKind;
use goldenfile::Mint;

#[derive(serde::Serialize, serde::Deserialize, PartialEq, Eq)]
struct TestPartInfo {
    pub loc: String,
}

#[typetag::serde(name = "fuse_lazy")]
impl PartInfo for TestPartInfo {
    fn as_any(&self) -> &dyn Any {
        self
    }

    fn equals(&self, info: &Box<dyn PartInfo>) -> bool {
        match info.as_any().downcast_ref::<TestPartInfo>() {
            None => false,
            Some(other) => self == other,
        }
    }

    fn hash(&self) -> u64 {
        let mut s = DefaultHasher::new();
        self.loc.hash(&mut s);
        s.finish()
    }
}

impl TestPartInfo {
    pub fn create(loc: String) -> PartInfoPtr {
        Arc::new(Box::new(TestPartInfo { loc }))
    }
}

fn gen_parts(kind: PartitionsShuffleKind, size: usize) -> Partitions {
    let mut parts = vec![];
    for i in 0..size {
        parts.push(TestPartInfo::create(format!("{}", i)));
    }

    Partitions::create(kind, parts, true)
}

#[test]
fn test_partition_reshuffle() {
    let mut mint = Mint::new("tests/it/testdata");
    let file = &mut mint.new_goldenfile("partition-reshuffle.txt").unwrap();

    let executors_3 = vec![
        "node-1".to_string(),
        "node-2".to_string(),
        "node-3".to_string(),
    ];

    let executors_2 = vec!["node-1".to_string(), "node-2".to_string()];

    // None.
    {
        let partitions = gen_parts(PartitionsShuffleKind::Seq, 11);
        let shuffle = partitions.reshuffle(executors_3.clone()).unwrap();

        writeln!(
            file,
            "PartitionsShuffleKind::Seq : 11 partitions of 3 executors"
        )
        .unwrap();
        let e1_parts = shuffle.get(&executors_3[0]).unwrap();
        writeln!(file, "{:?}", e1_parts).unwrap();

        let e2_parts = shuffle.get(&executors_3[1]).unwrap();
        writeln!(file, "{:?}", e2_parts).unwrap();

        let e3_parts = shuffle.get(&executors_3[2]).unwrap();
        writeln!(file, "{:?}", e3_parts).unwrap();
    }

    // None.
    {
        let partitions = gen_parts(PartitionsShuffleKind::Seq, 2);
        let shuffle = partitions.reshuffle(executors_3.clone()).unwrap();

        writeln!(
            file,
            "PartitionsShuffleKind::Seq : 2 partitions of 3 executors"
        )
        .unwrap();
        let e1_parts = shuffle.get(&executors_3[0]).unwrap();
        writeln!(file, "{:?}", e1_parts).unwrap();

        let e2_parts = shuffle.get(&executors_3[1]).unwrap();
        writeln!(file, "{:?}", e2_parts).unwrap();

        let e3_parts = shuffle.get(&executors_3[2]).unwrap();
        writeln!(file, "{:?}", e3_parts).unwrap();
    }

    // Mod.
    {
        let partitions = gen_parts(PartitionsShuffleKind::Mod, 11);
        let shuffle = partitions.reshuffle(executors_3.clone()).unwrap();

        writeln!(
            file,
            "PartitionsShuffleKind::Mod : 11 partitions of 3 executors"
        )
        .unwrap();
        let e1_parts = shuffle.get(&executors_3[0]).unwrap();
        writeln!(file, "{:?}", e1_parts).unwrap();

        let e2_parts = shuffle.get(&executors_3[1]).unwrap();
        writeln!(file, "{:?}", e2_parts).unwrap();

        let e3_parts = shuffle.get(&executors_3[2]).unwrap();
        writeln!(file, "{:?}", e3_parts).unwrap();
    }

    // Mod.
    {
        let partitions = gen_parts(PartitionsShuffleKind::Mod, 11);
        let shuffle = partitions.reshuffle(executors_2.clone()).unwrap();

        writeln!(
            file,
            "PartitionsShuffleKind::Mod : 11 partitions of 2 executors"
        )
        .unwrap();
        let e1_parts = shuffle.get(&executors_2[0]).unwrap();
        writeln!(file, "{:?}", e1_parts).unwrap();

        let e2_parts = shuffle.get(&executors_2[1]).unwrap();
        writeln!(file, "{:?}", e2_parts).unwrap();
    }

    // Rand.
    {
        let partitions = gen_parts(PartitionsShuffleKind::Rand, 11);
        let shuffle = partitions.reshuffle(executors_2.clone()).unwrap();

        writeln!(
            file,
            "PartitionsShuffleKind::Rand: 11 partitions of 2 executors"
        )
        .unwrap();
        let e1_parts = shuffle.get(&executors_2[0]).unwrap();
        writeln!(file, "{:?}", e1_parts.len()).unwrap();

        let e2_parts = shuffle.get(&executors_2[1]).unwrap();
        writeln!(file, "{:?}", e2_parts.len()).unwrap();
    }
}
