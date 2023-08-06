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

use crate::optimizer::MExpr;
use crate::optimizer::Memo;
use crate::optimizer::PhysicalProperty;
use crate::optimizer::RelationalProperty;
use crate::optimizer::RequiredProperty;
use crate::optimizer::SExpr;
use crate::optimizer::StatInfo;
use crate::plans::Operator;
use crate::IndexType;

/// A helper to access children of `SExpr` and `MExpr` in
/// a unified view.
pub enum RelExpr<'a> {
    SExpr { expr: &'a SExpr },
    MExpr { expr: &'a MExpr, memo: &'a Memo },
}

impl<'a> RelExpr<'a> {
    pub fn with_s_expr(s_expr: &'a SExpr) -> Self {
        Self::SExpr { expr: s_expr }
    }

    pub fn with_m_expr(m_expr: &'a MExpr, memo: &'a Memo) -> Self {
        Self::MExpr { expr: m_expr, memo }
    }

    pub fn derive_relational_prop(&self) -> Result<RelationalProperty> {
        match self {
            RelExpr::SExpr { expr } => {
                if let Some(rel_prop) = expr.rel_prop.lock().unwrap().as_ref() {
                    return Ok(rel_prop.clone());
                }
                let rel_prop = expr.plan.derive_relational_prop(self)?;
                *expr.rel_prop.lock().unwrap() = Some(rel_prop.clone());
                Ok(rel_prop)
            }
            RelExpr::MExpr { expr, .. } => expr.plan.derive_relational_prop(self),
        }
    }

    pub fn derive_relational_prop_child(&self, index: usize) -> Result<RelationalProperty> {
        match self {
            RelExpr::SExpr { expr } => {
                let child = expr.child(index)?;
                let rel_expr = RelExpr::with_s_expr(child);
                rel_expr.derive_relational_prop()
            }
            RelExpr::MExpr { expr, memo } => {
                Ok(memo.group(expr.group_index)?.relational_prop.clone())
            }
        }
    }

    // Derive cardinality and statistics
    pub fn derive_cardinality(&self) -> Result<StatInfo> {
        match self {
            RelExpr::SExpr { expr } => {
                if let Some(stat_info) = expr.stat_info.lock().unwrap().as_ref() {
                    return Ok(stat_info.clone());
                }
                let stat_info = expr.plan.derive_cardinality(self)?;
                *expr.stat_info.lock().unwrap() = Some(stat_info.clone());
                Ok(stat_info)
            }
            RelExpr::MExpr { expr, .. } => expr.plan.derive_cardinality(self),
        }
    }

    pub(crate) fn derive_cardinality_child(&self, index: IndexType) -> Result<StatInfo> {
        match self {
            RelExpr::SExpr { expr } => {
                let child = expr.child(index)?;
                let rel_expr = RelExpr::with_s_expr(child);
                rel_expr.derive_cardinality()
            }
            RelExpr::MExpr { expr, memo } => Ok(memo.group(expr.group_index)?.stat_info.clone()),
        }
    }

    pub fn derive_physical_prop(&self) -> Result<PhysicalProperty> {
        let plan = match self {
            RelExpr::SExpr { expr } => expr.plan(),
            RelExpr::MExpr { expr, .. } => &expr.plan,
        };

        let prop = plan.derive_physical_prop(self)?;
        Ok(prop)
    }

    pub fn derive_physical_prop_child(&self, index: usize) -> Result<PhysicalProperty> {
        match self {
            RelExpr::SExpr { expr } => {
                let child = expr.child(index)?;
                let rel_expr = RelExpr::with_s_expr(child);
                rel_expr.derive_physical_prop()
            }
            RelExpr::MExpr { .. } => Err(ErrorCode::Internal(
                "Cannot derive physical property from MExpr".to_string(),
            )),
        }
    }

    pub fn compute_required_prop_child(
        &self,
        ctx: Arc<dyn TableContext>,
        index: usize,
        input: &RequiredProperty,
    ) -> Result<RequiredProperty> {
        let plan = match self {
            RelExpr::SExpr { expr } => expr.plan(),
            RelExpr::MExpr { expr, .. } => &expr.plan,
        };

        let prop = plan.compute_required_prop_child(ctx, self, index, input)?;
        Ok(prop)
    }
}
