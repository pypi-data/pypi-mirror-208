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

use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::collections::HashSet;

use common_ast::ast::Expr;
use common_ast::ast::GroupBy;
use common_ast::ast::Literal;
use common_ast::ast::SelectTarget;
use common_exception::ErrorCode;
use common_exception::Result;
use common_expression::types::DataType;
use common_expression::types::NumberDataType;
use itertools::Itertools;

use super::prune_by_children;
use crate::binder::scalar::ScalarBinder;
use crate::binder::select::SelectList;
use crate::binder::Binder;
use crate::binder::ColumnBinding;
use crate::binder::Visibility;
use crate::optimizer::SExpr;
use crate::plans::Aggregate;
use crate::plans::AggregateFunction;
use crate::plans::AggregateMode;
use crate::plans::BoundColumnRef;
use crate::plans::CastExpr;
use crate::plans::EvalScalar;
use crate::plans::FunctionCall;
use crate::plans::ScalarExpr;
use crate::plans::ScalarItem;
use crate::plans::WindowFunc;
use crate::plans::WindowFuncType;
use crate::plans::WindowOrderBy;
use crate::BindContext;
use crate::IndexType;
use crate::MetadataRef;

#[derive(Default, Clone, PartialEq, Eq, Debug)]
pub struct AggregateInfo {
    /// Aggregation functions
    pub aggregate_functions: Vec<ScalarItem>,

    /// Arguments of aggregation functions
    pub aggregate_arguments: Vec<ScalarItem>,

    /// Group items of aggregation
    pub group_items: Vec<ScalarItem>,

    /// Output columns of aggregation, including group items and aggregate functions.
    pub output_columns: Vec<ColumnBinding>,

    /// Mapping: (aggregate function display name) -> (index of agg func in `aggregate_functions`)
    /// This is used to find a aggregate function in current context.
    pub aggregate_functions_map: HashMap<String, usize>,

    /// Mapping: (group item) -> (index of group item in `group_items`)
    /// This is used to check if a scalar expression is a group item.
    /// For example, `SELECT count(*) FROM t GROUP BY a+1 HAVING a+1+1`.
    /// The group item `a+1` is involved in `a+1+1`, so it's a valid `HAVING`.
    /// We will check the validity by lookup this map with display name.
    pub group_items_map: HashMap<ScalarExpr, usize>,

    /// Index for virtual column `grouping_id`. It's valid only if `grouping_sets` is not empty.
    pub grouping_id_column: Option<ColumnBinding>,
    /// Each grouping set is a list of column indices in `group_items`.
    pub grouping_sets: Vec<Vec<IndexType>>,
}

pub(super) struct AggregateRewriter<'a> {
    pub bind_context: &'a mut BindContext,
    pub metadata: MetadataRef,
    // If the aggregate function is in the arguments of window function,
    // ignore it here, it will be processed later when analyzing window.
    in_window: bool,
}

impl<'a> AggregateRewriter<'a> {
    pub fn new(bind_context: &'a mut BindContext, metadata: MetadataRef) -> Self {
        Self {
            bind_context,
            metadata,
            in_window: false,
        }
    }

    pub fn visit(&mut self, scalar: &ScalarExpr) -> Result<ScalarExpr> {
        match scalar {
            ScalarExpr::BoundColumnRef(_) => Ok(scalar.clone()),
            ScalarExpr::ConstantExpr(_) => Ok(scalar.clone()),
            ScalarExpr::FunctionCall(func) => {
                if func.func_name.eq_ignore_ascii_case("grouping") {
                    return self.replace_grouping(func);
                }
                let new_args = func
                    .arguments
                    .iter()
                    .map(|arg| self.visit(arg))
                    .collect::<Result<Vec<_>>>()?;
                Ok(FunctionCall {
                    span: func.span,
                    func_name: func.func_name.clone(),
                    params: func.params.clone(),
                    arguments: new_args,
                }
                .into())
            }
            ScalarExpr::CastExpr(cast) => Ok(CastExpr {
                span: cast.span,
                is_try: cast.is_try,
                argument: Box::new(self.visit(&cast.argument)?),
                target_type: cast.target_type.clone(),
            }
            .into()),

            // TODO(leiysky): should we recursively process subquery here?
            ScalarExpr::SubqueryExpr(_) => Ok(scalar.clone()),

            ScalarExpr::AggregateFunction(agg_func) => self.replace_aggregate_function(agg_func),

            ScalarExpr::WindowFunction(window) => {
                self.in_window = true;

                let partition_by = window
                    .partition_by
                    .iter()
                    .map(|part| self.visit(part))
                    .collect::<Result<Vec<_>>>()?;
                let order_by = window
                    .order_by
                    .iter()
                    .map(|order| {
                        Ok(WindowOrderBy {
                            expr: self.visit(&order.expr)?,
                            asc: order.asc,
                            nulls_first: order.nulls_first,
                        })
                    })
                    .collect::<Result<Vec<_>>>()?;
                let func = match &window.func {
                    WindowFuncType::Aggregate(agg) => {
                        let new_args = agg
                            .args
                            .iter()
                            .map(|arg| self.visit(arg))
                            .collect::<Result<Vec<_>>>()?;
                        WindowFuncType::Aggregate(AggregateFunction {
                            func_name: agg.func_name.clone(),
                            args: new_args,
                            display_name: agg.display_name.clone(),
                            distinct: agg.distinct,
                            params: agg.params.clone(),
                            return_type: agg.return_type.clone(),
                        })
                    }
                    func => func.clone(),
                };

                self.in_window = false;

                Ok(WindowFunc {
                    span: window.span,
                    display_name: window.display_name.clone(),
                    func,
                    partition_by,
                    order_by,
                    frame: window.frame.clone(),
                }
                .into())
            }
        }
    }

    /// Replace the arguments of aggregate function with a BoundColumnRef, and
    /// add the replaced aggregate function and the arguments into `AggregateInfo`.
    fn replace_aggregate_function(&mut self, aggregate: &AggregateFunction) -> Result<ScalarExpr> {
        let agg_info = &mut self.bind_context.aggregate_info;
        let mut replaced_args: Vec<ScalarExpr> = Vec::with_capacity(aggregate.args.len());

        for (i, arg) in aggregate.args.iter().enumerate() {
            let name = format!("{}_arg_{}", &aggregate.func_name, i);
            if let ScalarExpr::BoundColumnRef(column_ref) = arg {
                replaced_args.push(column_ref.clone().into());
                agg_info.aggregate_arguments.push(ScalarItem {
                    index: column_ref.column.index,
                    scalar: arg.clone(),
                });
            } else {
                let index = self
                    .metadata
                    .write()
                    .add_derived_column(name.clone(), arg.data_type()?);

                // Generate a ColumnBinding for each argument of aggregates
                let column_binding = ColumnBinding {
                    database_name: None,
                    table_name: None,

                    // TODO(leiysky): use a more reasonable name, since aggregate arguments
                    // can not be referenced, the name is only for debug
                    table_index: None,
                    column_name: name,
                    index,
                    data_type: Box::new(arg.data_type()?),
                    visibility: Visibility::Visible,
                };
                replaced_args.push(
                    BoundColumnRef {
                        span: arg.span(),
                        column: column_binding.clone(),
                    }
                    .into(),
                );
                agg_info.aggregate_arguments.push(ScalarItem {
                    index,
                    scalar: arg.clone(),
                });
            }
        }

        let index = self.metadata.write().add_derived_column(
            aggregate.display_name.clone(),
            *aggregate.return_type.clone(),
        );

        let replaced_agg = AggregateFunction {
            display_name: aggregate.display_name.clone(),
            func_name: aggregate.func_name.clone(),
            distinct: aggregate.distinct,
            params: aggregate.params.clone(),
            args: replaced_args,
            return_type: aggregate.return_type.clone(),
        };

        agg_info.aggregate_functions.push(ScalarItem {
            scalar: replaced_agg.clone().into(),
            index,
        });
        agg_info.aggregate_functions_map.insert(
            replaced_agg.display_name.clone(),
            agg_info.aggregate_functions.len() - 1,
        );

        Ok(replaced_agg.into())
    }

    fn replace_grouping(&mut self, function: &FunctionCall) -> Result<ScalarExpr> {
        let agg_info = &mut self.bind_context.aggregate_info;
        if agg_info.grouping_id_column.is_none() {
            return Err(ErrorCode::SemanticError(
                "grouping can only be called in GROUP BY GROUPING SETS clauses",
            ));
        }
        let grouping_id_column = agg_info.grouping_id_column.clone().unwrap();

        // Rewrite the args to params.
        // The params are the index offset in `grouping_id`.
        // Here is an example:
        // If the query is `select grouping(b, a) from group by grouping sets ((a, b), (a));`
        // The group-by items are: [a, b].
        // The group ids will be (a: 0, b: 1):
        // ba -> 00 -> 0
        // _a -> 01 -> 1
        // grouping(b, a) will be rewritten to grouping<1, 0>(grouping_id).
        let mut replaced_params = Vec::with_capacity(function.arguments.len());
        for arg in &function.arguments {
            if let Some(index) = agg_info.group_items_map.get(arg) {
                replaced_params.push(*index);
            } else {
                return Err(ErrorCode::BadArguments(
                    "Arguments of grouping should be group by expressions",
                ));
            }
        }

        let replaced_func = FunctionCall {
            span: function.span,
            func_name: function.func_name.clone(),
            params: replaced_params,
            arguments: vec![ScalarExpr::BoundColumnRef(BoundColumnRef {
                span: function.span,
                column: grouping_id_column,
            })],
        };

        Ok(replaced_func.into())
    }
}
impl Binder {
    /// Analyze aggregates in select clause, this will rewrite aggregate functions.
    /// See [`AggregateRewriter`] for more details.
    pub(crate) fn analyze_aggregate_select(
        &mut self,
        bind_context: &mut BindContext,
        select_list: &mut SelectList,
    ) -> Result<()> {
        for item in select_list.items.iter_mut() {
            let mut rewriter = AggregateRewriter::new(bind_context, self.metadata.clone());
            let new_scalar = rewriter.visit(&item.scalar)?;
            item.scalar = new_scalar;
        }

        Ok(())
    }

    /// We have supported three kinds of `group by` items:
    ///
    ///   - Index, a integral literal, e.g. `GROUP BY 1`. It choose the 1st item in select as
    ///     group item.
    ///   - Alias, the aliased expressions specified in `SELECT` clause, e.g. column `b` in
    ///     `SELECT a as b, COUNT(a) FROM t GROUP BY b`.
    ///   - Scalar expressions that can be evaluated in current scope(doesn't contain aliases), e.g.
    ///     column `a` and expression `a+1` in `SELECT a as b, COUNT(a) FROM t GROUP BY a, a+1`.
    #[async_backtrace::framed]
    pub async fn analyze_group_items<'a>(
        &mut self,
        bind_context: &mut BindContext,
        select_list: &SelectList<'a>,
        group_by: &GroupBy,
    ) -> Result<()> {
        let mut available_aliases = vec![];

        // Extract available aliases from `SELECT` clause,
        for item in select_list.items.iter() {
            if let SelectTarget::AliasedExpr { alias: Some(_), .. } = item.select_target {
                let column = if let ScalarExpr::BoundColumnRef(column_ref) = &item.scalar {
                    let mut column = column_ref.column.clone();
                    column.column_name = item.alias.clone();
                    column
                } else {
                    self.create_column_binding(
                        None,
                        None,
                        None,
                        item.alias.clone(),
                        item.scalar.data_type()?,
                    )
                };
                available_aliases.push((column, item.scalar.clone()));
            }
        }

        match group_by {
            GroupBy::Normal(exprs) => {
                self.resolve_group_items(
                    bind_context,
                    select_list,
                    exprs,
                    &available_aliases,
                    false,
                    &mut vec![],
                )
                .await
            }
            GroupBy::GroupingSets(sets) => {
                self.resolve_grouping_sets(bind_context, select_list, sets, &available_aliases)
                    .await
            }
            // TODO: avoid too many clones.
            GroupBy::Rollup(exprs) => {
                // ROLLUP (a,b,c) => GROUPING SETS ((a,b,c), (a,b), (a), ())
                let mut sets = Vec::with_capacity(exprs.len() + 1);
                for i in (0..=exprs.len()).rev() {
                    sets.push(exprs[0..i].to_vec());
                }
                self.resolve_grouping_sets(bind_context, select_list, &sets, &available_aliases)
                    .await
            }
            GroupBy::Cube(exprs) => {
                // CUBE (a,b) => GROUPING SETS ((a,b),(a),(b),()) // All subsets
                let sets = (0..=exprs.len())
                    .flat_map(|count| exprs.clone().into_iter().combinations(count))
                    .collect::<Vec<_>>();
                self.resolve_grouping_sets(bind_context, select_list, &sets, &available_aliases)
                    .await
            }
        }
    }

    #[async_backtrace::framed]
    pub(super) async fn bind_aggregate(
        &mut self,
        bind_context: &mut BindContext,
        child: SExpr,
    ) -> Result<SExpr> {
        // Enter in_grouping state
        bind_context.in_grouping = true;

        // Build a ProjectPlan, which will produce aggregate arguments and group items
        let agg_info = &bind_context.aggregate_info;
        let mut scalar_items: Vec<ScalarItem> =
            Vec::with_capacity(agg_info.aggregate_arguments.len() + agg_info.group_items.len());
        for arg in agg_info.aggregate_arguments.iter() {
            scalar_items.push(arg.clone());
        }
        for item in agg_info.group_items.iter() {
            if let ScalarExpr::BoundColumnRef(col) = &item.scalar {
                if col.column.column_name.eq("_grouping_id") {
                    continue;
                }
            }
            scalar_items.push(item.clone());
        }

        let mut new_expr = child;
        if !scalar_items.is_empty() {
            let eval_scalar = EvalScalar {
                items: scalar_items,
            };
            new_expr = SExpr::create_unary(eval_scalar.into(), new_expr);
        }

        let aggregate_plan = Aggregate {
            mode: AggregateMode::Initial,
            group_items: bind_context.aggregate_info.group_items.clone(),
            aggregate_functions: bind_context.aggregate_info.aggregate_functions.clone(),
            from_distinct: false,
            limit: None,
            grouping_sets: agg_info.grouping_sets.clone(),
            grouping_id_index: agg_info
                .grouping_id_column
                .as_ref()
                .map(|g| g.index)
                .unwrap_or(0),
        };
        new_expr = SExpr::create_unary(aggregate_plan.into(), new_expr);

        Ok(new_expr)
    }

    #[async_backtrace::framed]
    async fn resolve_grouping_sets(
        &mut self,
        bind_context: &mut BindContext,
        select_list: &SelectList<'_>,
        sets: &[Vec<Expr>],
        available_aliases: &[(ColumnBinding, ScalarExpr)],
    ) -> Result<()> {
        let mut grouping_sets = Vec::with_capacity(sets.len());
        for set in sets {
            self.resolve_group_items(
                bind_context,
                select_list,
                set,
                available_aliases,
                true,
                &mut grouping_sets,
            )
            .await?;
        }
        let agg_info = &mut bind_context.aggregate_info;
        // `grouping_sets` stores formatted `ScalarExpr` for each grouping set.
        let grouping_sets = grouping_sets
            .into_iter()
            .map(|set| {
                let mut set = set
                    .into_iter()
                    .map(|s| {
                        let offset = *agg_info.group_items_map.get(&s).unwrap();
                        agg_info.group_items[offset].index
                    })
                    .collect::<Vec<_>>();
                // Grouping sets with the same items should be treated as the same.
                set.sort();
                set
            })
            .collect::<Vec<_>>();
        let grouping_sets = grouping_sets.into_iter().unique().collect();
        agg_info.grouping_sets = grouping_sets;
        // Add a virtual column `_grouping_id` to group items.
        let grouping_id_column = self.create_column_binding(
            None,
            None,
            None,
            "_grouping_id".to_string(),
            DataType::Number(NumberDataType::UInt32),
        );
        let index = grouping_id_column.index;
        agg_info.grouping_id_column = Some(grouping_id_column.clone());
        agg_info.group_items_map.insert(
            ScalarExpr::BoundColumnRef(BoundColumnRef {
                span: None,
                column: grouping_id_column.clone(),
            }),
            agg_info.group_items.len(),
        );
        agg_info.group_items.push(ScalarItem {
            index,
            scalar: ScalarExpr::BoundColumnRef(BoundColumnRef {
                span: None,
                column: grouping_id_column,
            }),
        });
        Ok(())
    }

    #[async_backtrace::framed]
    async fn resolve_group_items(
        &mut self,
        bind_context: &mut BindContext,
        select_list: &SelectList<'_>,
        group_by: &[Expr],
        available_aliases: &[(ColumnBinding, ScalarExpr)],
        collect_grouping_sets: bool,
        grouping_sets: &mut Vec<Vec<ScalarExpr>>,
    ) -> Result<()> {
        if collect_grouping_sets {
            grouping_sets.push(Vec::with_capacity(group_by.len()));
        }
        // Resolve group items with `FROM` context. Since the alias item can not be resolved
        // from the context, we can detect the failure and fallback to resolving with `available_aliases`.
        for expr in group_by.iter() {
            // If expr is a number literal, then this is a index group item.
            if let Expr::Literal {
                lit: Literal::UInt64(index),
                ..
            } = expr
            {
                let (scalar, alias) = Self::resolve_index_item(expr, *index, select_list)?;
                if let Entry::Vacant(entry) = bind_context
                    .aggregate_info
                    .group_items_map
                    .entry(scalar.clone())
                {
                    // Add group item if it's not duplicated
                    let column_binding = if let ScalarExpr::BoundColumnRef(ref column_ref) = scalar
                    {
                        column_ref.column.clone()
                    } else {
                        self.create_column_binding(None, None, None, alias, scalar.data_type()?)
                    };
                    bind_context.aggregate_info.group_items.push(ScalarItem {
                        scalar: scalar.clone(),
                        index: column_binding.index,
                    });
                    entry.insert(bind_context.aggregate_info.group_items.len() - 1);
                }
                if collect_grouping_sets && !grouping_sets.last().unwrap().contains(&scalar) {
                    grouping_sets.last_mut().unwrap().push(scalar);
                }
                continue;
            }

            // Resolve scalar item and alias item
            let mut scalar_binder = ScalarBinder::new(
                bind_context,
                self.ctx.clone(),
                &self.name_resolution_ctx,
                self.metadata.clone(),
                &[],
            );
            let (scalar_expr, _) = scalar_binder
                .bind(expr)
                .await
                .or_else(|e| Self::resolve_alias_item(bind_context, expr, available_aliases, e))?;

            if collect_grouping_sets && !grouping_sets.last().unwrap().contains(&scalar_expr) {
                grouping_sets.last_mut().unwrap().push(scalar_expr.clone());
            }

            if bind_context
                .aggregate_info
                .group_items_map
                .get(&scalar_expr)
                .is_some()
            {
                // The group key is duplicated
                continue;
            }

            let group_item_name = format!("{:#}", expr);
            let index = if let ScalarExpr::BoundColumnRef(BoundColumnRef {
                column: ColumnBinding { index, .. },
                ..
            }) = &scalar_expr
            {
                *index
            } else {
                self.metadata
                    .write()
                    .add_derived_column(group_item_name.clone(), scalar_expr.data_type()?)
            };

            bind_context.aggregate_info.group_items.push(ScalarItem {
                scalar: scalar_expr.clone(),
                index,
            });
            bind_context.aggregate_info.group_items_map.insert(
                scalar_expr,
                bind_context.aggregate_info.group_items.len() - 1,
            );
        }

        // If it's `GROUP BY GROUPING SETS`, ignore the optimization below.
        if collect_grouping_sets {
            return Ok(());
        }

        // Remove dependent group items, group by a, f(a, b), f(a), b ---> group by a,b
        let mut results = vec![];
        for item in bind_context.aggregate_info.group_items.iter() {
            let columns: HashSet<ScalarExpr> = bind_context
                .aggregate_info
                .group_items
                .iter()
                .filter(|p| p.scalar != item.scalar)
                .map(|p| p.scalar.clone())
                .collect();

            if prune_by_children(&item.scalar, &columns) {
                continue;
            }
            results.push(item.clone());
        }

        bind_context.aggregate_info.group_items_map.clear();
        for (i, item) in results.iter().enumerate() {
            bind_context
                .aggregate_info
                .group_items_map
                .insert(item.scalar.clone(), i);
        }
        bind_context.aggregate_info.group_items = results;
        Ok(())
    }

    fn resolve_index_item(
        expr: &Expr,
        index: u64,
        select_list: &SelectList,
    ) -> Result<(ScalarExpr, String)> {
        // Convert to zero-based index
        debug_assert!(index > 0);
        let index = index as usize - 1;
        if index >= select_list.items.len() {
            return Err(ErrorCode::SemanticError(format!(
                "GROUP BY position {} is not in select list",
                index + 1
            ))
            .set_span(expr.span()));
        }
        let item = select_list
            .items
            .get(index)
            .ok_or_else(|| ErrorCode::Internal("Should not fail"))?;

        let scalar = item.scalar.clone();
        let alias = item.alias.clone();

        Ok((scalar, alias))
    }
    fn resolve_alias_item(
        bind_context: &mut BindContext,
        expr: &Expr,
        available_aliases: &[(ColumnBinding, ScalarExpr)],
        original_error: ErrorCode,
    ) -> Result<(ScalarExpr, DataType)> {
        let mut result: Vec<usize> = vec![];
        // If cannot resolve group item, then try to find an available alias
        for (i, (column_binding, _)) in available_aliases.iter().enumerate() {
            // Alias of the select item
            let col_name = column_binding.column_name.as_str();
            if let Expr::ColumnRef {
                column,
                database: None,
                table: None,
                ..
            } = expr
            {
                if col_name.eq_ignore_ascii_case(column.name.as_str()) {
                    result.push(i);
                }
            }
        }

        if result.is_empty() {
            Err(original_error)
        } else if result.len() > 1 {
            Err(
                ErrorCode::SemanticError(format!("GROUP BY \"{}\" is ambiguous", expr))
                    .set_span(expr.span()),
            )
        } else {
            let (column_binding, scalar) = available_aliases[result[0]].clone();
            // We will add the alias to BindContext, so we can reference it
            // in `HAVING` and `ORDER BY` clause.
            bind_context.columns.push(column_binding.clone());

            let index = column_binding.index;
            bind_context.aggregate_info.group_items.push(ScalarItem {
                scalar: scalar.clone(),
                index,
            });
            bind_context.aggregate_info.group_items_map.insert(
                scalar.clone(),
                bind_context.aggregate_info.group_items.len() - 1,
            );

            // Add a mapping (alias -> scalar), so we can resolve the alias later
            let column_ref: ScalarExpr = BoundColumnRef {
                span: scalar.span(),
                column: column_binding,
            }
            .into();
            bind_context.aggregate_info.group_items_map.insert(
                column_ref,
                bind_context.aggregate_info.group_items.len() - 1,
            );

            Ok((scalar.clone(), scalar.data_type()?))
        }
    }
}
