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

use common_ast::ast::Expr;
use common_catalog::table_args::TableArgs;
use common_exception::ErrorCode;
use common_exception::Result;
use common_expression::ConstantFolder;
use common_expression::Scalar;
use common_functions::BUILTIN_FUNCTIONS;

use crate::plans::ConstantExpr;
use crate::ScalarBinder;
use crate::ScalarExpr;

#[async_backtrace::framed]
pub async fn bind_table_args(
    scalar_binder: &mut ScalarBinder<'_>,
    params: &Vec<Expr>,
    named_params: &Vec<(String, Expr)>,
) -> Result<TableArgs> {
    let mut args = Vec::with_capacity(params.len());
    for arg in params.iter() {
        args.push(scalar_binder.bind(arg).await?.0);
    }

    let mut named_args = Vec::with_capacity(named_params.len());
    for (name, arg) in named_params.iter() {
        named_args.push((name.clone(), scalar_binder.bind(arg).await?.0));
    }

    let positioned_args = args
        .into_iter()
        .map(|scalar| {
            let expr = scalar.as_expr()?;
            let (expr, _) =
                ConstantFolder::fold(&expr, &scalar_binder.get_func_ctx()?, &BUILTIN_FUNCTIONS);
            match expr {
                common_expression::Expr::Constant { scalar, .. } => Ok(scalar),
                _ => Err(ErrorCode::Unimplemented(format!(
                    "Unsupported table argument type: {:?}",
                    scalar
                ))),
            }
        })
        .collect::<Result<Vec<_>>>()?;

    let named_args: HashMap<String, Scalar> = named_args
        .into_iter()
        .map(|(name, scalar)| match scalar {
            ScalarExpr::ConstantExpr(ConstantExpr { value, .. }) => Ok((name, value)),
            _ => Err(ErrorCode::Unimplemented(format!(
                "Unsupported table named argument type: {:?}",
                scalar
            ))),
        })
        .collect::<Result<HashMap<_, _>>>()?;

    Ok(TableArgs {
        positioned: positioned_args,
        named: named_args,
    })
}
