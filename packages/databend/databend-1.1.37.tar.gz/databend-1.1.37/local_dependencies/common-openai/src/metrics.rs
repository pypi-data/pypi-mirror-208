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

use metrics::increment_gauge;

pub fn metrics_completion_count(c: u32) {
    increment_gauge!("openai_completion_count", c as f64);
}

pub fn metrics_completion_token(c: u32) {
    increment_gauge!("openai_completion_token", c as f64);
}

pub fn metrics_embedding_count(c: u32) {
    increment_gauge!("openai_embedding_count", c as f64);
}

pub fn metrics_embedding_token(c: u32) {
    increment_gauge!("openai_embedding_token", c as f64);
}
