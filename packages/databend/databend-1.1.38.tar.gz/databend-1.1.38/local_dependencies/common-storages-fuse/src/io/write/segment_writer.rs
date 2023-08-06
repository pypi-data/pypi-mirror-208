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

use common_exception::Result;
use opendal::Operator;
use storages_common_table_meta::meta::Location;
use storages_common_table_meta::meta::SegmentInfo;
use storages_common_table_meta::meta::Versioned;

use super::meta_writer::MetaWriter;
use crate::io::CachedMetaWriter;
use crate::io::TableMetaLocationGenerator;

#[derive(Clone)]
pub struct SegmentWriter<'a> {
    location_generator: &'a TableMetaLocationGenerator,
    data_accessor: &'a Operator,
}

impl<'a> SegmentWriter<'a> {
    pub fn new(
        data_accessor: &'a Operator,
        location_generator: &'a TableMetaLocationGenerator,
    ) -> Self {
        Self {
            location_generator,
            data_accessor,
        }
    }

    #[async_backtrace::framed]
    pub async fn write_segment(&self, segment: SegmentInfo) -> Result<Location> {
        let location = self.generate_location();
        segment
            .write_meta_through_cache(self.data_accessor, &location.0)
            .await?;
        Ok(location)
    }

    #[async_backtrace::framed]
    pub async fn write_segment_no_cache(&self, segment: &SegmentInfo) -> Result<Location> {
        let location = self.generate_location();
        segment
            .write_meta(self.data_accessor, location.0.as_str())
            .await?;
        Ok(location)
    }

    fn generate_location(&self) -> Location {
        let path = self.location_generator.gen_segment_info_location();
        (path, SegmentInfo::VERSION)
    }
}
