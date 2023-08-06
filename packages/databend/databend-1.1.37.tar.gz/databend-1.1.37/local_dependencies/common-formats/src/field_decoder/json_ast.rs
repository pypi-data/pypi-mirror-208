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

use std::any::Any;
use std::io::Cursor;

use chrono_tz::Tz;
use common_arrow::arrow::bitmap::MutableBitmap;
use common_exception::ErrorCode;
use common_exception::Result;
use common_expression::serialize::read_decimal_from_json;
use common_expression::serialize::uniform_date;
use common_expression::types::array::ArrayColumnBuilder;
use common_expression::types::date::check_date;
use common_expression::types::decimal::Decimal;
use common_expression::types::decimal::DecimalColumnBuilder;
use common_expression::types::decimal::DecimalSize;
use common_expression::types::nullable::NullableColumnBuilder;
use common_expression::types::number::Number;
use common_expression::types::string::StringColumnBuilder;
use common_expression::types::timestamp::check_timestamp;
use common_expression::types::AnyType;
use common_expression::types::NumberColumnBuilder;
use common_expression::with_decimal_type;
use common_expression::with_number_mapped_type;
use common_expression::ColumnBuilder;
use common_io::cursor_ext::BufferReadDateTimeExt;
use common_io::cursor_ext::ReadNumberExt;
use lexical_core::FromLexical;
use num::cast::AsPrimitive;
use serde_json::Value;

use crate::FieldDecoder;
use crate::FileFormatOptionsExt;

pub struct FieldJsonAstDecoder {
    pub timezone: Tz,
    pub ident_case_sensitive: bool,
}

impl FieldDecoder for FieldJsonAstDecoder {
    fn as_any(&self) -> &dyn Any {
        self
    }
}

impl FieldJsonAstDecoder {
    pub fn create(options: &FileFormatOptionsExt) -> Self {
        FieldJsonAstDecoder {
            timezone: options.timezone,
            ident_case_sensitive: options.ident_case_sensitive,
        }
    }

    pub fn read_field(&self, column: &mut ColumnBuilder, value: &Value) -> Result<()> {
        match column {
            ColumnBuilder::Null { len } => self.read_null(len, value),
            ColumnBuilder::Nullable(c) => self.read_nullable(c, value),
            ColumnBuilder::Boolean(c) => self.read_bool(c, value),
            ColumnBuilder::Number(c) => with_number_mapped_type!(|NUM_TYPE| match c {
                NumberColumnBuilder::NUM_TYPE(c) => {
                    if NUM_TYPE::FLOATING {
                        self.read_float(c, value)
                    } else {
                        self.read_int(c, value)
                    }
                }
            }),
            ColumnBuilder::Decimal(c) => with_decimal_type!(|DECIMAL_TYPE| match c {
                DecimalColumnBuilder::DECIMAL_TYPE(c, size) => self.read_decimal(c, *size, value),
            }),
            ColumnBuilder::Date(c) => self.read_date(c, value),
            ColumnBuilder::Timestamp(c) => self.read_timestamp(c, value),
            ColumnBuilder::String(c) => self.read_string(c, value),
            ColumnBuilder::Array(c) => self.read_array(c, value),
            ColumnBuilder::Map(c) => self.read_map(c, value),
            ColumnBuilder::Tuple(fields) => self.read_tuple(fields, value),
            ColumnBuilder::Variant(c) => self.read_variant(c, value),
            _ => unimplemented!(),
        }
    }

    fn read_bool(&self, column: &mut MutableBitmap, value: &Value) -> Result<()> {
        match value {
            Value::Bool(v) => column.push(*v),
            _ => return Err(ErrorCode::BadBytes("Incorrect boolean value")),
        }
        Ok(())
    }

    fn read_null(&self, len: &mut usize, _value: &Value) -> Result<()> {
        *len += 1;
        Ok(())
    }

    fn read_nullable(
        &self,
        column: &mut NullableColumnBuilder<AnyType>,
        value: &Value,
    ) -> Result<()> {
        match value {
            Value::Null => {
                column.push_null();
            }
            other => {
                self.read_field(&mut column.builder, other)?;
                column.validity.push(true);
            }
        }
        Ok(())
    }

    fn read_int<T>(&self, column: &mut Vec<T>, value: &Value) -> Result<()>
    where
        T: Number + From<T::Native>,
        T::Native: FromLexical,
    {
        match value {
            Value::Number(v) => {
                let v = v.to_string();
                let mut reader = Cursor::new(v.as_bytes());
                let v: T::Native = if !T::FLOATING {
                    reader.read_int_text()
                } else {
                    reader.read_float_text()
                }?;

                column.push(v.into());
                Ok(())
            }
            _ => Err(ErrorCode::BadBytes("Incorrect json value, must be number")),
        }
    }

    fn read_float<T>(&self, column: &mut Vec<T>, value: &Value) -> Result<()>
    where
        T: Number + From<T::Native>,
        T::Native: FromLexical,
    {
        match value {
            Value::Number(v) => {
                let v = v.to_string();
                let mut reader = Cursor::new(v.as_bytes());
                let v: T::Native = if !T::FLOATING {
                    reader.read_int_text()
                } else {
                    reader.read_float_text()
                }?;

                column.push(v.into());
                Ok(())
            }
            _ => Err(ErrorCode::BadBytes("Incorrect json value, must be number")),
        }
    }

    fn read_decimal<D: Decimal>(
        &self,
        column: &mut Vec<D>,
        size: DecimalSize,
        value: &Value,
    ) -> Result<()> {
        column.push(read_decimal_from_json(value, size)?);
        Ok(())
    }

    fn read_string(&self, column: &mut StringColumnBuilder, value: &Value) -> Result<()> {
        match value {
            Value::String(s) => {
                column.put_str(s.as_str());
                column.commit_row();
                Ok(())
            }
            _ => Err(ErrorCode::BadBytes("Incorrect json value, must be string")),
        }
    }

    fn read_date(&self, column: &mut Vec<i32>, value: &Value) -> Result<()> {
        match value {
            Value::String(v) => {
                let mut reader = Cursor::new(v.as_bytes());
                let date = reader.read_date_text(&self.timezone)?;
                let days = uniform_date(date);
                check_date(days as i64)?;
                column.push(days);
                Ok(())
            }
            Value::Number(number) => match number.as_i64() {
                Some(n) => {
                    let n = check_date(n)?;
                    column.push(n);
                    Ok(())
                }
                None => Err(ErrorCode::BadArguments("Incorrect date value")),
            },
            _ => Err(ErrorCode::BadBytes("Incorrect date value")),
        }
    }

    fn read_timestamp(&self, column: &mut Vec<i64>, value: &Value) -> Result<()> {
        match value {
            Value::String(v) => {
                let v = v.clone();
                let mut reader = Cursor::new(v.as_bytes());
                let ts = reader.read_timestamp_text(&self.timezone)?;

                let micros = ts.timestamp_micros();
                check_timestamp(micros)?;
                column.push(micros.as_());
                Ok(())
            }
            Value::Number(number) => match number.as_i64() {
                Some(n) => {
                    check_timestamp(n)?;
                    column.push(n);
                    Ok(())
                }
                None => Err(ErrorCode::BadArguments(
                    "Incorrect timestamp value, must be i64",
                )),
            },
            _ => Err(ErrorCode::BadBytes("Incorrect timestamp value")),
        }
    }

    fn read_variant(&self, column: &mut StringColumnBuilder, value: &Value) -> Result<()> {
        let v = jsonb::Value::from(value);
        v.write_to_vec(&mut column.data);
        column.commit_row();
        Ok(())
    }

    fn read_array(&self, column: &mut ArrayColumnBuilder<AnyType>, value: &Value) -> Result<()> {
        match value {
            Value::Array(vals) => {
                for val in vals {
                    self.read_field(&mut column.builder, val)?;
                }
                column.commit_row();
                Ok(())
            }
            _ => Err(ErrorCode::BadBytes("Incorrect json value, must be array")),
        }
    }

    fn read_map(&self, column: &mut ArrayColumnBuilder<AnyType>, value: &Value) -> Result<()> {
        const KEY: usize = 0;
        const VALUE: usize = 1;
        let map_builder = column.builder.as_tuple_mut().unwrap();
        match value {
            Value::Object(obj) => {
                for (key, val) in obj.iter() {
                    let key = Value::String(key.to_string());
                    self.read_field(&mut map_builder[KEY], &key)?;
                    self.read_field(&mut map_builder[VALUE], val)?;
                }
                column.commit_row();
                Ok(())
            }
            _ => Err(ErrorCode::BadBytes("Incorrect json value, must be object")),
        }
    }

    fn read_tuple(&self, fields: &mut Vec<ColumnBuilder>, value: &Value) -> Result<()> {
        match value {
            Value::Object(obj) => {
                if fields.len() != obj.len() {
                    return Err(ErrorCode::BadBytes(format!(
                        "Incorrect json value, expect {} values, but get {} values",
                        fields.len(),
                        obj.len()
                    )));
                }
                for (field, item) in fields.iter_mut().zip(obj.iter()) {
                    let (_, val) = item;
                    self.read_field(field, val)?;
                }
                Ok(())
            }
            _ => Err(ErrorCode::BadBytes("Incorrect json value, must be object")),
        }
    }
}
