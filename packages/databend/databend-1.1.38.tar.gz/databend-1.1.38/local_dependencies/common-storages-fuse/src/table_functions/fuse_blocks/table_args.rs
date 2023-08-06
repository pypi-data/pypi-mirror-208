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

use crate::table_functions::string_value;
use crate::table_functions::TableArgs;

pub(crate) fn parse_func_table_args(
    table_args: &TableArgs,
) -> Result<(String, String, Option<String>)> {
    let args = table_args.expect_all_positioned("fuse_blocks", None)?;
    match args.len() {
        3 => {
            let db = string_value(&args[0])?;
            let tbl = string_value(&args[1])?;
            let snapshot_id = string_value(&args[2])?;
            Ok((db, tbl, Some(snapshot_id)))
        }
        2 => {
            let db = string_value(&args[0])?;
            let tbl = string_value(&args[1])?;
            Ok((db, tbl, None))
        }
        _ => Err(ErrorCode::BadArguments(format!(
            "expecting <database>, <table_name> and <snapshot_id> (as string literals), but got {:?}",
            args
        ))),
    }
}
