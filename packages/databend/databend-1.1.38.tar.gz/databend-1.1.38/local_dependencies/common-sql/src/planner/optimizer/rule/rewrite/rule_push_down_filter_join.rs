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

use crate::binder::JoinPredicate;
use crate::optimizer::rule::rewrite::filter_join::convert_mark_to_semi_join;
use crate::optimizer::rule::rewrite::filter_join::outer_to_inner;
use crate::optimizer::rule::rewrite::filter_join::rewrite_predicates;
use crate::optimizer::rule::rewrite::filter_join::try_derive_predicates;
use crate::optimizer::rule::Rule;
use crate::optimizer::rule::TransformResult;
use crate::optimizer::RelExpr;
use crate::optimizer::RuleID;
use crate::optimizer::SExpr;
use crate::plans::ComparisonOp;
use crate::plans::Filter;
use crate::plans::Join;
use crate::plans::JoinType;
use crate::plans::PatternPlan;
use crate::plans::RelOp;
use crate::plans::ScalarExpr;
use crate::MetadataRef;

pub struct RulePushDownFilterJoin {
    id: RuleID,
    patterns: Vec<SExpr>,
    _metadata: MetadataRef,
}

impl RulePushDownFilterJoin {
    pub fn new(metadata: MetadataRef) -> Self {
        Self {
            id: RuleID::PushDownFilterJoin,
            // Filter
            //  \
            //   InnerJoin
            //   | \
            //   |  *
            //   *
            patterns: vec![SExpr::create_unary(
                PatternPlan {
                    plan_type: RelOp::Filter,
                }
                .into(),
                SExpr::create_binary(
                    PatternPlan {
                        plan_type: RelOp::Join,
                    }
                    .into(),
                    SExpr::create_leaf(
                        PatternPlan {
                            plan_type: RelOp::Pattern,
                        }
                        .into(),
                    ),
                    SExpr::create_leaf(
                        PatternPlan {
                            plan_type: RelOp::Pattern,
                        }
                        .into(),
                    ),
                ),
            )],
            _metadata: metadata,
        }
    }
}

impl Rule for RulePushDownFilterJoin {
    fn id(&self) -> RuleID {
        self.id
    }

    fn apply(&self, s_expr: &SExpr, state: &mut TransformResult) -> Result<()> {
        // First, try to convert outer join to inner join
        let mut s_expr = outer_to_inner(s_expr)?;
        // Second, check if can convert mark join to semi join
        s_expr = convert_mark_to_semi_join(&s_expr)?;
        let filter: Filter = s_expr.plan().clone().try_into()?;
        if filter.predicates.is_empty() {
            state.add_result(s_expr);
            return Ok(());
        }
        // Finally, extract or predicates from Filter to push down them to join.
        // For example: `select * from t1, t2 where (t1.a=1 and t2.b=2) or (t1.a=2 and t2.b=1)`
        // The predicate will be rewritten to `((t1.a=1 and t2.b=2) or (t1.a=2 and t2.b=1)) and (t1.a=1 or t1.a=2) and (t2.b=2 or t2.b=1)`
        // So `(t1.a=1 or t1.a=1), (t2.b=2 or t2.b=1)` may be pushed down join and reduce rows between join
        let predicates = rewrite_predicates(&s_expr)?;
        let (need_push, mut result) = try_push_down_filter_join(&s_expr, predicates)?;
        if !need_push {
            return Ok(());
        }
        result.set_applied_rule(&self.id);
        state.add_result(result);

        Ok(())
    }

    fn patterns(&self) -> &Vec<SExpr> {
        &self.patterns
    }
}

pub fn try_push_down_filter_join(
    s_expr: &SExpr,
    predicates: Vec<ScalarExpr>,
) -> Result<(bool, SExpr)> {
    let join_expr = s_expr.child(0)?;
    let mut join: Join = join_expr.plan().clone().try_into()?;

    let rel_expr = RelExpr::with_s_expr(join_expr);
    let left_prop = rel_expr.derive_relational_prop_child(0)?;
    let right_prop = rel_expr.derive_relational_prop_child(1)?;

    let mut left_push_down = vec![];
    let mut right_push_down = vec![];
    let mut original_predicates = vec![];

    let mut need_push = false;

    for predicate in predicates.into_iter() {
        let pred = JoinPredicate::new(&predicate, &left_prop, &right_prop);
        match pred {
            JoinPredicate::Left(_) => {
                if matches!(join.join_type, JoinType::Right) {
                    original_predicates.push(predicate);
                    continue;
                }
                need_push = true;
                left_push_down.push(predicate);
            }
            JoinPredicate::Right(_) => {
                if matches!(join.join_type, JoinType::Left) {
                    original_predicates.push(predicate);
                    continue;
                }
                need_push = true;
                right_push_down.push(predicate);
            }
            JoinPredicate::Other(_) => original_predicates.push(predicate),

            JoinPredicate::Both { left, right, op } => {
                if op == ComparisonOp::Equal {
                    if matches!(join.join_type, JoinType::Inner | JoinType::Cross) {
                        join.join_type = JoinType::Inner;
                        join.left_conditions.push(left.clone());
                        join.right_conditions.push(right.clone());
                        need_push = true;
                    }
                } else if matches!(join.join_type, JoinType::Inner) {
                    join.non_equi_conditions.push(predicate.clone());
                    need_push = true;
                } else {
                    original_predicates.push(predicate);
                }
            }
        }
    }

    if !need_push {
        return Ok((false, s_expr.clone()));
    }

    // try to derive new predicate and push down filter
    let mut result = try_derive_predicates(s_expr, join, left_push_down, right_push_down)?;

    if !original_predicates.is_empty() {
        result = SExpr::create_unary(
            Filter {
                predicates: original_predicates,
                is_having: false,
            }
            .into(),
            result,
        );
    }
    Ok((need_push, result))
}
