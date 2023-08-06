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

mod cascades;
mod cost;
mod distributed;
mod format;
mod group;
mod heuristic;
mod hyper_dp;
mod m_expr;
mod memo;
#[allow(clippy::module_inception)]
mod optimizer;
mod pattern_extractor;
mod property;
mod rule;
mod runtime_filter;
mod s_expr;
mod util;

pub use heuristic::HeuristicOptimizer;
pub use heuristic::SubqueryRewriter;
pub use heuristic::DEFAULT_REWRITE_RULES;
pub use m_expr::MExpr;
pub use memo::Memo;
pub use optimizer::optimize;
pub use optimizer::OptimizerConfig;
pub use optimizer::OptimizerContext;
pub use pattern_extractor::PatternExtractor;
pub use property::*;
pub use rule::try_push_down_filter_join;
pub use rule::RuleFactory;
pub use rule::RuleID;
pub use rule::RuleSet;
pub use s_expr::SExpr;
