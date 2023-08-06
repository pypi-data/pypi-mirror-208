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

use std::collections::BTreeMap;
use std::sync::Arc;

use common_arrow::arrow::datatypes::Field;
use common_arrow::arrow::io::parquet::write::to_parquet_schema;
use common_arrow::parquet::metadata::SchemaDescriptor;
use common_catalog::plan::Projection;
use common_catalog::table_context::TableContext;
use common_exception::ErrorCode;
use common_exception::Result;
use common_expression::types::DataType;
use common_expression::ColumnId;
use common_expression::DataField;
use common_expression::DataSchema;
use common_expression::FieldIndex;
use common_expression::Scalar;
use common_expression::TableField;
use common_expression::TableSchemaRef;
use common_sql::field_default_value;
use common_storage::ColumnNode;
use common_storage::ColumnNodes;
use opendal::Operator;

// TODO: make BlockReader as a trait.
#[derive(Clone)]
pub struct BlockReader {
    pub(crate) operator: Operator,
    pub(crate) projection: Projection,
    pub(crate) projected_schema: TableSchemaRef,
    pub(crate) project_indices: BTreeMap<FieldIndex, (ColumnId, Field, DataType)>,
    pub(crate) project_column_nodes: Vec<ColumnNode>,
    pub(crate) parquet_schema_descriptor: SchemaDescriptor,
    pub(crate) default_vals: Vec<Scalar>,
    pub query_internal_columns: bool,
}

fn inner_project_field_default_values(default_vals: &[Scalar], paths: &[usize]) -> Result<Scalar> {
    if paths.is_empty() {
        return Err(ErrorCode::BadArguments(
            "path should not be empty".to_string(),
        ));
    }
    let index = paths[0];
    if paths.len() == 1 {
        return Ok(default_vals[index].clone());
    }

    match &default_vals[index] {
        Scalar::Tuple(s) => inner_project_field_default_values(s, &paths[1..]),
        _ => {
            if paths.len() > 1 {
                return Err(ErrorCode::BadArguments(
                    "Unable to get field default value by paths".to_string(),
                ));
            }
            inner_project_field_default_values(&[default_vals[index].clone()], &paths[1..])
        }
    }
}

impl BlockReader {
    pub fn create(
        operator: Operator,
        schema: TableSchemaRef,
        projection: Projection,
        ctx: Arc<dyn TableContext>,
        query_internal_columns: bool,
    ) -> Result<Arc<BlockReader>> {
        // init projected_schema and default_vals of schema.fields
        let (projected_schema, default_vals) = match projection {
            Projection::Columns(ref indices) => {
                let projected_schema = TableSchemaRef::new(schema.project(indices));
                // If projection by Columns, just calc default values by projected fields.
                let mut default_vals = Vec::with_capacity(projected_schema.fields().len());
                for field in projected_schema.fields() {
                    let default_val = field_default_value(ctx.clone(), field)?;
                    default_vals.push(default_val);
                }

                (projected_schema, default_vals)
            }
            Projection::InnerColumns(ref path_indices) => {
                let projected_schema = TableSchemaRef::new(schema.inner_project(path_indices));
                let mut field_default_vals = Vec::with_capacity(schema.fields().len());

                // If projection by InnerColumns, first calc default value of all schema fields.
                for field in schema.fields() {
                    field_default_vals.push(field_default_value(ctx.clone(), field)?);
                }

                // Then calc project scalars by path_indices
                let mut default_vals = Vec::with_capacity(schema.fields().len());
                path_indices.values().for_each(|path| {
                    default_vals.push(
                        inner_project_field_default_values(&field_default_vals, path).unwrap(),
                    );
                });

                (projected_schema, default_vals)
            }
        };

        let arrow_schema = schema.to_arrow();
        let parquet_schema_descriptor = to_parquet_schema(&arrow_schema)?;

        let column_nodes = ColumnNodes::new_from_schema(&arrow_schema, Some(&schema));

        let project_column_nodes: Vec<ColumnNode> = projection
            .project_column_nodes(&column_nodes)?
            .iter()
            .map(|c| (*c).clone())
            .collect();
        let project_indices = Self::build_projection_indices(&project_column_nodes);

        Ok(Arc::new(BlockReader {
            operator,
            projection,
            projected_schema,
            project_indices,
            project_column_nodes,
            parquet_schema_descriptor,
            default_vals,
            query_internal_columns,
        }))
    }

    pub fn support_blocking_api(&self) -> bool {
        self.operator.info().can_blocking()
    }

    // Build non duplicate leaf_indices to avoid repeated read column from parquet
    pub(crate) fn build_projection_indices(
        columns: &[ColumnNode],
    ) -> BTreeMap<FieldIndex, (ColumnId, Field, DataType)> {
        let mut indices = BTreeMap::new();
        for column in columns {
            for (i, index) in column.leaf_indices.iter().enumerate() {
                let f: TableField = (&column.field).into();
                let data_type: DataType = f.data_type().into();
                indices.insert(
                    *index,
                    (column.leaf_column_ids[i], column.field.clone(), data_type),
                );
            }
        }
        indices
    }

    pub fn query_internal_columns(&self) -> bool {
        self.query_internal_columns
    }

    pub fn schema(&self) -> TableSchemaRef {
        self.projected_schema.clone()
    }

    pub fn data_fields(&self) -> Vec<DataField> {
        self.schema().fields().iter().map(DataField::from).collect()
    }

    pub fn data_schema(&self) -> DataSchema {
        let fields = self.data_fields();
        DataSchema::new(fields)
    }
}
