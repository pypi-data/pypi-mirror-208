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

use std::iter::once;
use std::sync::Arc;

use common_arrow::arrow::array::ord as arrow_ord;
use common_arrow::arrow::array::ord::DynComparator;
use common_arrow::arrow::array::Array;
use common_arrow::arrow::array::PrimitiveArray;
use common_arrow::arrow::compute::merge_sort as arrow_merge_sort;
use common_arrow::arrow::compute::merge_sort::build_comparator_impl;
use common_arrow::arrow::compute::sort as arrow_sort;
use common_arrow::arrow::datatypes::DataType as ArrowType;
use common_arrow::arrow::error::Error as ArrowError;
use common_arrow::arrow::error::Result as ArrowResult;
use common_exception::ErrorCode;
use common_exception::Result;

use crate::types::DataType;
use crate::utils::arrow::column_to_arrow_array;
use crate::Column;
use crate::DataBlock;

pub type Aborting = Arc<Box<dyn Fn() -> bool + Send + Sync + 'static>>;

#[derive(Clone)]
pub struct SortColumnDescription {
    pub offset: usize,
    pub asc: bool,
    pub nulls_first: bool,
    pub is_nullable: bool,
}

impl DataBlock {
    pub fn sort(
        block: &DataBlock,
        descriptions: &[SortColumnDescription],
        limit: Option<usize>,
    ) -> Result<DataBlock> {
        let num_rows = block.num_rows();
        if num_rows <= 1 {
            return Ok(block.clone());
        }
        let order_columns = descriptions
            .iter()
            .map(|d| column_to_arrow_array(block.get_by_offset(d.offset), num_rows))
            .collect::<Vec<_>>();

        let order_arrays = descriptions
            .iter()
            .zip(order_columns.iter())
            .map(|(d, array)| arrow_sort::SortColumn {
                values: array.as_ref(),
                options: Some(arrow_sort::SortOptions {
                    descending: !d.asc,
                    nulls_first: d.nulls_first,
                }),
            })
            .collect::<Vec<_>>();

        let indices: PrimitiveArray<u32> =
            arrow_sort::lexsort_to_indices_impl(&order_arrays, limit, &build_compare)?;
        DataBlock::take(block, indices.values())
    }

    // merge two blocks to one sorted block
    // require: lhs and rhs have been `convert_to_full`.
    fn two_way_merge_sort(
        blocks: &[DataBlock],
        descriptions: &[SortColumnDescription],
        limit: Option<usize>,
    ) -> Result<DataBlock> {
        assert!(blocks.len() == 2);

        let lhs = &blocks[0];
        let rhs = &blocks[1];

        let lhs_len = lhs.num_rows();
        let rhs_len = rhs.num_rows();
        if lhs_len == 0 {
            return Ok(rhs.clone());
        }
        if rhs_len == 0 {
            return Ok(lhs.clone());
        }

        let mut sort_options = Vec::with_capacity(descriptions.len());
        let sort_arrays = descriptions
            .iter()
            .map(|d| {
                let left = column_to_arrow_array(lhs.get_by_offset(d.offset), lhs_len);
                let right = column_to_arrow_array(rhs.get_by_offset(d.offset), rhs_len);
                sort_options.push(arrow_sort::SortOptions {
                    descending: !d.asc,
                    nulls_first: d.nulls_first,
                });
                vec![left, right]
            })
            .collect::<Vec<_>>();

        let sort_dyn_arrays = sort_arrays
            .iter()
            .map(|f| vec![f[0].as_ref(), f[1].as_ref()])
            .collect::<Vec<_>>();

        let sort_options_with_arrays = sort_dyn_arrays
            .iter()
            .zip(sort_options.iter())
            .map(|(arrays, opt)| (arrays as &[&dyn Array], opt))
            .collect::<Vec<_>>();

        let comparator = build_comparator_impl(&sort_options_with_arrays, &build_compare)?;
        let lhs_slice = (0, 0, lhs_len);
        let rhs_slice = (1, 0, rhs_len);

        let slices =
            arrow_merge_sort::merge_sort_slices(once(&lhs_slice), once(&rhs_slice), &comparator)
                .to_vec(limit);

        let block = DataBlock::take_by_slices_limit_from_blocks(blocks, &slices, limit);
        Ok(block)
    }

    pub fn merge_sort(
        blocks: &[DataBlock],
        descriptions: &[SortColumnDescription],
        limit: Option<usize>,
        aborting: Aborting,
    ) -> Result<DataBlock> {
        match blocks.len() {
            0 => Result::Err(ErrorCode::EmptyData("Can't merge empty blocks")),
            1 => Ok(blocks[0].clone()),
            2 => {
                if aborting() {
                    return Err(ErrorCode::AbortedQuery(
                        "Aborted query, because the server is shutting down or the query was killed.",
                    ));
                }

                DataBlock::two_way_merge_sort(blocks, descriptions, limit)
            }
            _ => {
                if aborting() {
                    return Err(ErrorCode::AbortedQuery(
                        "Aborted query, because the server is shutting down or the query was killed.",
                    ));
                }
                let left = DataBlock::merge_sort(
                    &blocks[0..blocks.len() / 2],
                    descriptions,
                    limit,
                    aborting.clone(),
                )?;
                if aborting() {
                    return Err(ErrorCode::AbortedQuery(
                        "Aborted query, because the server is shutting down or the query was killed.",
                    ));
                }
                let right = DataBlock::merge_sort(
                    &blocks[blocks.len() / 2..blocks.len()],
                    descriptions,
                    limit,
                    aborting.clone(),
                )?;
                if aborting() {
                    return Err(ErrorCode::AbortedQuery(
                        "Aborted query, because the server is shutting down or the query was killed.",
                    ));
                }
                DataBlock::two_way_merge_sort(&[left, right], descriptions, limit)
            }
        }
    }
}

fn compare_variant(left: &dyn Array, right: &dyn Array) -> ArrowResult<DynComparator> {
    let left = Column::from_arrow(left, &DataType::Variant)
        .as_variant()
        .cloned()
        .unwrap();
    let right = Column::from_arrow(right, &DataType::Variant)
        .as_variant()
        .cloned()
        .unwrap();
    Ok(Box::new(move |i, j| {
        let l = unsafe { left.index_unchecked(i) };
        let r = unsafe { right.index_unchecked(j) };
        jsonb::compare(l, r).unwrap()
    }))
}

fn compare_decimal256(left: &dyn Array, right: &dyn Array) -> ArrowResult<DynComparator> {
    let left = left
        .as_any()
        .downcast_ref::<common_arrow::arrow::array::PrimitiveArray<common_arrow::arrow::types::i256>>()
        .unwrap()
        .clone();
    let right = right
        .as_any()
        .downcast_ref::<common_arrow::arrow::array::PrimitiveArray<common_arrow::arrow::types::i256>>()
        .unwrap()
        .clone();

    Ok(Box::new(move |i, j| left.value(i).cmp(&right.value(j))))
}

fn build_compare(left: &dyn Array, right: &dyn Array) -> ArrowResult<DynComparator> {
    match left.data_type() {
        ArrowType::Extension(name, _, _) => {
            if name == "Variant" {
                compare_variant(left, right)
            } else {
                Err(ArrowError::NotYetImplemented(format!(
                    "Sort not supported for data type {:?}",
                    left.data_type()
                )))
            }
        }
        ArrowType::Decimal256(_, _) => compare_decimal256(left, right),
        _ => arrow_ord::build_compare(left, right),
    }
}
