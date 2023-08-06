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

use common_expression::FunctionRegistry;

mod arithmetic;
mod arithmetic_modulo;
mod array;
mod bitmap;
mod boolean;
mod comparison;
mod control;
mod datetime;
mod decimal;
mod geo;
mod hash;
mod map;
mod math;
mod other;
mod string;
mod string_multi_args;
mod tuple;
mod variant;
mod vector;

pub use comparison::check_pattern_type;
pub use comparison::is_like_pattern_escape;
pub use comparison::PatternType;
pub use comparison::ALL_COMP_FUNC_NAMES;

pub fn register(registry: &mut FunctionRegistry) {
    variant::register(registry);
    arithmetic::register(registry);
    array::register(registry);
    boolean::register(registry);
    control::register(registry);
    comparison::register(registry);
    datetime::register(registry);
    math::register(registry);
    map::register(registry);
    string::register(registry);
    string_multi_args::register(registry);
    tuple::register(registry);
    geo::register(registry);
    hash::register(registry);
    other::register(registry);
    decimal::register(registry);
    vector::register(registry);
    bitmap::register(registry);
}
