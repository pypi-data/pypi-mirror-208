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
use std::sync::Arc;

use common_catalog::table::ColumnStatistics;
use common_catalog::table::TableStatistics;
use common_catalog::table_context::TableContext;
use common_exception::Result;
use itertools::Itertools;

use crate::optimizer::histogram_from_ndv;
use crate::optimizer::ColumnSet;
use crate::optimizer::ColumnStat;
use crate::optimizer::ColumnStatSet;
use crate::optimizer::Datum;
use crate::optimizer::Distribution;
use crate::optimizer::PhysicalProperty;
use crate::optimizer::RelExpr;
use crate::optimizer::RelationalProperty;
use crate::optimizer::RequiredProperty;
use crate::optimizer::SelectivityEstimator;
use crate::optimizer::StatInfo;
use crate::optimizer::Statistics as OpStatistics;
use crate::optimizer::DEFAULT_HISTOGRAM_BUCKETS;
use crate::optimizer::MAX_SELECTIVITY;
use crate::plans::Operator;
use crate::plans::RelOp;
use crate::plans::ScalarExpr;
use crate::plans::SortItem;
use crate::IndexType;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Prewhere {
    // columns needed to be output after prewhere scan
    pub output_columns: ColumnSet,
    // columns needed to conduct prewhere filter
    pub prewhere_columns: ColumnSet,
    // prewhere filter predicates
    pub predicates: Vec<ScalarExpr>,
}

#[derive(Clone, Debug)]
pub struct Statistics {
    // statistics will be ignored in comparison and hashing
    pub statistics: Option<TableStatistics>,
    // statistics will be ignored in comparison and hashing
    pub col_stats: HashMap<IndexType, Option<ColumnStatistics>>,
}

#[derive(Clone, Debug)]
pub struct Scan {
    pub table_index: IndexType,
    pub columns: ColumnSet,
    pub push_down_predicates: Option<Vec<ScalarExpr>>,
    pub limit: Option<usize>,
    pub order_by: Option<Vec<SortItem>>,
    pub prewhere: Option<Prewhere>,

    pub statistics: Statistics,
}

impl Scan {
    pub fn prune_columns(&self, columns: ColumnSet, prewhere: Option<Prewhere>) -> Self {
        let col_stats = self
            .statistics
            .col_stats
            .iter()
            .filter(|(col, _)| columns.contains(*col))
            .map(|(col, stat)| (*col, stat.clone()))
            .collect();

        Scan {
            table_index: self.table_index,
            columns,
            push_down_predicates: self.push_down_predicates.clone(),
            limit: self.limit,
            order_by: self.order_by.clone(),
            statistics: Statistics {
                statistics: self.statistics.statistics,
                col_stats,
            },
            prewhere,
        }
    }

    fn used_columns(&self) -> ColumnSet {
        let mut used_columns = ColumnSet::new();
        if let Some(preds) = &self.push_down_predicates {
            for pred in preds.iter() {
                used_columns.extend(pred.used_columns());
            }
        }
        if let Some(prewhere) = &self.prewhere {
            used_columns.extend(prewhere.prewhere_columns.iter());
        }

        used_columns.extend(self.columns.iter());
        used_columns
    }
}

impl PartialEq for Scan {
    fn eq(&self, other: &Self) -> bool {
        self.table_index == other.table_index
            && self.columns == other.columns
            && self.push_down_predicates == other.push_down_predicates
    }
}

impl Eq for Scan {}

impl std::hash::Hash for Scan {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.table_index.hash(state);
        for column in self.columns.iter().sorted() {
            column.hash(state);
        }
        self.push_down_predicates.hash(state);
    }
}

impl Operator for Scan {
    fn rel_op(&self) -> RelOp {
        RelOp::Scan
    }

    fn derive_relational_prop(&self, _rel_expr: &RelExpr) -> Result<RelationalProperty> {
        Ok(RelationalProperty {
            output_columns: self.columns.clone(),
            outer_columns: Default::default(),
            used_columns: self.used_columns(),
        })
    }

    fn derive_physical_prop(&self, _rel_expr: &RelExpr) -> Result<PhysicalProperty> {
        Ok(PhysicalProperty {
            distribution: Distribution::Random,
        })
    }

    fn derive_cardinality(&self, _rel_expr: &RelExpr) -> Result<StatInfo> {
        let used_columns = self.used_columns();

        let num_rows = self
            .statistics
            .statistics
            .as_ref()
            .map(|s| s.num_rows.unwrap_or(0))
            .unwrap_or(0);

        let mut column_stats: ColumnStatSet = Default::default();
        for (k, v) in &self.statistics.col_stats {
            // No need to cal histogram for unused columns
            if !used_columns.contains(k) {
                continue;
            }
            if let Some(col_stat) = v {
                let min = col_stat.min.clone();
                let max = col_stat.max.clone();
                let min_datum = Datum::from_scalar(&min);
                let max_datum = Datum::from_scalar(&max);
                if let (Some(min), Some(max)) = (min_datum, max_datum) {
                    let histogram = histogram_from_ndv(
                        col_stat.number_of_distinct_values,
                        num_rows,
                        Some((min.clone(), max.clone())),
                        DEFAULT_HISTOGRAM_BUCKETS,
                    )
                    .ok();
                    let column_stat = ColumnStat {
                        min,
                        max,
                        ndv: col_stat.number_of_distinct_values as f64,
                        null_count: col_stat.null_count,
                        histogram,
                    };
                    column_stats.insert(*k as IndexType, column_stat);
                }
            }
        }

        let precise_cardinality = self
            .statistics
            .statistics
            .as_ref()
            .and_then(|stat| stat.num_rows);

        let cardinality = match (precise_cardinality, &self.prewhere) {
            (Some(precise_cardinality), Some(ref prewhere)) => {
                let mut statistics = OpStatistics {
                    precise_cardinality: Some(precise_cardinality),
                    column_stats: column_stats.clone(),
                };

                // Derive cardinality
                let mut sb = SelectivityEstimator::new(&mut statistics);
                let mut selectivity = MAX_SELECTIVITY;
                for pred in prewhere.predicates.iter() {
                    // Compute selectivity for each conjunction
                    selectivity *= sb.compute_selectivity(pred, true)?;
                }
                (precise_cardinality as f64) * selectivity
            }
            (Some(precise_cardinality), None) => precise_cardinality as f64,
            (_, _) => 0.0,
        };

        // If prewhere is not none, we can't get precise cardinality
        let precise_cardinality = if self.prewhere.is_none() {
            precise_cardinality
        } else {
            None
        };
        Ok(StatInfo {
            cardinality,
            statistics: OpStatistics {
                precise_cardinality,
                column_stats,
            },
        })
    }

    // Won't be invoked at all, since `PhysicalScan` is leaf node
    fn compute_required_prop_child(
        &self,
        _ctx: Arc<dyn TableContext>,
        _rel_expr: &RelExpr,
        _child_index: usize,
        _required: &RequiredProperty,
    ) -> Result<RequiredProperty> {
        unreachable!()
    }
}
