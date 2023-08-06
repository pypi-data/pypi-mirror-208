// Copyright 2022 Datafuse Labs.
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
use common_expression::types::number::*;
use common_expression::types::NumberDataType;
use common_expression::types::StringType;
use common_expression::*;

use crate::common::new_block;

#[test]
fn test_group_by_hash() -> Result<()> {
    let schema = TableSchemaRefExt::create(vec![
        TableField::new("a", TableDataType::Number(NumberDataType::Int8)),
        TableField::new("b", TableDataType::Number(NumberDataType::Int8)),
        TableField::new("c", TableDataType::Number(NumberDataType::Int8)),
        TableField::new("x", TableDataType::String),
    ]);

    let block = new_block(&vec![
        Int8Type::from_data(vec![1i8, 1, 2, 1, 2, 3]),
        Int8Type::from_data(vec![1i8, 1, 2, 1, 2, 3]),
        Int8Type::from_data(vec![1i8, 1, 2, 1, 2, 3]),
        StringType::from_data(vec!["x1", "x1", "x2", "x1", "x2", "x3"]),
    ]);

    let method = DataBlock::choose_hash_method(&block, &[0, 3], false)?;
    assert_eq!(method.name(), HashMethodSerializer::default().name(),);

    let method = DataBlock::choose_hash_method(&block, &[0, 1, 2], false)?;

    assert_eq!(method.name(), HashMethodKeysU32::default().name());

    let hash = HashMethodKeysU32::default();
    let columns = vec!["a", "b", "c"];

    let mut group_columns = Vec::with_capacity(columns.len());
    {
        for col in columns {
            let index = schema.index_of(col).unwrap();
            let entry = block.get_by_offset(index);
            let col = entry.value.as_column().unwrap();
            group_columns.push((col.clone(), entry.data_type.clone()));
        }
    }

    let state = hash.build_keys_state(group_columns.as_slice(), block.num_rows())?;
    let keys_iter = hash.build_keys_iter(&state)?;
    let keys: Vec<u32> = keys_iter.copied().collect();
    assert_eq!(keys, vec![
        0x10101, 0x10101, 0x20202, 0x10101, 0x20202, 0x30303
    ]);
    Ok(())
}
