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

use std::sync::Arc;

use common_catalog::table_context::TableContext;
use common_exception::ErrorCode;
use common_exception::Result;

use super::aggregate::Aggregate;
use super::dummy_table_scan::DummyTableScan;
use super::eval_scalar::EvalScalar;
use super::filter::Filter;
use super::join::Join;
use super::limit::Limit;
use super::pattern::PatternPlan;
use super::scan::Scan;
use super::sort::Sort;
use super::union_all::UnionAll;
use crate::optimizer::PhysicalProperty;
use crate::optimizer::RelExpr;
use crate::optimizer::RelationalProperty;
use crate::optimizer::RequiredProperty;
use crate::optimizer::StatInfo;
use crate::plans::runtime_filter_source::RuntimeFilterSource;
use crate::plans::Exchange;
use crate::plans::ProjectSet;
use crate::plans::Window;

pub trait Operator {
    fn rel_op(&self) -> RelOp;

    fn is_pattern(&self) -> bool {
        false
    }

    fn derive_relational_prop(&self, rel_expr: &RelExpr) -> Result<RelationalProperty>;

    fn derive_physical_prop(&self, rel_expr: &RelExpr) -> Result<PhysicalProperty>;

    fn derive_cardinality(&self, rel_expr: &RelExpr) -> Result<StatInfo>;

    fn compute_required_prop_child(
        &self,
        ctx: Arc<dyn TableContext>,
        rel_expr: &RelExpr,
        child_index: usize,
        required: &RequiredProperty,
    ) -> Result<RequiredProperty>;
}

/// Relational operator
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum RelOp {
    Scan,
    Join,
    EvalScalar,
    Filter,
    Aggregate,
    Sort,
    Limit,
    Exchange,
    UnionAll,
    DummyTableScan,
    RuntimeFilterSource,
    Window,
    ProjectSet,

    // Pattern
    Pattern,
}

/// Relational operators
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum RelOperator {
    Scan(Scan),
    Join(Join),
    EvalScalar(EvalScalar),
    Filter(Filter),
    Aggregate(Aggregate),
    Sort(Sort),
    Limit(Limit),
    Exchange(Exchange),
    UnionAll(UnionAll),
    DummyTableScan(DummyTableScan),
    RuntimeFilterSource(RuntimeFilterSource),
    Window(Window),
    ProjectSet(ProjectSet),

    Pattern(PatternPlan),
}

impl Operator for RelOperator {
    fn rel_op(&self) -> RelOp {
        match self {
            RelOperator::Scan(rel_op) => rel_op.rel_op(),
            RelOperator::Join(rel_op) => rel_op.rel_op(),
            RelOperator::EvalScalar(rel_op) => rel_op.rel_op(),
            RelOperator::Filter(rel_op) => rel_op.rel_op(),
            RelOperator::Aggregate(rel_op) => rel_op.rel_op(),
            RelOperator::Sort(rel_op) => rel_op.rel_op(),
            RelOperator::Limit(rel_op) => rel_op.rel_op(),
            RelOperator::Pattern(rel_op) => rel_op.rel_op(),
            RelOperator::Exchange(rel_op) => rel_op.rel_op(),
            RelOperator::UnionAll(rel_op) => rel_op.rel_op(),
            RelOperator::DummyTableScan(rel_op) => rel_op.rel_op(),
            RelOperator::RuntimeFilterSource(rel_op) => rel_op.rel_op(),
            RelOperator::ProjectSet(rel_op) => rel_op.rel_op(),
            RelOperator::Window(rel_op) => rel_op.rel_op(),
        }
    }

    fn derive_relational_prop(&self, rel_expr: &RelExpr) -> Result<RelationalProperty> {
        match self {
            RelOperator::Scan(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::Join(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::EvalScalar(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::Filter(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::Aggregate(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::Sort(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::Limit(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::Pattern(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::Exchange(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::UnionAll(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::DummyTableScan(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::RuntimeFilterSource(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::ProjectSet(rel_op) => rel_op.derive_relational_prop(rel_expr),
            RelOperator::Window(rel_op) => rel_op.derive_relational_prop(rel_expr),
        }
    }

    fn derive_physical_prop(&self, rel_expr: &RelExpr) -> Result<PhysicalProperty> {
        match self {
            RelOperator::Scan(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::Join(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::EvalScalar(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::Filter(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::Aggregate(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::Sort(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::Limit(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::Pattern(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::Exchange(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::UnionAll(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::DummyTableScan(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::RuntimeFilterSource(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::ProjectSet(rel_op) => rel_op.derive_physical_prop(rel_expr),
            RelOperator::Window(rel_op) => rel_op.derive_physical_prop(rel_expr),
        }
    }

    fn derive_cardinality(&self, rel_expr: &RelExpr) -> Result<StatInfo> {
        match self {
            RelOperator::Scan(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::Join(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::EvalScalar(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::Filter(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::Aggregate(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::Sort(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::Limit(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::Pattern(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::Exchange(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::UnionAll(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::DummyTableScan(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::RuntimeFilterSource(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::ProjectSet(rel_op) => rel_op.derive_cardinality(rel_expr),
            RelOperator::Window(rel_op) => rel_op.derive_cardinality(rel_expr),
        }
    }

    fn compute_required_prop_child(
        &self,
        ctx: Arc<dyn TableContext>,
        rel_expr: &RelExpr,
        child_index: usize,
        required: &RequiredProperty,
    ) -> Result<RequiredProperty> {
        match self {
            RelOperator::Scan(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::Join(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::EvalScalar(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::Filter(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::Aggregate(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::Sort(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::Limit(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::Pattern(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::Exchange(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::UnionAll(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::DummyTableScan(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::RuntimeFilterSource(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::Window(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
            RelOperator::ProjectSet(rel_op) => {
                rel_op.compute_required_prop_child(ctx, rel_expr, child_index, required)
            }
        }
    }
}

impl From<Scan> for RelOperator {
    fn from(v: Scan) -> Self {
        Self::Scan(v)
    }
}

impl TryFrom<RelOperator> for Scan {
    type Error = ErrorCode;

    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::Scan(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal(
                "Cannot downcast RelOperator to LogicalGet",
            ))
        }
    }
}

impl From<Join> for RelOperator {
    fn from(v: Join) -> Self {
        Self::Join(v)
    }
}

impl TryFrom<RelOperator> for Join {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::Join(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal(
                "Cannot downcast RelOperator to LogicalJoin",
            ))
        }
    }
}

impl From<EvalScalar> for RelOperator {
    fn from(v: EvalScalar) -> Self {
        Self::EvalScalar(v)
    }
}

impl TryFrom<RelOperator> for EvalScalar {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::EvalScalar(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal(
                "Cannot downcast RelOperator to EvalScalar",
            ))
        }
    }
}

impl From<Filter> for RelOperator {
    fn from(v: Filter) -> Self {
        Self::Filter(v)
    }
}

impl TryFrom<RelOperator> for Filter {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::Filter(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal("Cannot downcast RelOperator to Filter"))
        }
    }
}

impl From<Aggregate> for RelOperator {
    fn from(v: Aggregate) -> Self {
        Self::Aggregate(v)
    }
}

impl TryFrom<RelOperator> for Aggregate {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::Aggregate(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal(
                "Cannot downcast RelOperator to Aggregate",
            ))
        }
    }
}

impl From<Window> for RelOperator {
    fn from(v: Window) -> Self {
        Self::Window(v)
    }
}

impl TryFrom<RelOperator> for Window {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::Window(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal("Cannot downcast RelOperator to Window"))
        }
    }
}

impl From<Sort> for RelOperator {
    fn from(v: Sort) -> Self {
        Self::Sort(v)
    }
}

impl TryFrom<RelOperator> for Sort {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::Sort(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal("Cannot downcast RelOperator to Sort"))
        }
    }
}

impl From<Limit> for RelOperator {
    fn from(v: Limit) -> Self {
        Self::Limit(v)
    }
}

impl TryFrom<RelOperator> for Limit {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::Limit(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal("Cannot downcast RelOperator to Limit"))
        }
    }
}

impl From<PatternPlan> for RelOperator {
    fn from(v: PatternPlan) -> Self {
        Self::Pattern(v)
    }
}

impl TryFrom<RelOperator> for PatternPlan {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::Pattern(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal(
                "Cannot downcast RelOperator to Pattern",
            ))
        }
    }
}

impl From<Exchange> for RelOperator {
    fn from(v: Exchange) -> Self {
        Self::Exchange(v)
    }
}

impl TryFrom<RelOperator> for Exchange {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::Exchange(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal(
                "Cannot downcast RelOperator to Exchange",
            ))
        }
    }
}

impl From<UnionAll> for RelOperator {
    fn from(v: UnionAll) -> Self {
        Self::UnionAll(v)
    }
}

impl TryFrom<RelOperator> for UnionAll {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::UnionAll(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal(
                "Cannot downcast RelOperator to UnionAll",
            ))
        }
    }
}

impl From<DummyTableScan> for RelOperator {
    fn from(v: DummyTableScan) -> Self {
        Self::DummyTableScan(v)
    }
}

impl TryFrom<RelOperator> for DummyTableScan {
    type Error = ErrorCode;
    fn try_from(value: RelOperator) -> Result<Self> {
        if let RelOperator::DummyTableScan(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal(
                "Cannot downcast RelOperator to DummyTableScan",
            ))
        }
    }
}

impl From<RuntimeFilterSource> for RelOperator {
    fn from(value: RuntimeFilterSource) -> Self {
        Self::RuntimeFilterSource(value)
    }
}

impl TryFrom<RelOperator> for RuntimeFilterSource {
    type Error = ErrorCode;

    fn try_from(value: RelOperator) -> std::result::Result<Self, Self::Error> {
        if let RelOperator::RuntimeFilterSource(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal(
                "Cannot downcast RelOperator to RuntimeFilterSource",
            ))
        }
    }
}

impl From<ProjectSet> for RelOperator {
    fn from(value: ProjectSet) -> Self {
        Self::ProjectSet(value)
    }
}

impl TryFrom<RelOperator> for ProjectSet {
    type Error = ErrorCode;

    fn try_from(value: RelOperator) -> std::result::Result<Self, Self::Error> {
        if let RelOperator::ProjectSet(value) = value {
            Ok(value)
        } else {
            Err(ErrorCode::Internal(
                "Cannot downcast RelOperator to ProjectSet",
            ))
        }
    }
}
