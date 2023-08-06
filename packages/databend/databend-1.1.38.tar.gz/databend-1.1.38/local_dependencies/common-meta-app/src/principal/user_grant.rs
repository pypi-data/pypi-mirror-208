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

use std::collections::HashSet;
use std::fmt;
use std::ops;

use enumflags2::BitFlags;

use crate::principal::UserPrivilegeSet;
use crate::principal::UserPrivilegeType;

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug, Eq, PartialEq)]
pub enum GrantObject {
    Global,
    Database(String, String),
    Table(String, String, String),
}

impl GrantObject {
    /// Comparing the grant objects, the Database object contains all the Table objects inside it.
    /// Global object contains all the Database objects.
    pub fn contains(&self, object: &GrantObject) -> bool {
        match (self, object) {
            (GrantObject::Global, _) => true,
            (GrantObject::Database(_, _), GrantObject::Global) => false,
            (GrantObject::Database(lcat, ldb), GrantObject::Database(rcat, rdb)) => {
                lcat == rcat && ldb == rdb
            }
            (GrantObject::Database(lcat, ldb), GrantObject::Table(rcat, rdb, _)) => {
                lcat == rcat && ldb == rdb
            }
            (
                GrantObject::Table(lcat, lhs_db, lhs_table),
                GrantObject::Table(rcat, rhs_db, rhs_table),
            ) => lcat == rcat && (lhs_db == rhs_db) && (lhs_table == rhs_table),
            (GrantObject::Table(_, _, _), _) => false,
        }
    }

    /// Global, database and table has different available privileges
    pub fn available_privileges(&self) -> UserPrivilegeSet {
        match self {
            GrantObject::Global => UserPrivilegeSet::available_privileges_on_global(),
            GrantObject::Database(_, _) => UserPrivilegeSet::available_privileges_on_database(),
            GrantObject::Table(_, _, _) => UserPrivilegeSet::available_privileges_on_table(),
        }
    }
}

impl fmt::Display for GrantObject {
    fn fmt(&self, f: &mut fmt::Formatter) -> std::result::Result<(), fmt::Error> {
        match self {
            GrantObject::Global => write!(f, "*.*"),
            GrantObject::Database(ref cat, ref db) => write!(f, "'{}'.'{}'.*", cat, db),
            GrantObject::Table(ref cat, ref db, ref table) => {
                write!(f, "'{}'.'{}'.'{}'", cat, db, table)
            }
        }
    }
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug, Eq, PartialEq)]
pub struct GrantEntry {
    object: GrantObject,
    privileges: BitFlags<UserPrivilegeType>,
}

impl GrantEntry {
    pub fn new(object: GrantObject, privileges: BitFlags<UserPrivilegeType>) -> Self {
        Self { object, privileges }
    }

    pub fn object(&self) -> &GrantObject {
        &self.object
    }

    pub fn privileges(&self) -> &BitFlags<UserPrivilegeType> {
        &self.privileges
    }

    pub fn verify_privilege(
        &self,
        object: &GrantObject,
        privileges: Vec<UserPrivilegeType>,
    ) -> bool {
        // the verified object should be smaller than the object inside my grant entry.
        if !self.object.contains(object) {
            return false;
        }

        let mut priv_set = UserPrivilegeSet::empty();
        for privilege in privileges {
            priv_set.set_privilege(privilege)
        }
        self.privileges.contains(BitFlags::from(priv_set))
    }

    pub fn matches_entry(&self, object: &GrantObject) -> bool {
        &self.object == object
    }

    fn has_all_available_privileges(&self) -> bool {
        let all_available_privileges = self.object.available_privileges();
        self.privileges
            .contains(BitFlags::from(all_available_privileges))
    }
}

impl fmt::Display for GrantEntry {
    fn fmt(&self, f: &mut fmt::Formatter) -> std::result::Result<(), fmt::Error> {
        let privileges: UserPrivilegeSet = self.privileges.into();
        let privileges_str = if self.has_all_available_privileges() {
            "ALL".to_string()
        } else {
            privileges.to_string()
        };
        write!(f, "GRANT {} ON {}", &privileges_str, self.object)
    }
}

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug, Eq, PartialEq, Default)]
pub struct UserGrantSet {
    entries: Vec<GrantEntry>,
    roles: HashSet<String>,
}

impl UserGrantSet {
    pub fn new(entries: Vec<GrantEntry>, roles: HashSet<String>) -> Self {
        UserGrantSet { entries, roles }
    }

    pub fn empty() -> Self {
        Self {
            entries: vec![],
            roles: HashSet::new(),
        }
    }

    pub fn entries(&self) -> Vec<GrantEntry> {
        self.entries.clone()
    }

    pub fn roles(&self) -> Vec<String> {
        self.roles.iter().cloned().collect::<Vec<_>>()
    }

    pub fn grant_role(&mut self, role: String) {
        self.roles.insert(role);
    }

    pub fn revoke_role(&mut self, role: &String) {
        self.roles.remove(role);
    }

    pub fn verify_privilege(
        &self,
        object: &GrantObject,
        privilege: Vec<UserPrivilegeType>,
    ) -> bool {
        self.entries
            .iter()
            .any(|e| e.verify_privilege(object, privilege.clone()))
    }

    pub fn grant_privileges(&mut self, object: &GrantObject, privileges: UserPrivilegeSet) {
        let privileges: BitFlags<UserPrivilegeType> = privileges.into();
        let mut new_entries: Vec<GrantEntry> = vec![];
        let mut changed = false;

        for entry in self.entries.iter() {
            let mut entry = entry.clone();
            if entry.matches_entry(object) {
                entry.privileges |= privileges;
                changed = true;
            }
            new_entries.push(entry);
        }

        if !changed {
            new_entries.push(GrantEntry::new(object.clone(), privileges))
        }

        self.entries = new_entries;
    }

    pub fn revoke_privileges(&mut self, object: &GrantObject, privileges: UserPrivilegeSet) {
        let privileges: BitFlags<UserPrivilegeType> = privileges.into();
        let new_entries = self
            .entries
            .iter()
            .map(|e| {
                if e.matches_entry(object) {
                    let mut e = e.clone();
                    e.privileges ^= privileges;
                    e
                } else {
                    e.clone()
                }
            })
            .filter(|e| e.privileges != BitFlags::empty())
            .collect::<Vec<_>>();
        self.entries = new_entries;
    }
}

impl ops::BitOrAssign for UserGrantSet {
    fn bitor_assign(&mut self, other: Self) {
        for entry in other.entries() {
            self.grant_privileges(&entry.object, entry.privileges.into());
        }
        for role in other.roles() {
            self.grant_role(role);
        }
    }
}

impl ops::BitOr for UserGrantSet {
    type Output = Self;
    fn bitor(self, other: Self) -> Self {
        let mut grants = self;
        grants |= other;
        grants
    }
}

impl fmt::Display for UserGrantSet {
    fn fmt(&self, f: &mut fmt::Formatter) -> std::result::Result<(), fmt::Error> {
        for entry in self.entries.iter() {
            write!(f, "{}, ", entry)?;
        }
        write!(f, "ROLES: {:?}", self.roles())
    }
}
