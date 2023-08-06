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

use std::sync::Arc;

use common_expression::DataSchema;
use common_expression::DataSchemaRef;
use common_meta_app::schema::CreateDatabaseReq;
use common_meta_app::schema::DatabaseMeta;
use common_meta_app::schema::DatabaseNameIdent;
use common_meta_app::schema::DropDatabaseReq;
use common_meta_app::schema::UndropDatabaseReq;

/// Create.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CreateDatabasePlan {
    pub if_not_exists: bool,
    pub tenant: String,
    pub catalog: String,
    pub database: String,
    pub meta: DatabaseMeta,
}

impl From<CreateDatabasePlan> for CreateDatabaseReq {
    fn from(p: CreateDatabasePlan) -> Self {
        CreateDatabaseReq {
            if_not_exists: p.if_not_exists,
            name_ident: DatabaseNameIdent {
                tenant: p.tenant,
                db_name: p.database,
            },
            meta: p.meta,
        }
    }
}

impl From<&CreateDatabasePlan> for CreateDatabaseReq {
    fn from(p: &CreateDatabasePlan) -> Self {
        CreateDatabaseReq {
            if_not_exists: p.if_not_exists,
            name_ident: DatabaseNameIdent {
                tenant: p.tenant.clone(),
                db_name: p.database.clone(),
            },
            meta: p.meta.clone(),
        }
    }
}

impl CreateDatabasePlan {
    pub fn schema(&self) -> DataSchemaRef {
        Arc::new(DataSchema::empty())
    }
}

/// Drop.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct DropDatabasePlan {
    pub if_exists: bool,
    pub tenant: String,
    pub catalog: String,
    pub database: String,
}

impl DropDatabasePlan {
    pub fn schema(&self) -> DataSchemaRef {
        Arc::new(DataSchema::empty())
    }
}

impl From<DropDatabasePlan> for DropDatabaseReq {
    fn from(p: DropDatabasePlan) -> Self {
        DropDatabaseReq {
            if_exists: p.if_exists,
            name_ident: DatabaseNameIdent {
                tenant: p.tenant,
                db_name: p.database,
            },
        }
    }
}

impl From<&DropDatabasePlan> for DropDatabaseReq {
    fn from(p: &DropDatabasePlan) -> Self {
        DropDatabaseReq {
            if_exists: p.if_exists,
            name_ident: DatabaseNameIdent {
                tenant: p.tenant.clone(),
                db_name: p.database.clone(),
            },
        }
    }
}

/// Rename.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RenameDatabasePlan {
    pub tenant: String,
    pub entities: Vec<RenameDatabaseEntity>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RenameDatabaseEntity {
    pub if_exists: bool,
    pub catalog: String,
    pub database: String,
    pub new_database: String,
}

impl RenameDatabasePlan {
    pub fn schema(&self) -> DataSchemaRef {
        Arc::new(DataSchema::empty())
    }
}

/// Undrop.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct UndropDatabasePlan {
    pub tenant: String,
    pub catalog: String,
    pub database: String,
}

impl UndropDatabasePlan {
    pub fn schema(&self) -> DataSchemaRef {
        Arc::new(DataSchema::empty())
    }
}

impl From<UndropDatabasePlan> for UndropDatabaseReq {
    fn from(p: UndropDatabasePlan) -> Self {
        UndropDatabaseReq {
            name_ident: DatabaseNameIdent {
                tenant: p.tenant,
                db_name: p.database,
            },
        }
    }
}

/// Use.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct UseDatabasePlan {
    pub database: String,
}

impl UseDatabasePlan {
    pub fn schema(&self) -> DataSchemaRef {
        Arc::new(DataSchema::empty())
    }
}

/// Show.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ShowCreateDatabasePlan {
    pub catalog: String,
    pub database: String,
    pub schema: DataSchemaRef,
}

impl ShowCreateDatabasePlan {
    pub fn schema(&self) -> DataSchemaRef {
        self.schema.clone()
    }
}
