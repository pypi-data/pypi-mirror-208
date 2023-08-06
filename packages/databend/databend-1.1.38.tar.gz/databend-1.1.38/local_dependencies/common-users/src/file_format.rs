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

use common_exception::ErrorCode;
use common_exception::Result;
use common_meta_app::principal::UserDefinedFileFormat;
use common_meta_types::MatchSeq;

use crate::UserApiProvider;

/// user file_format operations.
impl UserApiProvider {
    // Add a new file_format.
    #[async_backtrace::framed]
    pub async fn add_file_format(
        &self,
        tenant: &str,
        file_format_options: UserDefinedFileFormat,
        if_not_exists: bool,
    ) -> Result<u64> {
        let file_format_api_provider = self.get_file_format_api_client(tenant)?;
        let add_file_format = file_format_api_provider.add_file_format(file_format_options);
        match add_file_format.await {
            Ok(res) => Ok(res),
            Err(e) => {
                if if_not_exists && e.code() == ErrorCode::FILE_FORMAT_ALREADY_EXISTS {
                    Ok(u64::MIN)
                } else {
                    Err(e)
                }
            }
        }
    }

    // Get one file_format from by tenant.
    #[async_backtrace::framed]
    pub async fn get_file_format(
        &self,
        tenant: &str,
        file_format_name: &str,
    ) -> Result<UserDefinedFileFormat> {
        let file_format_api_provider = self.get_file_format_api_client(tenant)?;
        let get_file_format =
            file_format_api_provider.get_file_format(file_format_name, MatchSeq::GE(0));
        Ok(get_file_format.await?.data)
    }

    // Get the tenant all file_format list.
    #[async_backtrace::framed]
    pub async fn get_file_formats(&self, tenant: &str) -> Result<Vec<UserDefinedFileFormat>> {
        let file_format_api_provider = self.get_file_format_api_client(tenant)?;
        let get_file_formats = file_format_api_provider.get_file_formats();

        match get_file_formats.await {
            Err(e) => Err(e.add_message_back(" (while get file_format)")),
            Ok(seq_file_formats_info) => Ok(seq_file_formats_info),
        }
    }

    // Drop a file_format by name.
    #[async_backtrace::framed]
    pub async fn drop_file_format(&self, tenant: &str, name: &str, if_exists: bool) -> Result<()> {
        let file_format_api_provider = self.get_file_format_api_client(tenant)?;
        let drop_file_format = file_format_api_provider.drop_file_format(name, MatchSeq::GE(1));
        match drop_file_format.await {
            Ok(res) => Ok(res),
            Err(e) => {
                if if_exists && e.code() == ErrorCode::UNKNOWN_FILE_FORMAT {
                    Ok(())
                } else {
                    Err(e.add_message_back(" (while drop file_format)"))
                }
            }
        }
    }
}
