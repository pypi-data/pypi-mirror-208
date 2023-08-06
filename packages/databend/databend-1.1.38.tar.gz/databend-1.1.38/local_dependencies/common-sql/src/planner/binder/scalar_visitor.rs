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

use common_exception::Result;

use crate::plans::ScalarExpr;
use crate::plans::WindowFunc;
use crate::plans::WindowFuncType;

/// Controls how the visitor recursion should proceed.
pub enum Recursion<V: ScalarVisitor> {
    /// Attempt to visit all the children, recursively, of this expression.
    Continue(V),
    /// Do not visit the children of this expression, though the walk
    /// of parents of this expression will not be affected
    Stop(V),
}

/// Encode the traversal of an scalar tree. When passed to
/// `Scalar::accept`, `ScalarVisitor::visit` is invoked
/// recursively on all nodes of an scalar tree. See the comments
/// on `Scalar::accept` for details on its use
pub trait ScalarVisitor: Sized {
    /// Invoked before any children of `expr` are visited.
    fn pre_visit(self, scalar: &ScalarExpr) -> Result<Recursion<Self>>;

    fn visit(mut self, predecessor_scalar: &ScalarExpr) -> Result<Self> {
        let mut stack = vec![RecursionProcessing::Call(predecessor_scalar)];
        while let Some(element) = stack.pop() {
            match element {
                RecursionProcessing::Ret(scalar) => {
                    self = self.post_visit(scalar)?;
                }
                RecursionProcessing::Call(scalar) => {
                    stack.push(RecursionProcessing::Ret(scalar));
                    self = match self.pre_visit(scalar)? {
                        Recursion::Stop(visitor) => visitor,
                        Recursion::Continue(visitor) => {
                            match scalar {
                                ScalarExpr::AggregateFunction(func) => {
                                    for arg in &func.args {
                                        stack.push(RecursionProcessing::Call(arg));
                                    }
                                }
                                ScalarExpr::WindowFunction(WindowFunc {
                                    func,
                                    partition_by,
                                    order_by,
                                    ..
                                }) => {
                                    if let WindowFuncType::Aggregate(agg) = func {
                                        for arg in &agg.args {
                                            stack.push(RecursionProcessing::Call(arg));
                                        }
                                    }
                                    for arg in partition_by.iter() {
                                        stack.push(RecursionProcessing::Call(arg));
                                    }
                                    for arg in order_by.iter() {
                                        stack.push(RecursionProcessing::Call(&arg.expr));
                                    }
                                }
                                ScalarExpr::FunctionCall(func) => {
                                    for arg in func.arguments.iter() {
                                        stack.push(RecursionProcessing::Call(arg));
                                    }
                                }
                                ScalarExpr::BoundColumnRef(_) | ScalarExpr::ConstantExpr(_) => {}
                                ScalarExpr::CastExpr(cast) => {
                                    stack.push(RecursionProcessing::Call(&cast.argument))
                                }
                                ScalarExpr::SubqueryExpr(_) => {}
                            }

                            visitor
                        }
                    }
                }
            }
        }

        Ok(self)
    }

    /// Invoked after all children of `expr` are visited. Default
    /// implementation does nothing.
    fn post_visit(self, _expr: &ScalarExpr) -> Result<Self> {
        Ok(self)
    }
}

impl ScalarExpr {
    /// Performs a depth first walk of an scalar expression and
    /// its children, calling [`ScalarVisitor::pre_visit`] and
    /// `visitor.post_visit`.
    ///
    /// Implements the [visitor pattern](https://en.wikipedia.org/wiki/Visitor_pattern) to
    /// separate scalar expression algorithms from the structure of the
    /// `Scalar` tree and make it easier to add new types of scalar expressions
    /// and algorithms that walk the tree.
    ///
    /// For a scala rexpression tree such as
    /// ```text
    /// BinaryExpr (GT)
    ///    left: Column("foo")
    ///    right: Column("bar")
    /// ```
    ///
    /// The nodes are visited using the following order
    /// ```text
    /// pre_visit(ScalarFunction(GT))
    /// pre_visit(Column("foo"))
    /// post_visit(Column("foo"))
    /// pre_visit(Column("bar"))
    /// post_visit(Column("bar"))
    /// post_visit(ScalarFunction(GT))
    /// ```
    ///
    /// If an Err result is returned, recursion is stopped immediately
    pub fn accept<V: ScalarVisitor>(&self, visitor: V) -> Result<V> {
        let visitor = match visitor.pre_visit(self)? {
            Recursion::Continue(visitor) => visitor,
            // If the recursion should stop, do not visit children
            Recursion::Stop(visitor) => return Ok(visitor),
        };

        let visitor = visitor.visit(self)?;
        visitor.post_visit(self)
    }
}

enum RecursionProcessing<'a> {
    Call(&'a ScalarExpr),
    Ret(&'a ScalarExpr),
}
