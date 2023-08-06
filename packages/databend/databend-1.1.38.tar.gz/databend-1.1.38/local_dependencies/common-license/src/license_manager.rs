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

use common_base::base::GlobalInstance;
use common_exception::ErrorCode;
use common_exception::Result;
use common_settings::Settings;
use jwt_simple::claims::JWTClaims;

use crate::license::LicenseInfo;

pub trait LicenseManager {
    fn init() -> Result<()>
    where Self: Sized;
    fn instance() -> Arc<Box<dyn LicenseManager>>
    where Self: Sized;

    /// Check whether enterprise feature is available given context
    /// This function returns `LicenseKeyInvalid` error if enterprise license key is not valid or expired.
    fn check_enterprise_enabled(
        &self,
        settings: &Arc<Settings>,
        tenant: String,
        feature: String,
    ) -> Result<()>;

    /// Encodes a raw license string as a JWT using the constant public key.
    ///
    /// This function takes a raw license string and a secret key,
    /// The function returns a `jwt_simple::Claim` object that represents the
    /// decoded contents of the JWT  with custom fields `LicenseInfo`
    ///
    /// # Arguments
    ///
    /// * `raw` - The raw license string to be encoded.
    ///
    /// # Returns
    ///
    /// A `jwt_simple::Claim` object representing the decoded contents of the JWT.
    ///
    /// # Errors
    ///
    /// This function may return `LicenseKeyParseError` error if the encoding or decoding of the JWT fails.
    /// ```
    fn parse_license(&self, raw: &str) -> Result<JWTClaims<LicenseInfo>>;
}

pub struct LicenseManagerWrapper {
    pub manager: Box<dyn LicenseManager>,
}
unsafe impl Send for LicenseManagerWrapper {}
unsafe impl Sync for LicenseManagerWrapper {}

pub struct OssLicenseManager {}

impl LicenseManager for OssLicenseManager {
    fn init() -> Result<()> {
        let rm = OssLicenseManager {};
        let wrapper = LicenseManagerWrapper {
            manager: Box::new(rm),
        };
        GlobalInstance::set(Arc::new(wrapper));
        Ok(())
    }

    fn instance() -> Arc<Box<dyn LicenseManager>> {
        GlobalInstance::get()
    }

    fn check_enterprise_enabled(
        &self,
        _settings: &Arc<Settings>,
        _tenant: String,
        _feature: String,
    ) -> Result<()> {
        Err(ErrorCode::LicenseKeyInvalid(
            "Need Commercial License".to_string(),
        ))
    }

    fn parse_license(&self, _raw: &str) -> Result<JWTClaims<LicenseInfo>> {
        Err(ErrorCode::LicenceDenied(
            "Need Commercial License".to_string(),
        ))
    }
}

pub fn get_license_manager() -> Arc<LicenseManagerWrapper> {
    GlobalInstance::get()
}
