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

use std::borrow::Borrow;
use std::collections::HashMap;

use common_exception::Result;
use common_expression::BlockThresholds;
use common_expression::ColumnId;
use common_expression::Scalar;
use storages_common_table_meta::meta::BlockMeta;
use storages_common_table_meta::meta::ColumnStatistics;
use storages_common_table_meta::meta::Statistics;
use storages_common_table_meta::meta::StatisticsOfColumns;

pub fn reduce_block_statistics<T: Borrow<StatisticsOfColumns>>(
    stats_of_columns: &[T],
) -> Result<StatisticsOfColumns> {
    // Combine statistics of a column into `Vec`, that is:
    // from : `&[HashMap<ColumnId, ColumnStatistics>]`
    // to   : `HashMap<ColumnId, Vec<&ColumnStatistics>)>`
    let col_to_stats_lit = stats_of_columns.iter().fold(HashMap::new(), |acc, item| {
        item.borrow().iter().fold(
            acc,
            |mut acc: HashMap<ColumnId, Vec<&ColumnStatistics>>, (col_id, col_stats)| {
                acc.entry(*col_id).or_default().push(col_stats);
                acc
            },
        )
    });

    // Reduce the `Vec<&ColumnStatistics` into ColumnStatistics`, i.e.:
    // from : `HashMap<ColumnId, Vec<&ColumnStatistics>)>`
    // to   : `type BlockStatistics = HashMap<ColumnId, ColumnStatistics>`
    let len = col_to_stats_lit.len();
    col_to_stats_lit
        .iter()
        .try_fold(HashMap::with_capacity(len), |mut acc, (id, stats)| {
            let mut min_stats = Vec::with_capacity(stats.len());
            let mut max_stats = Vec::with_capacity(stats.len());
            let mut null_count = 0;
            let mut in_memory_size = 0;

            for col_stats in stats {
                min_stats.push(col_stats.min.clone());
                max_stats.push(col_stats.max.clone());

                null_count += col_stats.null_count;
                in_memory_size += col_stats.in_memory_size;
            }

            // TODO:

            // In accumulator.rs, we use aggregation functions to get the min/max of `DataValue`s,
            // like this:
            //   `let maxs = eval_aggr("max", vec![], &[column_field], rows)?`
            // we should unify these logics, or at least, ensure the ways they compares do NOT diverge
            let min = min_stats
                .iter()
                .filter(|s| !s.is_null())
                .min_by(|&x, &y| x.cmp(y))
                .cloned()
                .unwrap_or(Scalar::Null);

            let max = max_stats
                .iter()
                .filter(|s| !s.is_null())
                .max_by(|&x, &y| x.cmp(y))
                .cloned()
                .unwrap_or(Scalar::Null);

            acc.insert(*id, ColumnStatistics {
                min,
                max,
                null_count,
                in_memory_size,
                distinct_of_values: None,
            });
            Ok(acc)
        })
}

pub fn merge_statistics(l: &Statistics, r: &Statistics) -> Result<Statistics> {
    let s = Statistics {
        row_count: l.row_count + r.row_count,
        block_count: l.block_count + r.block_count,
        perfect_block_count: l.perfect_block_count + r.perfect_block_count,
        uncompressed_byte_size: l.uncompressed_byte_size + r.uncompressed_byte_size,
        compressed_byte_size: l.compressed_byte_size + r.compressed_byte_size,
        index_size: l.index_size + r.index_size,
        col_stats: reduce_block_statistics(&[&l.col_stats, &r.col_stats])?,
    };
    Ok(s)
}

pub fn merge_statistics_mut(l: &mut Statistics, r: &Statistics) -> Result<()> {
    l.row_count += r.row_count;
    l.block_count += r.block_count;
    l.perfect_block_count += r.perfect_block_count;
    l.uncompressed_byte_size += r.uncompressed_byte_size;
    l.compressed_byte_size += r.compressed_byte_size;
    l.index_size += r.index_size;
    l.col_stats = reduce_block_statistics(&[&l.col_stats, &r.col_stats])?;
    Ok(())
}

// Deduct statistics, only be used for calculate snapshot summary during update/delete/replace.
pub fn deduct_statistics_mut(l: &mut Statistics, r: &Statistics) {
    l.row_count -= r.row_count;
    l.block_count -= r.block_count;
    l.perfect_block_count -= r.perfect_block_count;
    l.uncompressed_byte_size -= r.uncompressed_byte_size;
    l.compressed_byte_size -= r.compressed_byte_size;
    l.index_size -= r.index_size;
    for (id, col_stats) in &mut l.col_stats {
        if let Some(r_col_stats) = r.col_stats.get(id) {
            // The MinMax of a column cannot be recalculated by the right statistics,
            // so we skip deduct the MinMax statistics here.
            col_stats.null_count -= r_col_stats.null_count;
            col_stats.in_memory_size -= r_col_stats.in_memory_size;
        }
    }
}

pub fn reduce_statistics<T: Borrow<Statistics>>(stats: &[T]) -> Result<Statistics> {
    let mut statistics = Statistics::default();
    for item in stats {
        statistics = merge_statistics(&statistics, item.borrow())?
    }
    Ok(statistics)
}

pub fn reduce_block_metas<T: Borrow<BlockMeta>>(
    block_metas: &[T],
    thresholds: BlockThresholds,
) -> Result<Statistics> {
    let mut row_count: u64 = 0;
    let mut block_count: u64 = 0;
    let mut uncompressed_byte_size: u64 = 0;
    let mut compressed_byte_size: u64 = 0;
    let mut index_size: u64 = 0;
    let mut perfect_block_count: u64 = 0;

    block_metas.iter().for_each(|b| {
        let b = b.borrow();
        row_count += b.row_count;
        block_count += 1;
        uncompressed_byte_size += b.block_size;
        compressed_byte_size += b.file_size;
        index_size += b.bloom_filter_index_size;
        if thresholds.check_large_enough(b.row_count as usize, b.block_size as usize) {
            perfect_block_count += 1;
        }
    });

    let stats = block_metas
        .iter()
        .map(|v| &v.borrow().col_stats)
        .collect::<Vec<_>>();
    let merged_col_stats = reduce_block_statistics(&stats)?;

    Ok(Statistics {
        row_count,
        block_count,
        perfect_block_count,
        uncompressed_byte_size,
        compressed_byte_size,
        index_size,
        col_stats: merged_col_stats,
    })
}
