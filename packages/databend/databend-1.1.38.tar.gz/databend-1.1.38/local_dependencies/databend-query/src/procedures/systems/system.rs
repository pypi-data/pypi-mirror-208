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

use crate::procedures::systems::ClusteringInformationProcedure;
use crate::procedures::systems::FuseBlockProcedure;
use crate::procedures::systems::FuseSegmentProcedure;
use crate::procedures::systems::FuseSnapshotProcedure;
use crate::procedures::systems::SearchTablesProcedure;
use crate::procedures::ProcedureFactory;

pub struct SystemProcedure;

impl SystemProcedure {
    pub fn register(factory: &mut ProcedureFactory) {
        factory.register(
            "system$clustering_information",
            Box::new(ClusteringInformationProcedure::try_create),
        );
        factory.register(
            "system$fuse_snapshot",
            Box::new(FuseSnapshotProcedure::try_create),
        );
        factory.register(
            "system$fuse_segment",
            Box::new(FuseSegmentProcedure::try_create),
        );
        factory.register(
            "system$fuse_block",
            Box::new(FuseBlockProcedure::try_create),
        );
        factory.register(
            "system$search_tables",
            Box::new(SearchTablesProcedure::try_create),
        );
    }
}
