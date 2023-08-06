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
use common_exception::Result;
use common_meta_app::principal::UserSetting;
use common_meta_kvapi::kvapi;
use common_meta_kvapi::kvapi::UpsertKVReq;
use common_meta_types::IntoSeqV;
use common_meta_types::MatchSeq;
use common_meta_types::MatchSeqExt;
use common_meta_types::MetaError;
use common_meta_types::Operation;
use common_meta_types::SeqV;

use crate::setting::SettingApi;

static USER_SETTING_API_KEY_PREFIX: &str = "__fd_settings";

pub struct SettingMgr {
    kv_api: Arc<dyn kvapi::KVApi<Error = MetaError>>,
    setting_prefix: String,
}

impl SettingMgr {
    #[allow(dead_code)]
    pub fn create(kv_api: Arc<dyn kvapi::KVApi<Error = MetaError>>, tenant: &str) -> Result<Self> {
        Ok(SettingMgr {
            kv_api,
            setting_prefix: format!("{}/{}", USER_SETTING_API_KEY_PREFIX, tenant),
        })
    }
}

#[async_trait::async_trait]
impl SettingApi for SettingMgr {
    #[async_backtrace::framed]
    async fn set_setting(&self, setting: UserSetting) -> Result<u64> {
        // Upsert.
        let seq = MatchSeq::GE(0);
        let val = Operation::Update(serde_json::to_vec(&setting)?);
        let key = format!("{}/{}", self.setting_prefix, setting.name);
        let upsert = self
            .kv_api
            .upsert_kv(UpsertKVReq::new(&key, seq, val, None));

        let res = upsert.await?.added_or_else(|v| v);

        match res {
            Ok(added) => Ok(added.seq),
            Err(existing) => Ok(existing.seq),
        }
    }

    #[async_backtrace::framed]
    async fn get_settings(&self) -> Result<Vec<UserSetting>> {
        let values = self.kv_api.prefix_list_kv(&self.setting_prefix).await?;

        let mut settings = Vec::with_capacity(values.len());
        for (_, value) in values {
            let setting = serde_json::from_slice::<UserSetting>(&value.data)?;
            settings.push(setting);
        }
        Ok(settings)
    }

    #[async_backtrace::framed]
    async fn get_setting(&self, name: &str, seq: MatchSeq) -> Result<SeqV<UserSetting>> {
        let key = format!("{}/{}", self.setting_prefix, name);
        let kv_api = self.kv_api.clone();
        let get_kv = async move { kv_api.get_kv(&key).await };
        let res = get_kv.await?;
        let seq_value =
            res.ok_or_else(|| ErrorCode::UnknownVariable(format!("Unknown setting {}", name)))?;

        match seq.match_seq(&seq_value) {
            Ok(_) => Ok(seq_value.into_seqv()?),
            Err(_) => Err(ErrorCode::UnknownVariable(format!(
                "Unknown setting {}",
                name
            ))),
        }
    }

    #[async_backtrace::framed]
    async fn drop_setting(&self, name: &str, seq: MatchSeq) -> Result<()> {
        let key = format!("{}/{}", self.setting_prefix, name);
        let kv_api = self.kv_api.clone();
        let upsert_kv = async move {
            kv_api
                .upsert_kv(UpsertKVReq::new(&key, seq, Operation::Delete, None))
                .await
        };
        let res = upsert_kv.await?;
        if res.prev.is_some() && res.result.is_none() {
            Ok(())
        } else {
            Err(ErrorCode::UnknownVariable(format!(
                "Unknown setting {}",
                name
            )))
        }
    }
}
