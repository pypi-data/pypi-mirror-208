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

use std::alloc::Layout;
use std::fmt;
use std::sync::Arc;

use common_arrow::arrow::bitmap::Bitmap;
use common_exception::Result;
use common_expression::types::AnyType;
use common_expression::types::DataType;
use common_expression::types::ValueType;
use common_expression::Column;
use common_expression::ColumnBuilder;

use super::aggregate_function::AggregateFunction;
use super::StateAddr;

#[derive(Clone)]
pub struct AggregateNullResultFunction {
    data_type: DataType,
}

impl AggregateNullResultFunction {
    pub fn try_create(data_type: DataType) -> Result<Arc<dyn AggregateFunction>> {
        Ok(Arc::new(AggregateNullResultFunction { data_type }))
    }
}

impl AggregateFunction for AggregateNullResultFunction {
    fn name(&self) -> &str {
        "AggregateNullResultFunction"
    }

    fn return_type(&self) -> Result<DataType> {
        Ok(self.data_type.clone())
    }

    fn init_state(&self, __place: StateAddr) {}

    fn state_layout(&self) -> Layout {
        Layout::new::<u8>()
    }

    fn accumulate(
        &self,
        __place: StateAddr,
        _columns: &[Column],
        _validity: Option<&Bitmap>,
        _input_rows: usize,
    ) -> Result<()> {
        Ok(())
    }

    fn accumulate_keys(
        &self,
        _places: &[StateAddr],
        _offset: usize,
        _columns: &[Column],
        _input_rows: usize,
    ) -> Result<()> {
        Ok(())
    }

    fn accumulate_row(&self, _place: StateAddr, _columns: &[Column], _row: usize) -> Result<()> {
        Ok(())
    }

    fn serialize(&self, _place: StateAddr, _writer: &mut Vec<u8>) -> Result<()> {
        Ok(())
    }

    fn deserialize(&self, _place: StateAddr, _reader: &mut &[u8]) -> Result<()> {
        Ok(())
    }

    fn merge(&self, _place: StateAddr, _rhs: StateAddr) -> Result<()> {
        Ok(())
    }

    fn merge_result(&self, _place: StateAddr, array: &mut ColumnBuilder) -> Result<()> {
        AnyType::push_default(array);
        Ok(())
    }
}

impl fmt::Display for AggregateNullResultFunction {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.name())
    }
}
