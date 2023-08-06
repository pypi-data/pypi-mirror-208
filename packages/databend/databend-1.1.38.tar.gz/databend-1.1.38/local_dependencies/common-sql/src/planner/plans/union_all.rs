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
use common_exception::Result;

use crate::optimizer::ColumnSet;
use crate::optimizer::Distribution;
use crate::optimizer::PhysicalProperty;
use crate::optimizer::RelExpr;
use crate::optimizer::RelationalProperty;
use crate::optimizer::RequiredProperty;
use crate::optimizer::StatInfo;
use crate::optimizer::Statistics;
use crate::plans::Operator;
use crate::plans::RelOp;
use crate::IndexType;

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct UnionAll {
    // Pairs of unioned columns
    pub pairs: Vec<(IndexType, IndexType)>,
}

impl UnionAll {
    pub fn used_columns(&self) -> Result<ColumnSet> {
        let mut used_columns = ColumnSet::new();
        for (left, right) in &self.pairs {
            used_columns.insert(*left);
            used_columns.insert(*right);
        }
        Ok(used_columns)
    }
}

impl Operator for UnionAll {
    fn rel_op(&self) -> RelOp {
        RelOp::UnionAll
    }

    fn derive_relational_prop(&self, rel_expr: &RelExpr) -> Result<RelationalProperty> {
        let left_prop = rel_expr.derive_relational_prop_child(0)?;
        let right_prop = rel_expr.derive_relational_prop_child(1)?;

        // Derive output columns
        let mut output_columns = left_prop.output_columns;
        output_columns = output_columns
            .union(&right_prop.output_columns)
            .cloned()
            .collect();

        // Derive outer columns
        let mut outer_columns = left_prop.outer_columns;
        outer_columns = outer_columns
            .union(&right_prop.outer_columns)
            .cloned()
            .collect();

        // Derive used columns
        let mut used_columns = self.used_columns()?;
        used_columns.extend(left_prop.used_columns);
        used_columns.extend(right_prop.used_columns);

        Ok(RelationalProperty {
            output_columns,
            outer_columns,
            used_columns,
        })
    }

    fn derive_physical_prop(&self, rel_expr: &RelExpr) -> Result<PhysicalProperty> {
        let left_child = rel_expr.derive_physical_prop_child(0)?;
        Ok(PhysicalProperty {
            distribution: left_child.distribution,
        })
    }

    fn derive_cardinality(&self, rel_expr: &RelExpr) -> Result<StatInfo> {
        let left_stat_info = rel_expr.derive_cardinality_child(0)?;
        let right_stat_info = rel_expr.derive_cardinality_child(1)?;
        let cardinality = left_stat_info.cardinality + right_stat_info.cardinality;

        let precise_cardinality =
            left_stat_info
                .statistics
                .precise_cardinality
                .and_then(|left_cardinality| {
                    right_stat_info
                        .statistics
                        .precise_cardinality
                        .map(|right_cardinality| left_cardinality + right_cardinality)
                });

        Ok(StatInfo {
            cardinality,
            statistics: Statistics {
                precise_cardinality,
                column_stats: Default::default(),
            },
        })
    }

    fn compute_required_prop_child(
        &self,
        _ctx: Arc<dyn TableContext>,
        rel_expr: &RelExpr,
        _child_index: usize,
        required: &RequiredProperty,
    ) -> Result<RequiredProperty> {
        let mut required = required.clone();
        let left_physical_prop = rel_expr.derive_physical_prop_child(0)?;
        let right_physical_prop = rel_expr.derive_physical_prop_child(1)?;
        if left_physical_prop.distribution == Distribution::Serial
            || right_physical_prop.distribution == Distribution::Serial
        {
            required.distribution = Distribution::Serial;
        } else if left_physical_prop.distribution == right_physical_prop.distribution {
            required.distribution = left_physical_prop.distribution;
        }
        Ok(required)
    }
}
