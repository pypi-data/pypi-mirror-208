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
use std::collections::BTreeMap;
use std::fmt::Debug;
use std::fmt::Formatter;

use common_arrow::native::read::reader::NativeReader;
use common_catalog::plan::PartInfoPtr;
use common_expression::BlockMetaInfo;
use common_expression::BlockMetaInfoPtr;
use serde::Deserializer;
use serde::Serializer;

use crate::io::NativeReaderExt;

pub type DataChunks = BTreeMap<usize, Vec<NativeReader<Box<dyn NativeReaderExt>>>>;

pub struct NativeDataSourceMeta {
    pub part: Vec<PartInfoPtr>,
    pub chunks: Vec<DataChunks>,
}

impl NativeDataSourceMeta {
    pub fn create(part: Vec<PartInfoPtr>, chunks: Vec<DataChunks>) -> BlockMetaInfoPtr {
        Box::new(NativeDataSourceMeta { part, chunks })
    }
}

impl Debug for NativeDataSourceMeta {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("NativeDataSourceMeta")
            .field("part", &self.part)
            .finish()
    }
}

impl serde::Serialize for NativeDataSourceMeta {
    fn serialize<S>(&self, _: S) -> common_exception::Result<S::Ok, S::Error>
    where S: Serializer {
        unimplemented!("Unimplemented serialize NativeDataSourceMeta")
    }
}

impl<'de> serde::Deserialize<'de> for NativeDataSourceMeta {
    fn deserialize<D>(_: D) -> common_exception::Result<Self, D::Error>
    where D: Deserializer<'de> {
        unimplemented!("Unimplemented deserialize NativeDataSourceMeta")
    }
}

#[typetag::serde(name = "fuse_data_source")]
impl BlockMetaInfo for NativeDataSourceMeta {
    fn as_any(&self) -> &dyn Any {
        self
    }

    fn equals(&self, _: &Box<dyn BlockMetaInfo>) -> bool {
        unimplemented!("Unimplemented equals NativeDataSourceMeta")
    }

    fn clone_self(&self) -> Box<dyn BlockMetaInfo> {
        unimplemented!("Unimplemented clone NativeDataSourceMeta")
    }
}
