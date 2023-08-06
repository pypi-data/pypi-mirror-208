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

pub use common_catalog::catalog::StorageDescription;
use common_config::InnerConfig;
use common_exception::ErrorCode;
use common_exception::Result;
use common_meta_app::schema::TableInfo;
use common_storages_memory::MemoryTable;
use common_storages_null::NullTable;
use common_storages_random::RandomTable;
use common_storages_view::view_table::ViewTable;
use dashmap::DashMap;

use crate::fuse::FuseTable;
use crate::Table;

pub trait StorageCreator: Send + Sync {
    fn try_create(&self, table_info: TableInfo) -> Result<Box<dyn Table>>;
}

impl<T> StorageCreator for T
where
    T: Fn(TableInfo) -> Result<Box<dyn Table>>,
    T: Send + Sync,
{
    fn try_create(&self, table_info: TableInfo) -> Result<Box<dyn Table>> {
        self(table_info)
    }
}

pub trait StorageDescriptor: Send + Sync {
    fn description(&self) -> StorageDescription;
}

impl<T> StorageDescriptor for T
where
    T: Fn() -> StorageDescription,
    T: Send + Sync,
{
    fn description(&self) -> StorageDescription {
        self()
    }
}

pub struct Storage {
    creator: Arc<dyn StorageCreator>,
    descriptor: Arc<dyn StorageDescriptor>,
}

#[derive(Default)]
pub struct StorageFactory {
    storages: DashMap<String, Storage>,
}

impl StorageFactory {
    pub fn create(conf: InnerConfig) -> Self {
        let creators: DashMap<String, Storage> = Default::default();

        // Register memory table engine.
        if conf.query.table_engine_memory_enabled {
            creators.insert("MEMORY".to_string(), Storage {
                creator: Arc::new(MemoryTable::try_create),
                descriptor: Arc::new(MemoryTable::description),
            });
        }

        // Register NULL table engine.
        creators.insert("NULL".to_string(), Storage {
            creator: Arc::new(NullTable::try_create),
            descriptor: Arc::new(NullTable::description),
        });

        // Register FUSE table engine.
        creators.insert("FUSE".to_string(), Storage {
            creator: Arc::new(FuseTable::try_create),
            descriptor: Arc::new(FuseTable::description),
        });

        // Register View table engine
        creators.insert("VIEW".to_string(), Storage {
            creator: Arc::new(ViewTable::try_create),
            descriptor: Arc::new(ViewTable::description),
        });

        // Register RANDOM table engine
        creators.insert("RANDOM".to_string(), Storage {
            creator: Arc::new(RandomTable::try_create),
            descriptor: Arc::new(RandomTable::description),
        });

        StorageFactory { storages: creators }
    }

    pub fn get_table(&self, table_info: &TableInfo) -> Result<Arc<dyn Table>> {
        let engine = table_info.engine().to_uppercase();
        let factory = self.storages.get(&engine).ok_or_else(|| {
            ErrorCode::UnknownTableEngine(format!("Unknown table engine {}", engine))
        })?;

        let table: Arc<dyn Table> = factory.creator.try_create(table_info.clone())?.into();
        Ok(table)
    }

    pub fn get_storage_descriptors(&self) -> Vec<StorageDescription> {
        let mut descriptors = Vec::with_capacity(self.storages.len());
        let it = self.storages.iter();
        for entry in it {
            descriptors.push(entry.value().descriptor.description())
        }
        descriptors
    }
}
