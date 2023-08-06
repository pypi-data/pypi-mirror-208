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

use std::collections::HashSet;

use common_ast::ast::Expr;
use common_ast::ast::Identifier;
use common_ast::ast::Literal;
use common_ast::ast::Window;
use common_ast::walk_expr;
use common_ast::Visitor;
use common_exception::ErrorCode;
use common_exception::Result;
use common_exception::Span;
use common_functions::is_builtin_function;

#[derive(Default)]
pub struct UDFValidator {
    pub name: String,
    pub parameters: Vec<String>,

    pub expr_params: HashSet<String>,
    pub has_recursive: bool,
}

impl UDFValidator {
    pub fn verify_definition_expr(&mut self, definition_expr: &Expr) -> Result<()> {
        self.expr_params.clear();

        walk_expr(self, definition_expr);

        if self.has_recursive {
            return Err(ErrorCode::SyntaxException("Recursive UDF is not supported"));
        }
        let expr_params = &self.expr_params;
        let parameters = self.parameters.iter().cloned().collect::<HashSet<_>>();

        let params_not_declared: HashSet<_> = parameters.difference(expr_params).collect();
        let params_not_used: HashSet<_> = expr_params.difference(&parameters).collect();

        if params_not_declared.is_empty() && params_not_used.is_empty() {
            return Ok(());
        }

        Err(ErrorCode::SyntaxException(format!(
            "{}{}",
            if params_not_declared.is_empty() {
                "".to_string()
            } else {
                format!("Parameters are not declared: {:?}", params_not_declared)
            },
            if params_not_used.is_empty() {
                "".to_string()
            } else {
                format!("Parameters are not used: {:?}", params_not_used)
            },
        )))
    }
}

impl<'ast> Visitor<'ast> for UDFValidator {
    fn visit_column_ref(
        &mut self,
        _span: Span,
        _database: &'ast Option<Identifier>,
        _table: &'ast Option<Identifier>,
        column: &'ast Identifier,
    ) {
        self.expr_params.insert(column.to_string());
    }

    fn visit_function_call(
        &mut self,
        _span: Span,
        _distinct: bool,
        name: &'ast Identifier,
        args: &'ast [Expr],
        _params: &'ast [Literal],
        over: &'ast Option<Window>,
    ) {
        let name = name.to_string();
        if !is_builtin_function(&name) && self.name.eq_ignore_ascii_case(&name) {
            self.has_recursive = true;
            return;
        }

        for arg in args {
            walk_expr(self, arg);
        }

        if let Some(over) = over {
            match over {
                Window::WindowSpec(spec) => {
                    spec.partition_by
                        .iter()
                        .for_each(|expr| walk_expr(self, expr));
                    spec.order_by
                        .iter()
                        .for_each(|expr| walk_expr(self, &expr.expr));

                    if let Some(frame) = &spec.window_frame {
                        self.visit_frame_bound(&frame.start_bound);
                        self.visit_frame_bound(&frame.end_bound);
                    }
                }
                Window::WindowReference(reference) => {
                    self.visit_identifier(&reference.window_name);
                }
            }
        }
    }
}
