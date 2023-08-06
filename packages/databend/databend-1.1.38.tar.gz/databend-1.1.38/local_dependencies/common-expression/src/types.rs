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

pub mod any;
pub mod array;
pub mod bitmap;
pub mod boolean;
pub mod date;
pub mod decimal;
pub mod empty_array;
pub mod empty_map;
pub mod generic;
pub mod map;
pub mod null;
pub mod nullable;
pub mod number;
pub mod number_class;
pub mod string;
pub mod timestamp;
pub mod variant;

use std::fmt::Debug;
use std::ops::Range;

use common_arrow::arrow::trusted_len::TrustedLen;
use enum_as_inner::EnumAsInner;
use serde::Deserialize;
use serde::Serialize;

pub use self::any::AnyType;
pub use self::array::ArrayType;
pub use self::bitmap::BitmapType;
pub use self::boolean::BooleanType;
pub use self::date::DateType;
pub use self::decimal::DecimalDataType;
use self::decimal::DecimalSize;
pub use self::empty_array::EmptyArrayType;
pub use self::empty_map::EmptyMapType;
pub use self::generic::GenericType;
pub use self::map::MapType;
pub use self::null::NullType;
pub use self::nullable::NullableType;
pub use self::number::*;
pub use self::number_class::*;
pub use self::string::StringType;
pub use self::timestamp::TimestampType;
pub use self::variant::VariantType;
use crate::property::Domain;
use crate::values::Column;
use crate::values::Scalar;
use crate::ColumnBuilder;
use crate::ScalarRef;

pub type GenericMap = [DataType];

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize, EnumAsInner)]
pub enum DataType {
    Null,
    EmptyArray,
    EmptyMap,
    Boolean,
    String,
    Number(NumberDataType),
    Decimal(DecimalDataType),
    Timestamp,
    Date,
    Nullable(Box<DataType>),
    Array(Box<DataType>),
    Map(Box<DataType>),
    Bitmap,
    Tuple(Vec<DataType>),
    Variant,
    Generic(usize),
}

impl DataType {
    pub fn wrap_nullable(&self) -> Self {
        match self {
            DataType::Null | DataType::Nullable(_) => self.clone(),
            _ => Self::Nullable(Box::new(self.clone())),
        }
    }

    pub fn is_nullable(&self) -> bool {
        matches!(self, &DataType::Nullable(_))
    }

    pub fn is_nullable_or_null(&self) -> bool {
        matches!(self, &DataType::Nullable(_) | &DataType::Null)
    }

    pub fn can_inside_nullable(&self) -> bool {
        !self.is_nullable_or_null()
    }

    pub fn remove_nullable(&self) -> Self {
        match self {
            DataType::Nullable(ty) => (**ty).clone(),
            _ => self.clone(),
        }
    }

    pub fn unnest(&self) -> Self {
        match self {
            DataType::Array(ty) => ty.unnest(),
            _ => self.clone(),
        }
    }

    pub fn has_generic(&self) -> bool {
        match self {
            DataType::Generic(_) => true,
            DataType::Nullable(ty) => ty.has_generic(),
            DataType::Array(ty) => ty.has_generic(),
            DataType::Map(ty) => ty.has_generic(),
            DataType::Tuple(tys) => tys.iter().any(|ty| ty.has_generic()),
            _ => false,
        }
    }

    pub fn has_nested_nullable(&self) -> bool {
        match self {
            DataType::Nullable(box DataType::Nullable(_) | box DataType::Null) => true,
            DataType::Array(ty) => ty.has_nested_nullable(),
            DataType::Map(ty) => ty.has_nested_nullable(),
            DataType::Tuple(tys) => tys.iter().any(|ty| ty.has_nested_nullable()),
            _ => false,
        }
    }

    pub fn is_unsigned_numeric(&self) -> bool {
        match self {
            DataType::Number(ty) => ALL_UNSIGNED_INTEGER_TYPES.contains(ty),
            _ => false,
        }
    }

    pub fn is_signed_numeric(&self) -> bool {
        match self {
            DataType::Number(ty) => {
                ALL_INTEGER_TYPES.contains(ty) && !ALL_UNSIGNED_INTEGER_TYPES.contains(ty)
            }
            _ => false,
        }
    }

    pub fn is_numeric(&self) -> bool {
        match self {
            DataType::Number(ty) => ALL_NUMERICS_TYPES.contains(ty),
            _ => false,
        }
    }

    #[inline]
    pub fn is_integer(&self) -> bool {
        match self {
            DataType::Number(ty) => ALL_INTEGER_TYPES.contains(ty),
            _ => false,
        }
    }

    #[inline]
    pub fn is_floating(&self) -> bool {
        match self {
            DataType::Number(ty) => ALL_FLOAT_TYPES.contains(ty),
            _ => false,
        }
    }

    #[inline]
    pub fn is_decimal(&self) -> bool {
        matches!(self, DataType::Decimal(_ty))
    }

    #[inline]
    pub fn is_date_or_date_time(&self) -> bool {
        matches!(self, DataType::Timestamp | DataType::Date)
    }

    pub fn numeric_byte_size(&self) -> Result<usize, String> {
        match self {
            DataType::Number(NumberDataType::UInt8) | DataType::Number(NumberDataType::Int8) => {
                Ok(1)
            }
            DataType::Number(NumberDataType::UInt16) | DataType::Number(NumberDataType::Int16) => {
                Ok(2)
            }
            DataType::Date
            | DataType::Number(NumberDataType::UInt32)
            | DataType::Number(NumberDataType::Float32)
            | DataType::Number(NumberDataType::Int32) => Ok(4),
            DataType::Timestamp
            | DataType::Number(NumberDataType::UInt64)
            | DataType::Number(NumberDataType::Float64)
            | DataType::Number(NumberDataType::Int64) => Ok(8),

            DataType::Decimal(DecimalDataType::Decimal128(_)) => Ok(16),
            DataType::Decimal(DecimalDataType::Decimal256(_)) => Ok(32),
            _ => Result::Err(format!(
                "Function number_byte_size argument must be numeric types, but got {:?}",
                self
            )),
        }
    }

    // Nullable will be displayed as Nullable(T)
    pub fn wrapped_display(&self) -> String {
        match self {
            DataType::Nullable(inner_ty) => format!("Nullable({})", inner_ty.wrapped_display()),
            _ => format!("{}", self),
        }
    }

    pub fn sql_name(&self) -> String {
        match self {
            DataType::Number(num_ty) => match num_ty {
                NumberDataType::UInt8 => "TINYINT UNSIGNED".to_string(),
                NumberDataType::UInt16 => "SMALLINT UNSIGNED".to_string(),
                NumberDataType::UInt32 => "INT UNSIGNED".to_string(),
                NumberDataType::UInt64 => "BIGINT UNSIGNED".to_string(),
                NumberDataType::Int8 => "TINYINT".to_string(),
                NumberDataType::Int16 => "SMALLINT".to_string(),
                NumberDataType::Int32 => "INT".to_string(),
                NumberDataType::Int64 => "BIGINT".to_string(),
                NumberDataType::Float32 => "FLOAT".to_string(),
                NumberDataType::Float64 => "DOUBLE".to_string(),
            },
            DataType::String => "VARCHAR".to_string(),
            DataType::Nullable(inner_ty) => format!("{} NULL", inner_ty.sql_name()),
            _ => self.to_string().to_uppercase(),
        }
    }

    // Returns the number of leaf columns of the DataType
    pub fn num_leaf_columns(&self) -> usize {
        match self {
            DataType::Nullable(box inner_ty)
            | DataType::Array(box inner_ty)
            | DataType::Map(box inner_ty) => inner_ty.num_leaf_columns(),
            DataType::Tuple(inner_tys) => inner_tys
                .iter()
                .map(|inner_ty| inner_ty.num_leaf_columns())
                .sum(),
            _ => 1,
        }
    }

    pub fn get_decimal_properties(&self) -> Option<DecimalSize> {
        match self {
            DataType::Decimal(decimal_type) => Some(decimal_type.size()),
            DataType::Number(num_ty) => num_ty.get_decimal_properties(),
            _ => None,
        }
    }
}

pub trait ValueType: Debug + Clone + PartialEq + Sized + 'static {
    type Scalar: Debug + Clone + PartialEq;
    type ScalarRef<'a>: Debug + Clone + PartialEq;
    type Column: Debug + Clone + PartialEq;
    type Domain: Debug + Clone + PartialEq;
    type ColumnIterator<'a>: Iterator<Item = Self::ScalarRef<'a>> + TrustedLen;
    type ColumnBuilder: Debug + Clone;

    /// Upcast GAT type's lifetime.
    fn upcast_gat<'short, 'long: 'short>(long: Self::ScalarRef<'long>) -> Self::ScalarRef<'short>;

    fn to_owned_scalar<'a>(scalar: Self::ScalarRef<'a>) -> Self::Scalar;
    fn to_scalar_ref<'a>(scalar: &'a Self::Scalar) -> Self::ScalarRef<'a>;

    fn try_downcast_scalar<'a>(scalar: &'a ScalarRef) -> Option<Self::ScalarRef<'a>>;
    fn try_downcast_column<'a>(col: &'a Column) -> Option<Self::Column>;
    fn try_downcast_domain(domain: &Domain) -> Option<Self::Domain>;

    /// Downcast `ColumnBuilder` to a mutable reference of its inner builder type.
    ///
    /// Not every builder can be downcasted successfully.
    /// For example: `ArrayType<T: ValueType>`, `NullableType<T: ValueType>`, and `KvPair<K: ValueType, V: ValueType>`
    /// cannot be downcasted and this method will return `None`.
    ///
    /// So when using this method, we cannot unwrap the returned value directly.
    /// We should:
    ///
    /// ```ignore
    /// // builder: ColumnBuilder
    /// // T: ValueType
    /// if let Some(inner) = T::try_downcast_builder(&mut builder) {
    ///     inner.push(...);
    /// } else {
    ///     builder.push(...);
    /// }
    /// ```
    fn try_downcast_builder<'a>(
        builder: &'a mut ColumnBuilder,
    ) -> Option<&'a mut Self::ColumnBuilder>;

    fn upcast_scalar(scalar: Self::Scalar) -> Scalar;
    fn upcast_column(col: Self::Column) -> Column;
    fn upcast_domain(domain: Self::Domain) -> Domain;

    fn column_len<'a>(col: &'a Self::Column) -> usize;
    fn index_column<'a>(col: &'a Self::Column, index: usize) -> Option<Self::ScalarRef<'a>>;

    /// # Safety
    ///
    /// Calling this method with an out-of-bounds index is *[undefined behavior]*
    unsafe fn index_column_unchecked<'a>(
        col: &'a Self::Column,
        index: usize,
    ) -> Self::ScalarRef<'a>;
    fn slice_column<'a>(col: &'a Self::Column, range: Range<usize>) -> Self::Column;
    fn iter_column<'a>(col: &'a Self::Column) -> Self::ColumnIterator<'a>;
    fn column_to_builder(col: Self::Column) -> Self::ColumnBuilder;

    fn builder_len(builder: &Self::ColumnBuilder) -> usize;
    fn push_item(builder: &mut Self::ColumnBuilder, item: Self::ScalarRef<'_>);
    fn push_default(builder: &mut Self::ColumnBuilder);
    fn append_column(builder: &mut Self::ColumnBuilder, other: &Self::Column);
    fn build_column(builder: Self::ColumnBuilder) -> Self::Column;
    fn build_scalar(builder: Self::ColumnBuilder) -> Self::Scalar;

    fn scalar_memory_size<'a>(_: &Self::ScalarRef<'a>) -> usize {
        std::mem::size_of::<Self::Scalar>()
    }

    fn column_memory_size(col: &Self::Column) -> usize {
        Self::column_len(col) * std::mem::size_of::<Self::Scalar>()
    }
}

pub trait ArgType: ValueType {
    fn data_type() -> DataType;
    fn full_domain() -> Self::Domain;
    fn create_builder(capacity: usize, generics: &GenericMap) -> Self::ColumnBuilder;

    fn column_from_vec(vec: Vec<Self::Scalar>, generics: &GenericMap) -> Self::Column {
        Self::column_from_iter(vec.iter().cloned(), generics)
    }

    fn column_from_iter(
        iter: impl Iterator<Item = Self::Scalar>,
        generics: &GenericMap,
    ) -> Self::Column {
        let mut col = Self::create_builder(iter.size_hint().0, generics);
        for item in iter {
            Self::push_item(&mut col, Self::to_scalar_ref(&item));
        }
        Self::build_column(col)
    }

    fn column_from_ref_iter<'a>(
        iter: impl Iterator<Item = Self::ScalarRef<'a>>,
        generics: &GenericMap,
    ) -> Self::Column {
        let mut col = Self::create_builder(iter.size_hint().0, generics);
        for item in iter {
            Self::push_item(&mut col, item);
        }
        Self::build_column(col)
    }
}
