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

use std::hash::BuildHasher;
use std::hash::Hash;
use std::sync::Arc;

use common_cache::Count;
use common_cache::CountableMeter;
use common_cache::DefaultHashBuilder;

use crate::metrics_inc_cache_access_count;
use crate::metrics_inc_cache_hit_count;
use crate::metrics_inc_cache_miss_count;

// The cache accessor, crate users usually working on this interface while manipulating caches
pub trait CacheAccessor<K, V, S = DefaultHashBuilder, M = Count>
where
    K: Eq + Hash,
    S: BuildHasher,
    M: CountableMeter<K, Arc<V>>,
{
    fn get<Q: AsRef<str>>(&self, k: Q) -> Option<Arc<V>>;
    fn put(&self, key: K, value: Arc<V>);
    fn evict(&self, k: &str) -> bool;
    fn contains_key(&self, k: &str) -> bool;
    fn size(&self) -> u64;
    fn len(&self) -> usize;
    fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

/// Helper trait to convert a Cache into NamedCache
pub trait Named
where Self: Sized
{
    fn name_with(self, name: impl Into<String>) -> NamedCache<Self> {
        NamedCache {
            name: name.into(),
            cache: self,
        }
    }
}

impl<T> Named for T where T: Sized + Clone {}

/// A named cache that with embedded metrics logging
#[derive(Clone)]
pub struct NamedCache<C> {
    name: String,
    cache: C,
}

impl<C> NamedCache<C> {
    #[inline]
    pub fn name(&self) -> &str {
        &self.name
    }
}

impl<K, V, S, M, C> CacheAccessor<K, V, S, M> for NamedCache<C>
where
    C: CacheAccessor<K, V, S, M>,
    K: Eq + Hash,
    S: BuildHasher,
    M: CountableMeter<K, Arc<V>>,
{
    fn get<Q: AsRef<str>>(&self, k: Q) -> Option<Arc<V>> {
        metrics_inc_cache_access_count(1, &self.name);
        match self.cache.get(k) {
            None => {
                metrics_inc_cache_miss_count(1, &self.name);
                None
            }
            v @ Some(_) => {
                metrics_inc_cache_hit_count(1, &self.name);
                v
            }
        }
    }

    fn put(&self, key: K, value: Arc<V>) {
        self.cache.put(key, value)
    }

    fn evict(&self, k: &str) -> bool {
        self.cache.evict(k)
    }

    fn size(&self) -> u64 {
        self.cache.size()
    }

    fn len(&self) -> usize {
        self.cache.len()
    }

    fn contains_key(&self, k: &str) -> bool {
        self.cache.contains_key(k)
    }
}
