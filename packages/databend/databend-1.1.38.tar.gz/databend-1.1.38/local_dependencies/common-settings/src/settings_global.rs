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
use common_meta_app::principal::UserSettingValue;
use common_meta_types::MatchSeq;
use common_users::UserApiProvider;

use crate::settings::ChangeValue;
use crate::settings::Settings;
use crate::settings_default::DefaultSettings;
use crate::ScopeLevel;

impl Settings {
    #[async_backtrace::framed]
    pub async fn load_settings(
        user_api: Arc<UserApiProvider>,
        tenant: String,
    ) -> Result<Vec<UserSetting>> {
        user_api
            .get_setting_api_client(&tenant)?
            .get_settings()
            .await
    }

    #[async_backtrace::framed]
    pub async fn try_drop_global_setting(&self, key: &str) -> Result<()> {
        self.changes.remove(key);

        if !DefaultSettings::has_setting(key)? {
            return Err(ErrorCode::UnknownVariable(format!(
                "Unknown variable: {:?}",
                key
            )));
        }

        UserApiProvider::instance()
            .get_setting_api_client(&self.tenant)?
            .drop_setting(key, MatchSeq::GE(1))
            .await
    }

    #[async_backtrace::framed]
    pub async fn set_global_setting(&self, k: String, v: String) -> Result<()> {
        if let (key, Some(value)) = DefaultSettings::convert_value(k.clone(), v)? {
            self.changes.insert(key.clone(), ChangeValue {
                value: value.clone(),
                level: ScopeLevel::Global,
            });

            UserApiProvider::instance()
                .set_setting(&self.tenant, UserSetting { name: key, value })
                .await?;

            return Ok(());
        }

        Err(ErrorCode::UnknownVariable(format!(
            "Unknown variable: {:?}",
            k
        )))
    }

    #[async_backtrace::framed]
    pub async fn load_global_changes(&self) -> Result<()> {
        let default_settings = DefaultSettings::instance()?;

        let api = UserApiProvider::instance();
        let global_settings = Settings::load_settings(api, self.tenant.clone()).await?;

        for global_setting in global_settings {
            let name = global_setting.name;
            let val = global_setting.value.as_string()?;

            self.changes
                .insert(name.clone(), match default_settings.settings.get(&name) {
                    None => {
                        // the settings may be deprecated
                        tracing::warn!("Ignore deprecated global setting {} = {}", name, val);
                        continue;
                    }
                    Some(default_setting_value) => match &default_setting_value.value {
                        UserSettingValue::UInt64(_) => ChangeValue {
                            level: ScopeLevel::Global,
                            value: UserSettingValue::UInt64(val.parse::<u64>()?),
                        },
                        UserSettingValue::String(_) => ChangeValue {
                            level: ScopeLevel::Global,
                            value: UserSettingValue::String(val.clone()),
                        },
                    },
                });
        }

        Ok(())
    }
}
