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

use std::sync::Arc;

use common_expression::DataBlock;
use common_pipeline_core::processors::port::InputPort;
use common_pipeline_core::processors::port::OutputPort;
use common_pipeline_core::processors::processor::ProcessorPtr;
use common_pipeline_transforms::processors::transforms::Transform;
use common_pipeline_transforms::processors::transforms::Transformer;

use crate::api::rpc::exchange::exchange_transform_shuffle::ExchangeShuffleMeta;
use crate::api::rpc::flight_scatter::FlightScatter;

pub struct ScatterTransform {
    scatter: Arc<Box<dyn FlightScatter>>,
}

impl ScatterTransform {
    pub fn create(
        input: Arc<InputPort>,
        output: Arc<OutputPort>,
        scatter: Arc<Box<dyn FlightScatter>>,
    ) -> ProcessorPtr {
        ProcessorPtr::create(Transformer::create(input, output, ScatterTransform {
            scatter,
        }))
    }
}

impl Transform for ScatterTransform {
    const NAME: &'static str = "ScatterTransform";

    fn transform(&mut self, data: DataBlock) -> common_exception::Result<DataBlock> {
        let blocks = self.scatter.execute(data)?;

        Ok(DataBlock::empty_with_meta(ExchangeShuffleMeta::create(
            blocks,
        )))
    }
}
