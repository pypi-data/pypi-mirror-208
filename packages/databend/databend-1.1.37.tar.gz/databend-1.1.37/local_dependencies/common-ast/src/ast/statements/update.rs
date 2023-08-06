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

use std::fmt::Display;
use std::fmt::Formatter;

use crate::ast::write_comma_separated_list;
use crate::ast::Expr;
use crate::ast::Hint;
use crate::ast::Identifier;
use crate::ast::TableReference;

#[derive(Debug, Clone, PartialEq)]
pub struct UpdateStmt {
    pub hints: Option<Hint>,
    pub table: TableReference,
    pub update_list: Vec<UpdateExpr>,
    pub selection: Option<Expr>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct UpdateExpr {
    pub name: Identifier,
    pub expr: Expr,
}

impl Display for UpdateStmt {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "UPDATE ")?;
        if let Some(hints) = &self.hints {
            write!(f, "{} ", hints)?;
        }
        write!(f, "{} SET ", self.table)?;
        write_comma_separated_list(f, &self.update_list)?;
        if let Some(conditions) = &self.selection {
            write!(f, " WHERE {conditions}")?;
        }
        Ok(())
    }
}

impl Display for UpdateExpr {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "{} = {}", self.name, self.expr)
    }
}
