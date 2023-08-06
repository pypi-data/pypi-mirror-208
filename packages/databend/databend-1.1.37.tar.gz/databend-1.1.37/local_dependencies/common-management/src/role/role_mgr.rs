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

use common_exception::ErrorCode;
use common_exception::ToErrorCode;
use common_meta_app::principal::RoleInfo;
use common_meta_kvapi::kvapi;
use common_meta_kvapi::kvapi::UpsertKVReq;
use common_meta_types::IntoSeqV;
use common_meta_types::MatchSeq;
use common_meta_types::MatchSeqExt;
use common_meta_types::MetaError;
use common_meta_types::Operation;
use common_meta_types::SeqV;

use crate::role::role_api::RoleApi;

static ROLE_API_KEY_PREFIX: &str = "__fd_roles";

pub struct RoleMgr {
    kv_api: Arc<dyn kvapi::KVApi<Error = MetaError>>,
    role_prefix: String,
}

impl RoleMgr {
    pub fn create(
        kv_api: Arc<dyn kvapi::KVApi<Error = MetaError>>,
        tenant: &str,
    ) -> Result<Self, ErrorCode> {
        if tenant.is_empty() {
            return Err(ErrorCode::TenantIsEmpty(
                "Tenant can not empty(while role mgr create)",
            ));
        }

        Ok(RoleMgr {
            kv_api,
            role_prefix: format!("{}/{}", ROLE_API_KEY_PREFIX, tenant),
        })
    }

    #[async_backtrace::framed]
    async fn upsert_role_info(
        &self,
        role_info: &RoleInfo,
        seq: MatchSeq,
    ) -> Result<u64, ErrorCode> {
        let key = self.make_role_key(role_info.identity());
        let value = serde_json::to_vec(&role_info)?;

        let kv_api = self.kv_api.clone();
        let res = kv_api
            .upsert_kv(UpsertKVReq::new(&key, seq, Operation::Update(value), None))
            .await?;
        match res.result {
            Some(SeqV { seq: s, .. }) => Ok(s),
            None => Err(ErrorCode::UnknownRole(format!(
                "unknown role, or seq not match {}",
                role_info.name
            ))),
        }
    }

    fn make_role_key(&self, role: &str) -> String {
        format!("{}/{}", self.role_prefix, role)
    }
}

#[async_trait::async_trait]
impl RoleApi for RoleMgr {
    #[async_backtrace::framed]
    async fn add_role(&self, role_info: RoleInfo) -> common_exception::Result<u64> {
        let match_seq = MatchSeq::Exact(0);
        let key = self.make_role_key(role_info.identity());
        let value = serde_json::to_vec(&role_info)?;

        let kv_api = self.kv_api.clone();
        let upsert_kv = kv_api.upsert_kv(UpsertKVReq::new(
            &key,
            match_seq,
            Operation::Update(value),
            None,
        ));

        let res = upsert_kv.await?.added_or_else(|v| {
            ErrorCode::UserAlreadyExists(format!("Role already exists, seq [{}]", v.seq))
        })?;

        Ok(res.seq)
    }

    #[async_backtrace::framed]
    async fn get_role(&self, role: &String, seq: MatchSeq) -> Result<SeqV<RoleInfo>, ErrorCode> {
        let key = self.make_role_key(role);
        let res = self.kv_api.get_kv(&key).await?;
        let seq_value =
            res.ok_or_else(|| ErrorCode::UnknownRole(format!("unknown role {}", role)))?;

        match seq.match_seq(&seq_value) {
            Ok(_) => Ok(seq_value.into_seqv()?),
            Err(_) => Err(ErrorCode::UnknownRole(format!("unknown role {}", role))),
        }
    }

    #[async_backtrace::framed]
    async fn get_roles(&self) -> Result<Vec<SeqV<RoleInfo>>, ErrorCode> {
        let role_prefix = self.role_prefix.clone();
        let kv_api = self.kv_api.clone();
        let values = kv_api.prefix_list_kv(role_prefix.as_str()).await?;

        let mut r = vec![];
        for (_key, val) in values {
            let u = serde_json::from_slice::<RoleInfo>(&val.data)
                .map_err_to_code(ErrorCode::IllegalUserInfoFormat, || "")?;

            r.push(SeqV::new(val.seq, u));
        }

        Ok(r)
    }

    /// General role update.
    ///
    /// It fetch the role that matches the specified seq number, update it in place, then write it back with the seq it sees.
    ///
    /// Seq number ensures there is no other write happens between get and set.
    #[async_backtrace::framed]
    async fn update_role_with<F>(
        &self,
        role: &String,
        seq: MatchSeq,
        f: F,
    ) -> Result<Option<u64>, ErrorCode>
    where
        F: FnOnce(&mut RoleInfo) + Send,
    {
        let SeqV {
            seq,
            data: mut role_info,
            ..
        } = self.get_role(role, seq).await?;

        f(&mut role_info);

        let seq = self
            .upsert_role_info(&role_info, MatchSeq::Exact(seq))
            .await?;
        Ok(Some(seq))
    }

    #[async_backtrace::framed]
    async fn drop_role(&self, role: String, seq: MatchSeq) -> Result<(), ErrorCode> {
        let key = self.make_role_key(&role);
        let kv_api = self.kv_api.clone();
        let res = kv_api
            .upsert_kv(UpsertKVReq::new(&key, seq, Operation::Delete, None))
            .await?;
        if res.prev.is_some() && res.result.is_none() {
            Ok(())
        } else {
            Err(ErrorCode::UnknownRole(format!("unknown role {}", role)))
        }
    }
}
