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

use crate::optimizer::SExpr;
use crate::plans::Filter;
use crate::plans::Join;
use crate::plans::JoinType;
use crate::ScalarExpr;

pub fn convert_mark_to_semi_join(s_expr: &SExpr) -> Result<SExpr> {
    let mut filter: Filter = s_expr.plan().clone().try_into()?;
    let mut join: Join = s_expr.child(0)?.plan().clone().try_into()?;
    let has_disjunction = filter.predicates.iter().any(
        |predicate| matches!(predicate, ScalarExpr::FunctionCall(func) if func.func_name == "or"),
    );
    if !join.join_type.is_mark_join() || has_disjunction {
        return Ok(s_expr.clone());
    }

    let mark_index = join.marker_index.unwrap();
    let mut find_mark_index = false;

    // remove mark index filter
    for (idx, predicate) in filter.predicates.iter().enumerate() {
        match predicate {
            ScalarExpr::BoundColumnRef(col) if col.column.index == mark_index => {
                find_mark_index = true;
                filter.predicates.remove(idx);
                break;
            }
            ScalarExpr::FunctionCall(func) if func.func_name == "not" => {
                // Check if the argument is mark index, if so, we won't convert it to semi join
                if let ScalarExpr::BoundColumnRef(col) = &func.arguments[0] {
                    if col.column.index == mark_index {
                        return Ok(s_expr.clone());
                    }
                }
            }
            _ => (),
        }
    }

    if !find_mark_index {
        // To be conservative, we do not convert
        return Ok(s_expr.clone());
    }

    join.join_type = match join.join_type {
        JoinType::LeftMark => JoinType::RightSemi,
        JoinType::RightMark => JoinType::LeftSemi,
        _ => unreachable!(),
    };

    let s_join_expr = s_expr.child(0)?;
    let mut result = SExpr::create_binary(
        join.into(),
        s_join_expr.child(0)?.clone(),
        s_join_expr.child(1)?.clone(),
    );

    result = SExpr::create_unary(filter.into(), result);
    Ok(result)
}
