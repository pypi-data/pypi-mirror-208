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

use common_base::base::escape_for_key;
use common_exception::ErrorCode;
use common_exception::Result;
use common_meta_app::principal::UserDefinedFileFormat;
use common_meta_kvapi::kvapi;
use common_meta_kvapi::kvapi::UpsertKVReq;
use common_meta_types::MatchSeq;
use common_meta_types::MatchSeqExt;
use common_meta_types::MetaError;
use common_meta_types::Operation;
use common_meta_types::SeqV;

use crate::serde::deserialize_struct;
use crate::serde::serialize_struct;
use crate::FileFormatApi;

static USER_FILE_FORMAT_API_KEY_PREFIX: &str = "__fd_file_formats";

pub struct FileFormatMgr {
    kv_api: Arc<dyn kvapi::KVApi<Error = MetaError>>,
    file_format_prefix: String,
}

impl FileFormatMgr {
    pub fn create(kv_api: Arc<dyn kvapi::KVApi<Error = MetaError>>, tenant: &str) -> Result<Self> {
        if tenant.is_empty() {
            return Err(ErrorCode::TenantIsEmpty(
                "Tenant can not empty(while role mgr create)",
            ));
        }

        Ok(Self {
            kv_api,
            file_format_prefix: format!(
                "{}/{}",
                USER_FILE_FORMAT_API_KEY_PREFIX,
                escape_for_key(tenant)?
            ),
        })
    }
}

#[async_trait::async_trait]
impl FileFormatApi for FileFormatMgr {
    #[async_backtrace::framed]
    async fn add_file_format(&self, info: UserDefinedFileFormat) -> Result<u64> {
        let seq = MatchSeq::Exact(0);
        let val = Operation::Update(serialize_struct(
            &info,
            ErrorCode::IllegalFileFormat,
            || "",
        )?);
        let key = format!(
            "{}/{}",
            self.file_format_prefix,
            escape_for_key(&info.name)?
        );
        let upsert_info = self
            .kv_api
            .upsert_kv(UpsertKVReq::new(&key, seq, val, None));

        let res = upsert_info.await?.added_or_else(|v| {
            ErrorCode::FileFormatAlreadyExists(format!(
                "file_format already exists, seq [{}]",
                v.seq
            ))
        })?;

        Ok(res.seq)
    }

    #[async_backtrace::framed]
    async fn get_file_format(
        &self,
        name: &str,
        seq: MatchSeq,
    ) -> Result<SeqV<UserDefinedFileFormat>> {
        let key = format!("{}/{}", self.file_format_prefix, escape_for_key(name)?);
        let kv_api = self.kv_api.clone();
        let get_kv = async move { kv_api.get_kv(&key).await };
        let res = get_kv.await?;
        let seq_value = res
            .ok_or_else(|| ErrorCode::UnknownFileFormat(format!("Unknown file_format {}", name)))?;

        match seq.match_seq(&seq_value) {
            Ok(_) => Ok(SeqV::new(
                seq_value.seq,
                deserialize_struct(&seq_value.data, ErrorCode::IllegalFileFormat, || "")?,
            )),
            Err(_) => Err(ErrorCode::UnknownFileFormat(format!(
                "Unknown file_format {}",
                name
            ))),
        }
    }

    #[async_backtrace::framed]
    async fn get_file_formats(&self) -> Result<Vec<UserDefinedFileFormat>> {
        let values = self.kv_api.prefix_list_kv(&self.file_format_prefix).await?;

        let mut file_format_infos = Vec::with_capacity(values.len());
        for (_, value) in values {
            let file_format_info =
                deserialize_struct(&value.data, ErrorCode::IllegalFileFormat, || "")?;
            file_format_infos.push(file_format_info);
        }
        Ok(file_format_infos)
    }

    #[async_backtrace::framed]
    async fn drop_file_format(&self, name: &str, seq: MatchSeq) -> Result<()> {
        let key = format!("{}/{}", self.file_format_prefix, escape_for_key(name)?);
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
            Err(ErrorCode::UnknownFileFormat(format!(
                "Unknown FileFormat {}",
                name
            )))
        }
    }
}
