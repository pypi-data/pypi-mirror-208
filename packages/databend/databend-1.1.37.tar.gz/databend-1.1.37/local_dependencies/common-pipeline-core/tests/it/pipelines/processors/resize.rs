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

use std::sync::Arc;

use common_exception::Result;
use common_pipeline_core::processors::connect;
use common_pipeline_core::processors::port::InputPort;
use common_pipeline_core::processors::port::OutputPort;
use common_pipeline_core::processors::processor::Event;
use common_pipeline_core::processors::Processor;
use common_pipeline_core::processors::ResizeProcessor;

#[tokio::test(flavor = "multi_thread", worker_threads = 1)]
async fn test_resize_output_finish() -> Result<()> {
    let mut resize_processor = ResizeProcessor::create(8, 1);
    let resize_inputs = connect_inputs(resize_processor.get_inputs());
    let resize_outputs = connect_outputs(resize_processor.get_outputs());

    for output in &resize_outputs {
        output.finish();
    }

    assert!(matches!(resize_processor.event()?, Event::Finished));

    for input in &resize_inputs {
        assert!(input.is_finished());
    }

    Ok(())
}

fn connect_inputs(inputs: &[Arc<InputPort>]) -> Vec<Arc<OutputPort>> {
    let mut outputs = Vec::with_capacity(inputs.len());

    unsafe {
        for input in inputs {
            let output = OutputPort::create();
            connect(input, &output);
            outputs.push(output);
        }
    }

    outputs
}

fn connect_outputs(outputs: &[Arc<OutputPort>]) -> Vec<Arc<InputPort>> {
    let mut inputs = Vec::with_capacity(outputs.len());

    unsafe {
        for output in outputs {
            let input = InputPort::create();
            connect(&input, output);
            inputs.push(input);
        }
    }

    inputs
}
