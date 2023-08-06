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
use common_expression::types::DataType;
use common_expression::Scalar;

use crate::binder::split_conjunctions;
use crate::optimizer::rule::Rule;
use crate::optimizer::rule::TransformResult;
use crate::optimizer::RuleID;
use crate::optimizer::SExpr;
use crate::plans::ConstantExpr;
use crate::plans::Filter;
use crate::plans::FunctionCall;
use crate::plans::PatternPlan;
use crate::plans::RelOp;
use crate::plans::ScalarExpr;

#[derive(Clone, PartialEq, Debug)]
enum PredicateScalar {
    And { args: Vec<PredicateScalar> },
    Or { args: Vec<PredicateScalar> },
    Other { expr: Box<ScalarExpr> },
}

fn predicate_scalar(scalar: &ScalarExpr) -> PredicateScalar {
    match scalar {
        ScalarExpr::FunctionCall(func) if func.func_name == "and" => {
            let args = func.arguments.iter().map(predicate_scalar).collect();
            PredicateScalar::And { args }
        }
        ScalarExpr::FunctionCall(func) if func.func_name == "or" => {
            let args = func.arguments.iter().map(predicate_scalar).collect();
            PredicateScalar::Or { args }
        }
        _ => PredicateScalar::Other {
            expr: Box::from(scalar.clone()),
        },
    }
}

fn normalize_predicate_scalar(
    predicate_scalar: PredicateScalar,
    return_type: DataType,
) -> ScalarExpr {
    match predicate_scalar {
        PredicateScalar::And { args } => {
            assert!(args.len() >= 2);
            args.into_iter()
                .map(|arg| normalize_predicate_scalar(arg, return_type.clone()))
                .reduce(|lhs, rhs| {
                    ScalarExpr::FunctionCall(FunctionCall {
                        span: None,
                        func_name: "and".to_string(),
                        params: vec![],
                        arguments: vec![lhs, rhs],
                    })
                })
                .expect("has at least two args")
        }
        PredicateScalar::Or { args } => {
            assert!(args.len() >= 2);
            args.into_iter()
                .map(|arg| normalize_predicate_scalar(arg, return_type.clone()))
                .reduce(|lhs, rhs| {
                    ScalarExpr::FunctionCall(FunctionCall {
                        span: None,
                        func_name: "or".to_string(),
                        params: vec![],
                        arguments: vec![lhs, rhs],
                    })
                })
                .expect("has at least two args")
        }
        PredicateScalar::Other { expr } => *expr,
    }
}

// The rule tries to apply the inverse OR distributive law to the predicate.
// ((A AND B) OR (A AND C))  =>  (A AND (B OR C))
// It'll find all OR expressions and extract the common terms.
pub struct RuleNormalizeDisjunctiveFilter {
    id: RuleID,
    patterns: Vec<SExpr>,
}

impl RuleNormalizeDisjunctiveFilter {
    pub fn new() -> Self {
        Self {
            id: RuleID::NormalizeDisjunctiveFilter,
            // Filter
            //  \
            //   *
            patterns: vec![SExpr::create_unary(
                PatternPlan {
                    plan_type: RelOp::Filter,
                }
                .into(),
                SExpr::create_leaf(
                    PatternPlan {
                        plan_type: RelOp::Pattern,
                    }
                    .into(),
                ),
            )],
        }
    }
}

impl Rule for RuleNormalizeDisjunctiveFilter {
    fn id(&self) -> RuleID {
        self.id
    }

    fn apply(&self, s_expr: &SExpr, state: &mut TransformResult) -> Result<()> {
        let filter: Filter = s_expr.plan().clone().try_into()?;
        let predicates = filter.predicates;
        let mut rewritten_predicates = Vec::with_capacity(predicates.len());
        let mut rewritten = false;
        for predicate in predicates.iter() {
            let predicate_scalar = predicate_scalar(predicate);
            let (rewritten_predicate_scalar, has_rewritten) =
                rewrite_predicate_ors(predicate_scalar);
            if has_rewritten {
                rewritten = true;
            }
            rewritten_predicates.push(normalize_predicate_scalar(
                rewritten_predicate_scalar,
                predicate.data_type()?,
            ));
        }
        let mut split_predicates: Vec<ScalarExpr> = Vec::with_capacity(rewritten_predicates.len());
        for predicate in rewritten_predicates.iter() {
            split_predicates.extend_from_slice(&split_conjunctions(predicate));
        }
        if rewritten {
            state.add_result(SExpr::create_unary(
                Filter {
                    predicates: split_predicates,
                    is_having: filter.is_having,
                }
                .into(),
                s_expr.child(0)?.clone(),
            ));
        }
        Ok(())
    }

    fn patterns(&self) -> &Vec<SExpr> {
        &self.patterns
    }
}

fn rewrite_predicate_ors(predicate: PredicateScalar) -> (PredicateScalar, bool) {
    match predicate {
        PredicateScalar::Or { args } => {
            let mut or_args = Vec::with_capacity(args.len());
            for arg in args.iter() {
                or_args.push(rewrite_predicate_ors(arg.clone()).0);
            }
            or_args = flatten_ors(or_args);
            process_duplicate_or_exprs(&or_args)
        }
        PredicateScalar::And { args } => {
            let mut and_args = Vec::with_capacity(args.len());
            for arg in args.iter() {
                and_args.push(rewrite_predicate_ors(arg.clone()).0);
            }
            and_args = flatten_ands(and_args);
            (PredicateScalar::And { args: and_args }, false)
        }
        PredicateScalar::Other { .. } => (predicate, false),
    }
}

// Recursively flatten the OR expressions.
fn flatten_ors(or_args: impl IntoIterator<Item = PredicateScalar>) -> Vec<PredicateScalar> {
    let mut flattened_ors = vec![];
    for or_arg in or_args {
        match or_arg {
            PredicateScalar::Or { args } => flattened_ors.extend(flatten_ors(args)),
            _ => flattened_ors.push(or_arg),
        }
    }
    flattened_ors
}

// Recursively flatten the AND expressions.
fn flatten_ands(and_args: impl IntoIterator<Item = PredicateScalar>) -> Vec<PredicateScalar> {
    let mut flattened_ands = vec![];
    for and_arg in and_args {
        match and_arg {
            PredicateScalar::And { args } => flattened_ands.extend(flatten_ands(args)),
            _ => flattened_ands.push(and_arg),
        }
    }
    flattened_ands
}

// Apply the inverse OR distributive law.
fn process_duplicate_or_exprs(or_args: &[PredicateScalar]) -> (PredicateScalar, bool) {
    let mut shortest_exprs: Vec<PredicateScalar> = vec![];
    let mut shortest_exprs_len = 0;
    if or_args.is_empty() {
        return (
            PredicateScalar::Other {
                expr: Box::from(ScalarExpr::ConstantExpr(ConstantExpr {
                    span: None,
                    value: Scalar::Boolean(false),
                })),
            },
            false,
        );
    }
    if or_args.len() == 1 {
        return (or_args[0].clone(), false);
    }
    // choose the shortest AND expression
    for or_arg in or_args.iter() {
        match or_arg {
            PredicateScalar::And { args } => {
                let args_num = args.len();
                if shortest_exprs.is_empty() || args_num < shortest_exprs_len {
                    shortest_exprs = (*args).clone();
                    shortest_exprs_len = args_num;
                }
            }
            _ => {
                // if there is no AND expression, it must be the shortest expression.
                shortest_exprs = vec![or_arg.clone()];
                break;
            }
        }
    }

    // dedup shortest_exprs
    shortest_exprs.dedup();

    // Check each element in shortest_exprs to see if it's in all the OR arguments.
    let mut exist_exprs: Vec<PredicateScalar> = vec![];
    for expr in shortest_exprs.iter() {
        let found = or_args.iter().all(|or_arg| match or_arg {
            PredicateScalar::And { args } => args.contains(expr),
            _ => or_arg == expr,
        });
        if found {
            exist_exprs.push((*expr).clone());
        }
    }

    if exist_exprs.is_empty() {
        return (
            PredicateScalar::Or {
                args: or_args.to_vec(),
            },
            false,
        );
    }

    // Rebuild the OR predicate.
    // (A AND B) OR A will be optimized to A.
    let mut new_or_args = vec![];
    for or_arg in or_args.iter() {
        match or_arg {
            PredicateScalar::And { args } => {
                let mut new_args = (*args).clone();
                new_args.retain(|expr| !exist_exprs.contains(expr));
                if !new_args.is_empty() {
                    if new_args.len() == 1 {
                        new_or_args.push(new_args[0].clone());
                    } else {
                        new_or_args.push(PredicateScalar::And { args: new_args });
                    }
                } else {
                    new_or_args.clear();
                    break;
                }
            }
            _ => {
                if exist_exprs.contains(or_arg) {
                    new_or_args.clear();
                    break;
                }
            }
        }
    }
    if !new_or_args.is_empty() {
        if new_or_args.len() == 1 {
            exist_exprs.push(new_or_args[0].clone());
        } else {
            exist_exprs.push(PredicateScalar::Or {
                args: flatten_ors(new_or_args),
            });
        }
    }

    if exist_exprs.len() == 1 {
        (exist_exprs[0].clone(), true)
    } else {
        (
            PredicateScalar::And {
                args: flatten_ands(exist_exprs),
            },
            true,
        )
    }
}
