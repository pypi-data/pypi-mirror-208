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

use std::fmt::Debug;
use std::fmt::Formatter;
use std::sync::Arc;

use crate::processors::port::InputPort;
use crate::processors::port::OutputPort;
use crate::processors::processor::ProcessorPtr;

#[derive(Clone)]
pub struct PipeItem {
    pub processor: ProcessorPtr,
    pub inputs_port: Vec<Arc<InputPort>>,
    pub outputs_port: Vec<Arc<OutputPort>>,
}

impl PipeItem {
    pub fn create(
        proc: ProcessorPtr,
        inputs: Vec<Arc<InputPort>>,
        outputs: Vec<Arc<OutputPort>>,
    ) -> PipeItem {
        PipeItem {
            processor: proc,
            inputs_port: inputs,
            outputs_port: outputs,
        }
    }
}

impl Debug for PipeItem {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("PipeItem")
            .field("name", &unsafe { self.processor.name() })
            .field("inputs", &self.inputs_port.len())
            .field("outputs", &self.outputs_port.len())
            .finish()
    }
}

#[derive(Clone)]
pub struct Pipe {
    pub items: Vec<PipeItem>,
    pub input_length: usize,
    pub output_length: usize,
}

impl Debug for Pipe {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:?}", &self.items)
    }
}

impl Pipe {
    pub fn create(inputs: usize, outputs: usize, items: Vec<PipeItem>) -> Pipe {
        Pipe {
            items,
            input_length: inputs,
            output_length: outputs,
        }
    }
}

#[derive(Clone)]
pub struct SourcePipeBuilder {
    items: Vec<PipeItem>,
}

impl SourcePipeBuilder {
    pub fn create() -> SourcePipeBuilder {
        SourcePipeBuilder { items: vec![] }
    }

    pub fn finalize(self) -> Pipe {
        Pipe::create(0, self.items.len(), self.items)
    }

    pub fn add_source(&mut self, output_port: Arc<OutputPort>, source: ProcessorPtr) {
        self.items
            .push(PipeItem::create(source, vec![], vec![output_port]));
    }
}

#[allow(dead_code)]
pub struct SinkPipeBuilder {
    items: Vec<PipeItem>,
}

#[allow(dead_code)]
impl SinkPipeBuilder {
    pub fn create() -> SinkPipeBuilder {
        SinkPipeBuilder { items: vec![] }
    }

    pub fn finalize(self) -> Pipe {
        Pipe::create(self.items.len(), 0, self.items)
    }

    pub fn add_sink(&mut self, inputs_port: Arc<InputPort>, sink: ProcessorPtr) {
        self.items
            .push(PipeItem::create(sink, vec![inputs_port], vec![]));
    }
}

pub struct TransformPipeBuilder {
    items: Vec<PipeItem>,
}

impl TransformPipeBuilder {
    pub fn create() -> TransformPipeBuilder {
        TransformPipeBuilder { items: vec![] }
    }

    pub fn finalize(self) -> Pipe {
        Pipe::create(self.items.len(), self.items.len(), self.items)
    }

    pub fn add_transform(
        &mut self,
        input: Arc<InputPort>,
        output: Arc<OutputPort>,
        proc: ProcessorPtr,
    ) {
        self.items
            .push(PipeItem::create(proc, vec![input], vec![output]));
    }
}
