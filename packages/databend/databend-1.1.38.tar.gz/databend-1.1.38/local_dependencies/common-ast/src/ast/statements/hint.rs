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

use crate::ast::Expr;
use crate::ast::Identifier;

#[derive(Debug, Clone, PartialEq)]
pub struct Hint {
    pub hints_list: Vec<HintItem>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct HintItem {
    pub name: Identifier,
    pub expr: Expr,
}

impl Display for Hint {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "/*+ ")?;
        for hint in &self.hints_list {
            write!(f, "SET_VAR(")?;
            write!(f, "{}", hint.name)?;
            write!(f, "=")?;
            write!(f, "{}", hint.expr)?;
            write!(f, ") ")?;
        }
        write!(f, "*/")
    }
}
