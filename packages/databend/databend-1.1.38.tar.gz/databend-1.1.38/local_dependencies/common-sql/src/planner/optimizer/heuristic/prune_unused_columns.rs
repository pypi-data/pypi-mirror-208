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

use common_exception::ErrorCode;
use common_exception::Result;

use crate::optimizer::util::contains_project_set;
use crate::optimizer::ColumnSet;
use crate::optimizer::SExpr;
use crate::plans::Aggregate;
use crate::plans::DummyTableScan;
use crate::plans::EvalScalar;
use crate::plans::RelOperator;
use crate::plans::WindowFuncType;
use crate::ColumnEntry;
use crate::MetadataRef;

pub struct UnusedColumnPruner {
    metadata: MetadataRef,
}

impl UnusedColumnPruner {
    pub fn new(metadata: MetadataRef) -> Self {
        Self { metadata }
    }

    pub fn remove_unused_columns(&self, expr: &SExpr, require_columns: ColumnSet) -> Result<SExpr> {
        let mut s_expr = self.keep_required_columns(expr, require_columns)?;
        s_expr.applied_rules = expr.applied_rules.clone();
        Ok(s_expr)
    }

    /// Keep columns referenced by parent plan node.
    /// `required` contains columns referenced by its ancestors. When a node has multiple children,
    /// the required columns for each child could be different and we may include columns not needed
    /// by a specific child. Columns should be skipped once we found it not exist in the subtree as we
    /// visit a plan node.
    fn keep_required_columns(&self, expr: &SExpr, mut required: ColumnSet) -> Result<SExpr> {
        match expr.plan() {
            RelOperator::Scan(p) => {
                // add virtual columns to scan
                let mut virtual_columns = ColumnSet::new();
                for column in self
                    .metadata
                    .read()
                    .virtual_columns_by_table_index(p.table_index)
                    .iter()
                {
                    match column {
                        ColumnEntry::VirtualColumn(virtual_column) => {
                            virtual_columns.insert(virtual_column.column_index);
                        }
                        _ => unreachable!(),
                    }
                }

                // Some table may not have any column,
                // e.g. `system.sync_crash_me`
                if p.columns.is_empty() && virtual_columns.is_empty() {
                    return Ok(expr.clone());
                }
                let columns = p.columns.union(&virtual_columns).cloned().collect();
                let mut prewhere = p.prewhere.clone();
                let mut used: ColumnSet = required.intersection(&columns).cloned().collect();
                if let Some(ref mut pw) = prewhere {
                    debug_assert!(
                        pw.prewhere_columns.is_subset(&columns),
                        "prewhere columns should be a subset of scan columns"
                    );
                    pw.output_columns = used.clone();
                    // `prune_columns` is after `prewhere_optimize`,
                    // so we need to add prewhere columns to scan columns.
                    used = used.union(&pw.prewhere_columns).cloned().collect();
                }

                Ok(SExpr::create_leaf(RelOperator::Scan(
                    p.prune_columns(used, prewhere),
                )))
            }
            RelOperator::Join(p) => {
                // Include columns referenced in left conditions
                let left = p.left_conditions.iter().fold(required.clone(), |acc, v| {
                    acc.union(&v.used_columns()).cloned().collect()
                });
                // Include columns referenced in right conditions
                let right = p.right_conditions.iter().fold(required.clone(), |acc, v| {
                    acc.union(&v.used_columns()).cloned().collect()
                });

                let others = p.non_equi_conditions.iter().fold(required, |acc, v| {
                    acc.union(&v.used_columns()).cloned().collect()
                });

                Ok(SExpr::create_binary(
                    RelOperator::Join(p.clone()),
                    self.keep_required_columns(
                        expr.child(0)?,
                        left.union(&others).cloned().collect(),
                    )?,
                    self.keep_required_columns(
                        expr.child(1)?,
                        right.union(&others).cloned().collect(),
                    )?,
                ))
            }

            RelOperator::EvalScalar(p) => {
                let mut used = vec![];
                if contains_project_set(expr) {
                    return Ok(SExpr::create_unary(
                        RelOperator::EvalScalar(EvalScalar {
                            items: p.items.clone(),
                        }),
                        expr.child(0)?.clone(),
                    ));
                }
                // Only keep columns needed by parent plan.
                for s in p.items.iter() {
                    if !required.contains(&s.index) {
                        continue;
                    }
                    used.push(s.clone());
                    s.scalar.used_columns().iter().for_each(|c| {
                        required.insert(*c);
                    })
                }
                if used.is_empty() {
                    // Eliminate unnecessary `EvalScalar`
                    self.keep_required_columns(expr.child(0)?, required)
                } else {
                    Ok(SExpr::create_unary(
                        RelOperator::EvalScalar(EvalScalar { items: used }),
                        self.keep_required_columns(expr.child(0)?, required)?,
                    ))
                }
            }
            RelOperator::Filter(p) => {
                let used = p.predicates.iter().fold(required, |acc, v| {
                    acc.union(&v.used_columns()).cloned().collect()
                });
                Ok(SExpr::create_unary(
                    RelOperator::Filter(p.clone()),
                    self.keep_required_columns(expr.child(0)?, used)?,
                ))
            }
            RelOperator::Aggregate(p) => {
                let mut used = vec![];
                for item in &p.aggregate_functions {
                    if required.contains(&item.index) {
                        for c in item.scalar.used_columns() {
                            required.insert(c);
                        }
                        used.push(item.clone());
                    }
                }

                p.group_items.iter().for_each(|i| {
                    // If the group item comes from a complex expression, we only include the final
                    // column index here. The used columns will be included in its EvalScalar child.
                    required.insert(i.index);
                });

                // If the aggregate is empty, we remove the aggregate operator and replace it with
                // a DummyTableScan which returns exactly one row.
                if p.group_items.is_empty() && used.is_empty() {
                    Ok(SExpr::create_leaf(RelOperator::DummyTableScan(
                        DummyTableScan,
                    )))
                } else {
                    Ok(SExpr::create_unary(
                        RelOperator::Aggregate(Aggregate {
                            group_items: p.group_items.clone(),
                            aggregate_functions: used,
                            from_distinct: p.from_distinct,
                            mode: p.mode,
                            limit: p.limit,
                            grouping_id_index: p.grouping_id_index,
                            grouping_sets: p.grouping_sets.clone(),
                        }),
                        self.keep_required_columns(expr.child(0)?, required)?,
                    ))
                }
            }
            RelOperator::Window(p) => {
                if required.contains(&p.index) {
                    if let WindowFuncType::Aggregate(agg) = &p.function {
                        agg.args.iter().for_each(|item| {
                            required.extend(item.used_columns());
                        });
                    }
                    p.partition_by.iter().for_each(|item| {
                        required.insert(item.index);
                    });
                    p.order_by.iter().for_each(|item| {
                        required.insert(item.order_by_item.index);
                    });
                }

                Ok(SExpr::create_unary(
                    RelOperator::Window(p.clone()),
                    self.keep_required_columns(expr.child(0)?, required)?,
                ))
            }
            RelOperator::Sort(p) => {
                p.items.iter().for_each(|s| {
                    required.insert(s.index);
                });
                Ok(SExpr::create_unary(
                    RelOperator::Sort(p.clone()),
                    self.keep_required_columns(expr.child(0)?, required)?,
                ))
            }
            RelOperator::Limit(p) => Ok(SExpr::create_unary(
                RelOperator::Limit(p.clone()),
                self.keep_required_columns(expr.child(0)?, required)?,
            )),

            RelOperator::UnionAll(p) => {
                let left_used = p.pairs.iter().fold(required.clone(), |mut acc, v| {
                    acc.insert(v.0);
                    acc
                });
                let right_used = p.pairs.iter().fold(required, |mut acc, v| {
                    acc.insert(v.1);
                    acc
                });
                Ok(SExpr::create_binary(
                    RelOperator::UnionAll(p.clone()),
                    self.keep_required_columns(expr.child(0)?, left_used)?,
                    self.keep_required_columns(expr.child(1)?, right_used)?,
                ))
            }

            RelOperator::ProjectSet(op) => {
                // We can't prune SRFs because they may change the cardinality of result set,
                // even if the result column of an SRF is not used by any following expression.
                for s in op.srfs.iter() {
                    required.extend(s.scalar.used_columns().iter().copied());
                }

                Ok(SExpr::create_unary(
                    RelOperator::ProjectSet(op.clone()),
                    self.keep_required_columns(expr.child(0)?, required)?,
                ))
            }

            RelOperator::DummyTableScan(_) => Ok(expr.clone()),

            _ => Err(ErrorCode::Internal(
                "Attempting to prune columns of a physical plan is not allowed",
            )),
        }
    }
}
