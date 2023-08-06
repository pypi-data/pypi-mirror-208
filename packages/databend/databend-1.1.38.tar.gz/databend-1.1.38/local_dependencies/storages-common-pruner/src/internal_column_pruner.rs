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

use common_expression::types::string::StringDomain;
use common_expression::ConstantFolder;
use common_expression::Domain;
use common_expression::Expr;
use common_expression::FunctionContext;
use common_expression::Scalar;
use common_expression::BLOCK_NAME_COL_NAME;
use common_expression::SEGMENT_NAME_COL_NAME;
use common_functions::BUILTIN_FUNCTIONS;

/// Only support `_segment_name` and `_block_name` now.
pub struct InternalColumnPruner {
    func_ctx: FunctionContext,
    expr: Expr<String>,
    input_domains: HashMap<String, Domain>,
}

impl InternalColumnPruner {
    pub fn try_create(func_ctx: FunctionContext, expr: Option<&Expr<String>>) -> Option<Arc<Self>> {
        if let Some(expr) = expr {
            let exprs = expr.column_refs();
            if !exprs.contains_key(SEGMENT_NAME_COL_NAME)
                && !exprs.contains_key(BLOCK_NAME_COL_NAME)
            {
                None
            } else {
                let input_domains = exprs
                    .into_iter()
                    .map(|(name, ty)| (name, Domain::full(&ty)))
                    .collect();
                Some(Arc::new(InternalColumnPruner {
                    func_ctx,
                    expr: expr.clone(),
                    input_domains,
                }))
            }
        } else {
            None
        }
    }

    pub fn should_keep(&self, col_name: &str, value: &str) -> bool {
        if self.input_domains.contains_key(col_name) {
            let mut input_domains = self.input_domains.clone();
            let bytes = value.as_bytes().to_vec();
            let domain = Domain::String(StringDomain {
                min: bytes.clone(),
                max: Some(bytes),
            });
            input_domains.insert(col_name.to_string(), domain);

            let (folded_expr, _) = ConstantFolder::fold_with_domain(
                &self.expr,
                &input_domains,
                &self.func_ctx,
                &BUILTIN_FUNCTIONS,
            );

            !matches!(folded_expr, Expr::Constant {
                scalar: Scalar::Boolean(false),
                ..
            })
        } else {
            true
        }
    }
}
