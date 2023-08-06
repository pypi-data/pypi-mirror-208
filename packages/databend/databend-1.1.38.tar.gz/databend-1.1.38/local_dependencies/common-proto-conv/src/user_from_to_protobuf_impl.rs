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

//! This mod is the key point about compatibility.
//! Everytime update anything in this file, update the `VER` and let the tests pass.

use std::collections::BTreeMap;
use std::collections::HashSet;

use common_meta_app as mt;
use common_protos::pb;
use enumflags2::BitFlags;
use num::FromPrimitive;

use crate::reader_check_msg;
use crate::FromToProto;
use crate::Incompatible;
use crate::MIN_READER_VER;
use crate::VER;

impl FromToProto for mt::principal::AuthInfo {
    type PB = pb::AuthInfo;
    fn get_pb_ver(p: &Self::PB) -> u64 {
        p.ver
    }
    fn from_pb(p: pb::AuthInfo) -> Result<Self, Incompatible>
    where Self: Sized {
        reader_check_msg(p.ver, p.min_reader_ver)?;

        match p.info {
            Some(pb::auth_info::Info::None(pb::auth_info::None {})) => {
                Ok(mt::principal::AuthInfo::None)
            }
            Some(pb::auth_info::Info::Jwt(pb::auth_info::Jwt {})) => {
                Ok(mt::principal::AuthInfo::JWT)
            }
            Some(pb::auth_info::Info::Password(pb::auth_info::Password {
                hash_value,
                hash_method,
            })) => Ok(mt::principal::AuthInfo::Password {
                hash_value,
                hash_method: FromPrimitive::from_i32(hash_method).ok_or_else(|| Incompatible {
                    reason: format!("invalid PasswordHashMethod: {}", hash_method),
                })?,
            }),
            None => Err(Incompatible {
                reason: "AuthInfo cannot be None".to_string(),
            }),
        }
    }

    fn to_pb(&self) -> Result<pb::AuthInfo, Incompatible> {
        let info = match self {
            mt::principal::AuthInfo::None => {
                Some(pb::auth_info::Info::None(pb::auth_info::None {}))
            }
            mt::principal::AuthInfo::JWT => Some(pb::auth_info::Info::Jwt(pb::auth_info::Jwt {})),
            mt::principal::AuthInfo::Password {
                hash_value,
                hash_method,
            } => Some(pb::auth_info::Info::Password(pb::auth_info::Password {
                hash_value: hash_value.clone(),
                hash_method: *hash_method as i32,
            })),
        };
        Ok(pb::AuthInfo {
            ver: VER,
            min_reader_ver: MIN_READER_VER,
            info,
        })
    }
}

impl FromToProto for mt::principal::UserOption {
    type PB = pb::UserOption;
    fn get_pb_ver(p: &Self::PB) -> u64 {
        p.ver
    }
    fn from_pb(p: pb::UserOption) -> Result<Self, Incompatible>
    where Self: Sized {
        reader_check_msg(p.ver, p.min_reader_ver)?;

        // ignore unknown flags
        let flags = BitFlags::<mt::principal::UserOptionFlag, u64>::from_bits_truncate(p.flags);

        Ok(mt::principal::UserOption::default()
            .with_flags(flags)
            .with_default_role(p.default_role))
    }

    fn to_pb(&self) -> Result<pb::UserOption, Incompatible> {
        Ok(pb::UserOption {
            ver: VER,
            min_reader_ver: MIN_READER_VER,
            flags: self.flags().bits(),
            default_role: self.default_role().cloned(),
        })
    }
}

impl FromToProto for mt::principal::UserQuota {
    type PB = pb::UserQuota;
    fn get_pb_ver(p: &Self::PB) -> u64 {
        p.ver
    }
    fn from_pb(p: pb::UserQuota) -> Result<Self, Incompatible>
    where Self: Sized {
        reader_check_msg(p.ver, p.min_reader_ver)?;

        Ok(Self {
            max_cpu: p.max_cpu,
            max_memory_in_bytes: p.max_memory_in_bytes,
            max_storage_in_bytes: p.max_storage_in_bytes,
        })
    }

    fn to_pb(&self) -> Result<pb::UserQuota, Incompatible> {
        Ok(pb::UserQuota {
            ver: VER,
            min_reader_ver: MIN_READER_VER,
            max_cpu: self.max_cpu,
            max_memory_in_bytes: self.max_memory_in_bytes,
            max_storage_in_bytes: self.max_storage_in_bytes,
        })
    }
}

impl FromToProto for mt::principal::GrantObject {
    type PB = pb::GrantObject;
    fn get_pb_ver(p: &Self::PB) -> u64 {
        p.ver
    }
    fn from_pb(p: pb::GrantObject) -> Result<Self, Incompatible>
    where Self: Sized {
        reader_check_msg(p.ver, p.min_reader_ver)?;

        match p.object {
            Some(pb::grant_object::Object::Global(pb::grant_object::GrantGlobalObject {})) => {
                Ok(mt::principal::GrantObject::Global)
            }
            Some(pb::grant_object::Object::Database(pb::grant_object::GrantDatabaseObject {
                catalog,
                db,
            })) => Ok(mt::principal::GrantObject::Database(catalog, db)),
            Some(pb::grant_object::Object::Table(pb::grant_object::GrantTableObject {
                catalog,
                db,
                table,
            })) => Ok(mt::principal::GrantObject::Table(catalog, db, table)),
            _ => Err(Incompatible {
                reason: "GrantObject cannot be None".to_string(),
            }),
        }
    }

    fn to_pb(&self) -> Result<pb::GrantObject, Incompatible> {
        let object = match self {
            mt::principal::GrantObject::Global => Some(pb::grant_object::Object::Global(
                pb::grant_object::GrantGlobalObject {},
            )),
            mt::principal::GrantObject::Database(catalog, db) => Some(
                pb::grant_object::Object::Database(pb::grant_object::GrantDatabaseObject {
                    catalog: catalog.clone(),
                    db: db.clone(),
                }),
            ),
            mt::principal::GrantObject::Table(catalog, db, table) => Some(
                pb::grant_object::Object::Table(pb::grant_object::GrantTableObject {
                    catalog: catalog.clone(),
                    db: db.clone(),
                    table: table.clone(),
                }),
            ),
        };
        Ok(pb::GrantObject {
            ver: VER,
            min_reader_ver: MIN_READER_VER,
            object,
        })
    }
}

impl FromToProto for mt::principal::GrantEntry {
    type PB = pb::GrantEntry;
    fn get_pb_ver(p: &Self::PB) -> u64 {
        p.ver
    }
    fn from_pb(p: pb::GrantEntry) -> Result<Self, Incompatible>
    where Self: Sized {
        reader_check_msg(p.ver, p.min_reader_ver)?;

        let privileges = BitFlags::<mt::principal::UserPrivilegeType, u64>::from_bits(p.privileges);
        match privileges {
            Ok(privileges) => Ok(mt::principal::GrantEntry::new(
                mt::principal::GrantObject::from_pb(p.object.ok_or_else(|| Incompatible {
                    reason: "GrantEntry.object can not be None".to_string(),
                })?)?,
                privileges,
            )),
            Err(e) => Err(Incompatible {
                reason: format!("UserPrivilegeType error: {}", e),
            }),
        }
    }

    fn to_pb(&self) -> Result<pb::GrantEntry, Incompatible> {
        Ok(pb::GrantEntry {
            ver: VER,
            min_reader_ver: MIN_READER_VER,
            object: Some(self.object().to_pb()?),
            privileges: self.privileges().bits(),
        })
    }
}

impl FromToProto for mt::principal::UserGrantSet {
    type PB = pb::UserGrantSet;
    fn get_pb_ver(p: &Self::PB) -> u64 {
        p.ver
    }
    fn from_pb(p: pb::UserGrantSet) -> Result<Self, Incompatible>
    where Self: Sized {
        reader_check_msg(p.ver, p.min_reader_ver)?;

        let mut entries = Vec::new();
        for entry in p.entries.iter() {
            entries.push(mt::principal::GrantEntry::from_pb(entry.clone())?);
        }
        let mut roles = HashSet::new();
        for role in p.roles.iter() {
            roles.insert(role.0.clone());
        }
        Ok(mt::principal::UserGrantSet::new(entries, roles))
    }

    fn to_pb(&self) -> Result<pb::UserGrantSet, Incompatible> {
        let mut entries = Vec::new();
        for entry in self.entries().iter() {
            entries.push(entry.to_pb()?);
        }

        let mut roles = BTreeMap::new();
        for role in self.roles().iter() {
            roles.insert(role.clone(), true);
        }

        Ok(pb::UserGrantSet {
            ver: VER,
            min_reader_ver: MIN_READER_VER,
            entries,
            roles,
        })
    }
}

impl FromToProto for mt::principal::UserInfo {
    type PB = pb::UserInfo;
    fn get_pb_ver(p: &Self::PB) -> u64 {
        p.ver
    }
    fn from_pb(p: pb::UserInfo) -> Result<Self, Incompatible>
    where Self: Sized {
        reader_check_msg(p.ver, p.min_reader_ver)?;

        Ok(mt::principal::UserInfo {
            name: p.name.clone(),
            hostname: p.hostname.clone(),
            auth_info: mt::principal::AuthInfo::from_pb(p.auth_info.ok_or_else(|| {
                Incompatible {
                    reason: "UserInfo.auth_info cannot be None".to_string(),
                }
            })?)?,
            grants: mt::principal::UserGrantSet::from_pb(p.grants.ok_or_else(|| {
                Incompatible {
                    reason: "UserInfo.grants cannot be None".to_string(),
                }
            })?)?,
            quota: mt::principal::UserQuota::from_pb(p.quota.ok_or_else(|| Incompatible {
                reason: "UserInfo.quota cannot be None".to_string(),
            })?)?,
            option: mt::principal::UserOption::from_pb(p.option.ok_or_else(|| Incompatible {
                reason: "UserInfo.option cannot be None".to_string(),
            })?)?,
        })
    }

    fn to_pb(&self) -> Result<pb::UserInfo, Incompatible> {
        Ok(pb::UserInfo {
            ver: VER,
            min_reader_ver: MIN_READER_VER,
            name: self.name.clone(),
            hostname: self.hostname.clone(),
            auth_info: Some(mt::principal::AuthInfo::to_pb(&self.auth_info)?),
            grants: Some(mt::principal::UserGrantSet::to_pb(&self.grants)?),
            quota: Some(mt::principal::UserQuota::to_pb(&self.quota)?),
            option: Some(mt::principal::UserOption::to_pb(&self.option)?),
        })
    }
}

impl FromToProto for mt::principal::UserIdentity {
    type PB = pb::UserIdentity;
    fn get_pb_ver(p: &Self::PB) -> u64 {
        p.ver
    }
    fn from_pb(p: pb::UserIdentity) -> Result<Self, Incompatible>
    where Self: Sized {
        reader_check_msg(p.ver, p.min_reader_ver)?;

        Ok(mt::principal::UserIdentity {
            username: p.username.clone(),
            hostname: p.hostname,
        })
    }

    fn to_pb(&self) -> Result<pb::UserIdentity, Incompatible> {
        Ok(pb::UserIdentity {
            ver: VER,
            min_reader_ver: MIN_READER_VER,
            username: self.username.clone(),
            hostname: self.hostname.clone(),
        })
    }
}
