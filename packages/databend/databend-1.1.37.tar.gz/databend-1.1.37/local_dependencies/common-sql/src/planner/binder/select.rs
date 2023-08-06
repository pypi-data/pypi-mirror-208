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

use std::collections::HashMap;
use std::collections::HashSet;

use async_recursion::async_recursion;
use common_ast::ast::BinaryOperator;
use common_ast::ast::Expr;
use common_ast::ast::Expr::Array;
use common_ast::ast::GroupBy;
use common_ast::ast::Identifier;
use common_ast::ast::Join;
use common_ast::ast::JoinCondition;
use common_ast::ast::JoinOperator;
use common_ast::ast::Literal;
use common_ast::ast::OrderByExpr;
use common_ast::ast::Query;
use common_ast::ast::SelectStmt;
use common_ast::ast::SelectTarget;
use common_ast::ast::SetExpr;
use common_ast::ast::SetOperator;
use common_ast::ast::TableReference;
use common_ast::ast::Window;
use common_ast::ast::WindowSpec;
use common_exception::ErrorCode;
use common_exception::Result;
use common_exception::Span;
use tracing::warn;

use super::sort::OrderItem;
use crate::binder::join::JoinConditions;
use crate::binder::project_set::SrfCollector;
use crate::binder::scalar_common::split_conjunctions;
use crate::binder::CteInfo;
use crate::binder::ExprContext;
use crate::optimizer::SExpr;
use crate::planner::binder::scalar::ScalarBinder;
use crate::planner::binder::BindContext;
use crate::planner::binder::Binder;
use crate::plans::BoundColumnRef;
use crate::plans::Filter;
use crate::plans::JoinType;
use crate::plans::ScalarExpr;
use crate::plans::ScalarItem;
use crate::plans::UnionAll;
use crate::ColumnBinding;
use crate::ColumnEntry;
use crate::IndexType;

// A normalized IR for `SELECT` clause.
#[derive(Debug, Default)]
pub struct SelectList<'a> {
    pub items: Vec<SelectItem<'a>>,
}

#[derive(Debug)]
pub struct SelectItem<'a> {
    pub select_target: &'a SelectTarget,
    pub scalar: ScalarExpr,
    pub alias: String,
}

impl Binder {
    #[async_backtrace::framed]
    pub(super) async fn bind_select_stmt(
        &mut self,
        bind_context: &mut BindContext,
        stmt: &SelectStmt,
        order_by: &[OrderByExpr],
        limit: usize,
    ) -> Result<(SExpr, BindContext)> {
        if let Some(hints) = &stmt.hints {
            if let Some(e) = self.opt_hints_set_var(bind_context, hints).await.err() {
                warn!(
                    "In SELECT resolve optimize hints {:?} failed, err: {:?}",
                    hints, e
                );
            }
        }
        let (mut s_expr, mut from_context) = if stmt.from.is_empty() {
            self.bind_one_table(bind_context, stmt).await?
        } else {
            let cross_joins = stmt
                .from
                .iter()
                .cloned()
                .reduce(|left, right| TableReference::Join {
                    span: None,
                    join: Join {
                        op: JoinOperator::CrossJoin,
                        condition: JoinCondition::None,
                        left: Box::new(left),
                        right: Box::new(right),
                    },
                })
                .unwrap();
            self.bind_table_reference(bind_context, &cross_joins)
                .await?
        };

        let mut rewriter = SelectRewriter::new(
            from_context.all_column_bindings(),
            self.name_resolution_ctx.unquoted_ident_case_sensitive,
        );
        let (new_stmt, new_order_by) = rewriter.rewrite(stmt, order_by)?;
        let stmt = new_stmt.as_ref().unwrap_or(stmt);
        let order_by = new_order_by.as_deref().unwrap_or(order_by);

        // Collect set returning functions
        let set_returning_functions = {
            let mut collector = SrfCollector::new();
            stmt.select_list.iter().for_each(|item| {
                if let SelectTarget::AliasedExpr { expr, .. } = item {
                    collector.visit(expr);
                }
            });
            collector.into_srfs()
        };

        // Bind set returning functions
        s_expr = self
            .bind_project_set(&mut from_context, &set_returning_functions, s_expr)
            .await?;

        // Generate a analyzed select list with from context
        let mut select_list = self
            .normalize_select_list(&mut from_context, &stmt.select_list)
            .await?;

        // This will potentially add some alias group items to `from_context` if find some.
        if let Some(group_by) = stmt.group_by.as_ref() {
            self.analyze_group_items(&mut from_context, &select_list, group_by)
                .await?;
        }

        self.analyze_aggregate_select(&mut from_context, &mut select_list)?;

        // `analyze_window` should behind `analyze_aggregate_select`,
        // because `analyze_window` will rewrite the aggregate functions in the window function's arguments.
        self.analyze_window(&mut from_context, &mut select_list)?;

        let aliases = select_list
            .items
            .iter()
            .map(|item| (item.alias.clone(), item.scalar.clone()))
            .collect::<Vec<_>>();

        // To support using aliased column in `WHERE` clause,
        // we should bind where after `select_list` is rewritten.
        let where_scalar = if let Some(expr) = &stmt.selection {
            let (new_expr, scalar) = self
                .bind_where(&mut from_context, &aliases, expr, s_expr)
                .await?;
            s_expr = new_expr;
            Some(scalar)
        } else {
            None
        };

        // `analyze_projection` should behind `analyze_aggregate_select` because `analyze_aggregate_select` will rewrite `grouping`.
        let (mut scalar_items, projections) =
            self.analyze_projection(&from_context, &select_list)?;

        let having = if let Some(having) = &stmt.having {
            Some(
                self.analyze_aggregate_having(&mut from_context, &aliases, having)
                    .await?,
            )
        } else {
            None
        };

        let order_items = self
            .analyze_order_items(
                &mut from_context,
                &mut scalar_items,
                &aliases,
                &projections,
                order_by,
                stmt.distinct,
            )
            .await?;

        // After all analysis is done.
        if set_returning_functions.is_empty() {
            // Ignore SRFs.
            self.analyze_lazy_materialization(
                &from_context,
                stmt,
                &scalar_items,
                &select_list,
                &where_scalar,
                &order_items.items,
                limit,
            )?;
        }

        if !from_context.aggregate_info.aggregate_functions.is_empty()
            || !from_context.aggregate_info.group_items.is_empty()
        {
            s_expr = self.bind_aggregate(&mut from_context, s_expr).await?;
        }

        if let Some((having, span)) = having {
            s_expr = self
                .bind_having(&mut from_context, having, span, s_expr)
                .await?;
        }

        // bind window
        // window run after the HAVING clause but before the ORDER BY clause.
        for window_info in &from_context.windows.window_functions {
            s_expr = self.bind_window_function(window_info, s_expr).await?;
        }

        if stmt.distinct {
            s_expr = self.bind_distinct(
                stmt.span,
                &from_context,
                &projections,
                &mut scalar_items,
                s_expr,
            )?;
        }

        if !order_by.is_empty() {
            s_expr = self
                .bind_order_by(
                    &from_context,
                    order_items,
                    &select_list,
                    &mut scalar_items,
                    s_expr,
                )
                .await?;
        }

        s_expr = self.bind_projection(&mut from_context, &projections, &scalar_items, s_expr)?;

        // add internal column binding into expr
        s_expr = from_context.add_internal_column_into_expr(s_expr);

        let mut output_context = BindContext::new();
        output_context.parent = from_context.parent;
        output_context.columns = from_context.columns;
        output_context.ctes_map = from_context.ctes_map;

        Ok((s_expr, output_context))
    }

    #[async_recursion]
    #[async_backtrace::framed]
    pub(crate) async fn bind_set_expr(
        &mut self,
        bind_context: &mut BindContext,
        set_expr: &SetExpr,
        order_by: &[OrderByExpr],
        limit: usize,
    ) -> Result<(SExpr, BindContext)> {
        match set_expr {
            SetExpr::Select(stmt) => {
                self.bind_select_stmt(bind_context, stmt, order_by, limit)
                    .await
            }
            SetExpr::Query(stmt) => self.bind_query(bind_context, stmt).await,
            SetExpr::SetOperation(set_operation) => {
                self.bind_set_operator(
                    bind_context,
                    &set_operation.left,
                    &set_operation.right,
                    &set_operation.op,
                    &set_operation.all,
                )
                .await
            }
        }
    }

    #[async_recursion]
    #[async_backtrace::framed]
    pub(crate) async fn bind_query(
        &mut self,
        bind_context: &mut BindContext,
        query: &Query,
    ) -> Result<(SExpr, BindContext)> {
        if let Some(with) = &query.with {
            for cte in with.ctes.iter() {
                let table_name = cte.alias.name.name.clone();
                if bind_context.ctes_map.contains_key(&table_name) {
                    return Err(ErrorCode::SemanticError(format!(
                        "duplicate cte {table_name}"
                    )));
                }
                let cte_info = CteInfo {
                    columns_alias: cte.alias.columns.iter().map(|c| c.name.clone()).collect(),
                    query: cte.query.clone(),
                };
                bind_context.ctes_map.insert(table_name, cte_info);
            }
        }

        let (limit, offset) = if !query.limit.is_empty() {
            if query.limit.len() == 1 {
                Self::analyze_limit(Some(&query.limit[0]), &query.offset)?
            } else {
                Self::analyze_limit(Some(&query.limit[1]), &Some(query.limit[0].clone()))?
            }
        } else if query.offset.is_some() {
            Self::analyze_limit(None, &query.offset)?
        } else {
            (None, 0)
        };

        let (mut s_expr, bind_context) = match query.body {
            SetExpr::Select(_) | SetExpr::Query(_) => {
                self.bind_set_expr(
                    bind_context,
                    &query.body,
                    &query.order_by,
                    limit.unwrap_or_default(),
                )
                .await?
            }
            SetExpr::SetOperation(_) => {
                let (mut s_expr, mut bind_context) = self
                    .bind_set_expr(bind_context, &query.body, &[], limit.unwrap_or_default())
                    .await?;
                if !query.order_by.is_empty() {
                    s_expr = self
                        .bind_order_by_for_set_operation(&mut bind_context, s_expr, &query.order_by)
                        .await?;
                }
                (s_expr, bind_context)
            }
        };

        if !query.limit.is_empty() || query.offset.is_some() {
            s_expr = Self::bind_limit(s_expr, limit, offset);
        }

        Ok((s_expr, bind_context))
    }

    #[async_backtrace::framed]
    pub(super) async fn bind_where(
        &mut self,
        bind_context: &mut BindContext,
        aliases: &[(String, ScalarExpr)],
        expr: &Expr,
        child: SExpr,
    ) -> Result<(SExpr, ScalarExpr)> {
        let last_expr_context = bind_context.expr_context.clone();
        bind_context.set_expr_context(ExprContext::WhereClause);

        let mut scalar_binder = ScalarBinder::new(
            bind_context,
            self.ctx.clone(),
            &self.name_resolution_ctx,
            self.metadata.clone(),
            aliases,
        );
        let (scalar, _) = scalar_binder.bind(expr).await?;
        let filter_plan = Filter {
            predicates: split_conjunctions(&scalar),
            is_having: false,
        };
        let new_expr = SExpr::create_unary(filter_plan.into(), child);
        bind_context.set_expr_context(last_expr_context);
        Ok((new_expr, scalar))
    }

    #[async_backtrace::framed]
    pub(super) async fn bind_set_operator(
        &mut self,
        bind_context: &mut BindContext,
        left: &SetExpr,
        right: &SetExpr,
        op: &SetOperator,
        all: &bool,
    ) -> Result<(SExpr, BindContext)> {
        let (left_expr, left_bind_context) = self.bind_set_expr(bind_context, left, &[], 0).await?;
        let (right_expr, right_bind_context) =
            self.bind_set_expr(bind_context, right, &[], 0).await?;

        if left_bind_context.columns.len() != right_bind_context.columns.len() {
            return Err(ErrorCode::SemanticError(
                "SetOperation must have the same number of columns",
            ));
        }

        match (op, all) {
            (SetOperator::Intersect, false) => {
                // Transfer Intersect to Semi join
                self.bind_intersect(
                    left.span(),
                    right.span(),
                    left_bind_context,
                    right_bind_context,
                    left_expr,
                    right_expr,
                )
            }
            (SetOperator::Except, false) => {
                // Transfer Except to Anti join
                self.bind_except(
                    left.span(),
                    right.span(),
                    left_bind_context,
                    right_bind_context,
                    left_expr,
                    right_expr,
                )
            }
            (SetOperator::Union, true) => self.bind_union(
                left.span(),
                right.span(),
                left_bind_context,
                right_bind_context,
                left_expr,
                right_expr,
                false,
            ),
            (SetOperator::Union, false) => self.bind_union(
                left.span(),
                right.span(),
                left_bind_context,
                right_bind_context,
                left_expr,
                right_expr,
                true,
            ),
            _ => Err(ErrorCode::Unimplemented(
                "Unsupported query type, currently, databend only support intersect distinct and except distinct",
            )),
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn bind_union(
        &mut self,
        left_span: Span,
        _right_span: Span,
        left_context: BindContext,
        right_context: BindContext,
        left_expr: SExpr,
        right_expr: SExpr,
        distinct: bool,
    ) -> Result<(SExpr, BindContext)> {
        let pairs = left_context
            .columns
            .iter()
            .zip(right_context.columns.iter())
            .map(|(l, r)| (l.index, r.index))
            .collect();

        let union_plan = UnionAll { pairs };
        let mut new_expr = SExpr::create_binary(union_plan.into(), left_expr, right_expr);

        if distinct {
            new_expr = self.bind_distinct(
                left_span,
                &left_context,
                left_context.all_column_bindings(),
                &mut HashMap::new(),
                new_expr,
            )?;
        }

        Ok((new_expr, left_context))
    }

    fn bind_intersect(
        &mut self,
        left_span: Span,
        right_span: Span,
        left_context: BindContext,
        right_context: BindContext,
        left_expr: SExpr,
        right_expr: SExpr,
    ) -> Result<(SExpr, BindContext)> {
        self.bind_intersect_or_except(
            left_span,
            right_span,
            left_context,
            right_context,
            left_expr,
            right_expr,
            JoinType::LeftSemi,
        )
    }

    fn bind_except(
        &mut self,
        left_span: Span,
        right_span: Span,
        left_context: BindContext,
        right_context: BindContext,
        left_expr: SExpr,
        right_expr: SExpr,
    ) -> Result<(SExpr, BindContext)> {
        self.bind_intersect_or_except(
            left_span,
            right_span,
            left_context,
            right_context,
            left_expr,
            right_expr,
            JoinType::LeftAnti,
        )
    }

    #[allow(clippy::too_many_arguments)]
    fn bind_intersect_or_except(
        &mut self,
        left_span: Span,
        right_span: Span,
        left_context: BindContext,
        right_context: BindContext,
        left_expr: SExpr,
        right_expr: SExpr,
        join_type: JoinType,
    ) -> Result<(SExpr, BindContext)> {
        let left_expr = self.bind_distinct(
            left_span,
            &left_context,
            left_context.all_column_bindings(),
            &mut HashMap::new(),
            left_expr,
        )?;
        let mut left_conditions = Vec::with_capacity(left_context.columns.len());
        let mut right_conditions = Vec::with_capacity(right_context.columns.len());
        assert_eq!(left_context.columns.len(), right_context.columns.len());
        for (left_column, right_column) in left_context
            .columns
            .iter()
            .zip(right_context.columns.iter())
        {
            left_conditions.push(
                BoundColumnRef {
                    span: left_span,
                    column: left_column.clone(),
                }
                .into(),
            );
            right_conditions.push(
                BoundColumnRef {
                    span: right_span,
                    column: right_column.clone(),
                }
                .into(),
            );
        }
        let join_conditions = JoinConditions {
            left_conditions,
            right_conditions,
            non_equi_conditions: vec![],
            other_conditions: vec![],
        };
        let s_expr = self.bind_join_with_type(join_type, join_conditions, left_expr, right_expr)?;
        Ok((s_expr, left_context))
    }

    #[allow(clippy::too_many_arguments)]
    fn analyze_lazy_materialization(
        &self,
        bind_context: &BindContext,
        stmt: &SelectStmt,
        scalar_items: &HashMap<IndexType, ScalarItem>,
        select_list: &SelectList,
        where_scalar: &Option<ScalarExpr>,
        order_by: &[OrderItem],
        limit: usize,
    ) -> Result<()> {
        // Only simple single table Top-N query is supported.
        // e.g.
        // SELECT ... FROM t WHERE ... ORDER BY ... LIMIT ...
        if stmt.group_by.is_some()
            || stmt.having.is_some()
            || stmt.distinct
            || !bind_context.ctes_map.is_empty()
            || !bind_context.aggregate_info.group_items.is_empty()
            || !bind_context.aggregate_info.aggregate_functions.is_empty()
        {
            return Ok(());
        }

        let limit_threadhold = self.ctx.get_settings().get_lazy_topn_threshold()? as usize;

        if !(!order_by.is_empty() && limit > 0 && limit <= limit_threadhold) {
            return Ok(());
        }

        let mut metadata = self.metadata.write();
        if metadata.tables().len() != 1 {
            // Only support single table query.
            return Ok(());
        }

        if !metadata.table(0).table().support_row_id_column() {
            return Ok(());
        }

        let cols = metadata.columns();

        let virtual_cols = cols
            .iter()
            .filter(|col| matches!(col, ColumnEntry::VirtualColumn(_)))
            .map(|col| col.index())
            .collect::<Vec<_>>();

        if !virtual_cols.is_empty() {
            // Virtual columns are not supported now.
            return Ok(());
        }

        let mut select_cols = HashSet::with_capacity(select_list.items.len());
        for s in select_list.items.iter() {
            select_cols.extend(s.scalar.used_columns())
        }

        let mut order_by_cols = HashSet::with_capacity(order_by.len());
        for o in order_by {
            if let Some(scalar) = scalar_items.get(&o.index) {
                let cols = scalar.scalar.used_columns();
                order_by_cols.extend(cols);
            } else {
                // Is a col ref not appears in select list.
                order_by_cols.insert(o.index);
            }
        }

        let where_cols = where_scalar
            .as_ref()
            .map(|w| w.used_columns())
            .unwrap_or_default();

        let internal_cols = cols
            .iter()
            .filter(|col| matches!(col, ColumnEntry::InternalColumn(_)))
            .map(|col| col.index())
            .collect::<HashSet<_>>();

        let mut non_lazy_cols = order_by_cols;
        non_lazy_cols.extend(where_cols);
        non_lazy_cols.extend(internal_cols);

        let lazy_cols = select_cols.difference(&non_lazy_cols).copied().collect();
        metadata.add_lazy_columns(lazy_cols);

        Ok(())
    }
}

/// It is useful when implementing some SQL syntax sugar,
///
/// [`column_binding`] contains the column binding information of the SelectStmt.
///
/// to rewrite the SelectStmt, just add a new rewrite_* function and call it in the `rewrite` function.
struct SelectRewriter<'a> {
    column_binding: &'a [ColumnBinding],
    new_stmt: Option<SelectStmt>,
    new_order_by: Option<Vec<OrderByExpr>>,
    is_unquoted_ident_case_sensitive: bool,
}

// helper functions to SelectRewriter
impl<'a> SelectRewriter<'a> {
    fn compare_unquoted_ident(&self, a: &str, b: &str) -> bool {
        if self.is_unquoted_ident_case_sensitive {
            a == b
        } else {
            a.eq_ignore_ascii_case(b)
        }
    }
    fn parse_aggregate_function(expr: &Expr) -> Result<(&Identifier, &[Expr])> {
        match expr {
            Expr::FunctionCall { name, args, .. } => Ok((name, args)),
            _ => Err(ErrorCode::SyntaxException("Aggregate function is required")),
        }
    }

    fn ident_from_string(s: &str) -> Identifier {
        Identifier {
            name: s.to_string(),
            quote: None,
            span: None,
        }
    }

    fn expr_eq_from_col_and_value(col: Identifier, value: Expr) -> Expr {
        Expr::BinaryOp {
            span: None,
            left: Box::new(Expr::ColumnRef {
                column: col,
                span: None,
                database: None,
                table: None,
            }),
            op: BinaryOperator::Eq,
            right: Box::new(value),
        }
    }

    fn target_func_from_name_args(
        name: Identifier,
        args: Vec<Expr>,
        alias: Option<Identifier>,
    ) -> SelectTarget {
        SelectTarget::AliasedExpr {
            expr: Box::new(Expr::FunctionCall {
                span: Span::default(),
                distinct: false,
                name,
                args,
                params: vec![],
                window: None,
            }),
            alias,
        }
    }

    fn expr_literal_array_from_vec_ident(exprs: Vec<Identifier>) -> Expr {
        Array {
            span: Span::default(),
            exprs: exprs
                .into_iter()
                .map(|expr| Expr::Literal {
                    span: None,
                    lit: Literal::String(expr.name),
                })
                .collect(),
        }
    }

    fn expr_column_ref_array_from_vec_ident(exprs: Vec<Identifier>) -> Expr {
        Array {
            span: Span::default(),
            exprs: exprs
                .into_iter()
                .map(|expr| Expr::ColumnRef {
                    span: None,
                    column: expr,
                    database: None,
                    table: None,
                })
                .collect(),
        }
    }

    // For Expr::Literal, expr.to_string() is quoted, sometimes we need the raw string.
    fn raw_string_from_literal_expr(expr: &Expr) -> Option<String> {
        match expr {
            Expr::Literal { lit, .. } => match lit {
                Literal::String(v) => Some(v.clone()),
                _ => Some(expr.to_string()),
            },
            _ => None,
        }
    }
}

impl<'a> SelectRewriter<'a> {
    fn new(column_binding: &'a [ColumnBinding], is_unquoted_ident_case_sensitive: bool) -> Self {
        SelectRewriter {
            column_binding,
            new_stmt: None,
            new_order_by: None,
            is_unquoted_ident_case_sensitive,
        }
    }

    fn rewrite(
        &mut self,
        stmt: &SelectStmt,
        order_by: &[OrderByExpr],
    ) -> Result<(Option<SelectStmt>, Option<Vec<OrderByExpr>>)> {
        self.rewrite_window_references(stmt, order_by)?;
        self.rewrite_pivot(stmt)?;
        self.rewrite_unpivot(stmt)?;
        Ok((self.new_stmt.take(), self.new_order_by.take()))
    }

    fn rewrite_pivot(&mut self, stmt: &SelectStmt) -> Result<()> {
        if stmt.from.len() != 1 || stmt.from[0].pivot().is_none() {
            return Ok(());
        }
        let pivot = stmt.from[0].pivot().unwrap();
        let (aggregate_name, aggregate_args) = Self::parse_aggregate_function(&pivot.aggregate)?;
        let aggregate_columns = aggregate_args
            .iter()
            .map(|expr| match expr {
                Expr::ColumnRef { column, .. } => Some(column.clone()),
                _ => None,
            })
            .collect::<Option<Vec<_>>>()
            .ok_or_else(|| ErrorCode::SyntaxException("Aggregate column not found"))?;
        let aggregate_column_names = aggregate_columns
            .iter()
            .map(|col| col.name.as_str())
            .collect::<Vec<_>>();
        let new_group_by = stmt.group_by.clone().unwrap_or_else(|| {
            GroupBy::Normal(
                self.column_binding
                    .iter()
                    .filter(|col_bind| {
                        !self
                            .compare_unquoted_ident(&col_bind.column_name, &pivot.value_column.name)
                            && !aggregate_column_names
                                .iter()
                                .any(|col| self.compare_unquoted_ident(col, &col_bind.column_name))
                    })
                    .map(|col| Expr::Literal {
                        span: Span::default(),
                        lit: Literal::UInt64(col.index as u64 + 1),
                    })
                    .collect(),
            )
        });

        let mut new_select_list = stmt.select_list.clone();
        if let Some(star) = new_select_list.iter_mut().find(|target| target.is_star()) {
            let mut exclude_columns = aggregate_columns;
            exclude_columns.push(pivot.value_column.clone());
            star.exclude(exclude_columns);
        };
        let new_aggregate_name = Identifier {
            name: format!("{}_if", aggregate_name.name),
            ..aggregate_name.clone()
        };
        for value in &pivot.values {
            let mut args = aggregate_args.to_vec();
            args.push(Self::expr_eq_from_col_and_value(
                pivot.value_column.clone(),
                value.clone(),
            ));
            let alias = Self::raw_string_from_literal_expr(value)
                .ok_or_else(|| ErrorCode::SyntaxException("Pivot value should be literal"))?;
            new_select_list.push(Self::target_func_from_name_args(
                new_aggregate_name.clone(),
                args,
                Some(Self::ident_from_string(&alias)),
            ));
        }

        if let Some(ref mut new_stmt) = self.new_stmt {
            new_stmt.select_list = new_select_list;
            new_stmt.group_by = Some(new_group_by);
        } else {
            self.new_stmt = Some(SelectStmt {
                select_list: new_select_list,
                group_by: Some(new_group_by),
                ..stmt.clone()
            });
        }
        Ok(())
    }

    fn rewrite_unpivot(&mut self, stmt: &SelectStmt) -> Result<()> {
        if stmt.from.len() != 1 || stmt.from[0].unpivot().is_none() {
            return Ok(());
        }
        let unpivot = stmt.from[0].unpivot().unwrap();
        let mut new_select_list = stmt.select_list.clone();
        if let Some(star) = new_select_list.iter_mut().find(|target| target.is_star()) {
            star.exclude(unpivot.names.clone());
        };
        new_select_list.push(Self::target_func_from_name_args(
            Self::ident_from_string("unnest"),
            vec![Self::expr_literal_array_from_vec_ident(
                unpivot.names.clone(),
            )],
            Some(unpivot.column_name.clone()),
        ));
        new_select_list.push(Self::target_func_from_name_args(
            Self::ident_from_string("unnest"),
            vec![Self::expr_column_ref_array_from_vec_ident(
                unpivot.names.clone(),
            )],
            Some(unpivot.value_column.clone()),
        ));

        if let Some(ref mut new_stmt) = self.new_stmt {
            new_stmt.select_list = new_select_list;
        } else {
            self.new_stmt = Some(SelectStmt {
                select_list: new_select_list,
                ..stmt.clone()
            });
        };
        Ok(())
    }

    fn rewrite_window_references(
        &mut self,
        stmt: &SelectStmt,
        order_by: &[OrderByExpr],
    ) -> Result<()> {
        if stmt.window_list.is_none() {
            return Ok(());
        }
        let (window_specs, mut resolved_window_specs) = self.extract_window_definitions(stmt)?;

        let mut window_definitions = HashMap::with_capacity(window_specs.len());

        for (name, spec) in window_specs.iter() {
            let new_spec = Self::rewrite_inherited_window_spec(
                spec,
                &window_specs,
                &mut resolved_window_specs,
            )?;
            window_definitions.insert(name.clone(), new_spec);
        }

        let mut new_select_list = stmt.select_list.clone();
        for target in &mut new_select_list {
            match target {
                SelectTarget::AliasedExpr { expr, .. } => match expr {
                    box Expr::FunctionCall { window, .. } => {
                        if let Some(window) = window {
                            match window {
                                Window::WindowReference(reference) => {
                                    let window_spec = window_definitions
                                        .get(&reference.window_name.name)
                                        .ok_or_else(|| {
                                            ErrorCode::SyntaxException("Window not found")
                                        })?;
                                    *window = Window::WindowSpec(WindowSpec {
                                        existing_window_name: None,
                                        partition_by: window_spec.partition_by.clone(),
                                        order_by: window_spec.order_by.clone(),
                                        window_frame: window_spec.window_frame.clone(),
                                    });
                                }
                                Window::WindowSpec(_) => continue,
                            }
                        }
                    }
                    _ => continue,
                },
                SelectTarget::QualifiedName { .. } => {}
            }
        }

        if !order_by.is_empty() {
            let mut new_order_by = order_by.to_vec();
            for order in &mut new_order_by {
                match &mut order.expr {
                    Expr::FunctionCall { window, .. } => {
                        if let Some(window) = window {
                            match window {
                                Window::WindowReference(reference) => {
                                    let window_spec = window_definitions
                                        .get(&reference.window_name.name)
                                        .ok_or_else(|| {
                                            ErrorCode::SyntaxException("Window not found")
                                        })?;
                                    *window = Window::WindowSpec(WindowSpec {
                                        existing_window_name: None,
                                        partition_by: window_spec.partition_by.clone(),
                                        order_by: window_spec.order_by.clone(),
                                        window_frame: window_spec.window_frame.clone(),
                                    });
                                }
                                Window::WindowSpec(_) => continue,
                            }
                        }
                    }
                    _ => continue,
                }
            }
            self.new_order_by = Some(new_order_by);
        }

        if let Some(ref mut new_stmt) = self.new_stmt {
            new_stmt.select_list = new_select_list;
        } else {
            self.new_stmt = Some(SelectStmt {
                select_list: new_select_list,
                ..stmt.clone()
            });
        };
        Ok(())
    }

    fn extract_window_definitions(
        &mut self,
        stmt: &SelectStmt,
    ) -> Result<(HashMap<String, WindowSpec>, HashMap<String, WindowSpec>)> {
        let mut window_specs = HashMap::new();
        let mut resolved_window_specs = HashMap::new();
        for window in stmt.window_list.as_ref().unwrap() {
            window_specs.insert(window.name.name.clone(), window.spec.clone());
            if window.spec.existing_window_name.is_none() {
                resolved_window_specs.insert(window.name.name.clone(), window.spec.clone());
            }
        }
        if let Some(ref mut new_stmt) = self.new_stmt {
            new_stmt.window_list = None;
        } else {
            self.new_stmt = Some(SelectStmt {
                window_list: None,
                ..stmt.clone()
            });
        };
        Ok((window_specs, resolved_window_specs))
    }

    fn rewrite_inherited_window_spec(
        window_spec: &WindowSpec,
        window_list: &HashMap<String, WindowSpec>,
        resolved_window: &mut HashMap<String, WindowSpec>,
    ) -> Result<WindowSpec> {
        if window_spec.existing_window_name.is_some() {
            let referenced_name = window_spec
                .existing_window_name
                .as_ref()
                .unwrap()
                .name
                .clone();
            // check if spec is resolved first, so that we no need to resolve again.
            let referenced_window_spec = {
                resolved_window.get(&referenced_name).unwrap_or(
                    window_list
                        .get(&referenced_name)
                        .ok_or_else(|| ErrorCode::SyntaxException("Referenced window not found"))?,
                )
            }
            .clone();

            let resolved_spec = match referenced_window_spec.existing_window_name.clone() {
                Some(_) => Self::rewrite_inherited_window_spec(
                    &referenced_window_spec,
                    window_list,
                    resolved_window,
                )?,
                None => referenced_window_spec.clone(),
            };

            // add to resolved.
            resolved_window.insert(referenced_name, resolved_spec.clone());

            // check semantic
            if !window_spec.partition_by.is_empty() {
                return Err(ErrorCode::SemanticError(
                    "WINDOW specification with named WINDOW reference cannot specify PARTITION BY",
                ));
            }
            if !window_spec.order_by.is_empty() && !resolved_spec.order_by.is_empty() {
                return Err(ErrorCode::SemanticError(
                    "Cannot specify ORDER BY if referenced named WINDOW specifies ORDER BY",
                ));
            }
            if resolved_spec.window_frame.is_some() {
                return Err(ErrorCode::SemanticError(
                    "Cannot reference named WINDOW containing frame specification",
                ));
            }

            // resolve referenced window
            let mut partition_by = window_spec.partition_by.clone();
            if !resolved_spec.partition_by.is_empty() {
                partition_by = resolved_spec.partition_by.clone();
            }

            let mut order_by = window_spec.order_by.clone();
            if order_by.is_empty() && !resolved_spec.order_by.is_empty() {
                order_by = resolved_spec.order_by.clone();
            }

            let mut window_frame = window_spec.window_frame.clone();
            if window_frame.is_none() && resolved_spec.window_frame.is_some() {
                window_frame = resolved_spec.window_frame;
            }

            // replace with new window spec
            let new_window_spec = WindowSpec {
                existing_window_name: None,
                partition_by,
                order_by,
                window_frame,
            };
            Ok(new_window_spec)
        } else {
            Ok(window_spec.clone())
        }
    }
}
