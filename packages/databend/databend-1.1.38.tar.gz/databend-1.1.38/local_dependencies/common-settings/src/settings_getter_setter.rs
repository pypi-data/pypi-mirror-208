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

use common_ast::Dialect;
use common_exception::ErrorCode;
use common_exception::Result;
use common_meta_app::principal::UserSettingValue;

use crate::settings::Settings;
use crate::settings_default::DefaultSettings;
use crate::ChangeValue;
use crate::ScopeLevel;

impl Settings {
    // Get u64 value, we don't get from the metasrv.
    fn try_get_u64(&self, key: &str) -> Result<u64> {
        match self.changes.get(key) {
            Some(v) => v.value.as_u64(),
            None => DefaultSettings::try_get_u64(key),
        }
    }

    fn try_get_string(&self, key: &str) -> Result<String> {
        match self.changes.get(key) {
            Some(v) => v.value.as_string(),
            None => DefaultSettings::try_get_string(key),
        }
    }

    fn try_set_u64(&self, key: &str, val: u64) -> Result<()> {
        match DefaultSettings::instance()?.settings.get(key) {
            None => Err(ErrorCode::UnknownVariable(format!(
                "Unknown variable: {:?}",
                key
            ))),
            Some(default_val) => {
                if !matches!(&default_val.value, UserSettingValue::UInt64(_)) {
                    return Err(ErrorCode::BadArguments(format!(
                        "Set a integer({}) into {:?}.",
                        val, key
                    )));
                }

                self.changes.insert(key.to_string(), ChangeValue {
                    level: ScopeLevel::Session,
                    value: UserSettingValue::UInt64(val),
                });

                Ok(())
            }
        }
    }

    // Get max_block_size.
    pub fn get_max_block_size(&self) -> Result<u64> {
        self.try_get_u64("max_block_size")
    }

    // Get max_threads.
    pub fn get_max_threads(&self) -> Result<u64> {
        match self.try_get_u64("max_threads")? {
            0 => Ok(16),
            value => Ok(value),
        }
    }

    // Set max_threads.
    pub fn set_max_threads(&self, val: u64) -> Result<()> {
        self.try_set_u64("max_threads", val)
    }

    // Get storage_fetch_part_num.
    pub fn get_storage_fetch_part_num(&self) -> Result<u64> {
        match self.try_get_u64("storage_fetch_part_num")? {
            0 => Ok(16),
            value => Ok(value),
        }
    }

    // Set storage_fetch_part_num.
    pub fn set_storage_fetch_part_num(&self, val: u64) -> Result<()> {
        self.try_set_u64("storage_fetch_part_num", val)
    }

    // Get parquet_uncompressed_buffer_size.
    pub fn get_parquet_uncompressed_buffer_size(&self) -> Result<u64> {
        self.try_get_u64("parquet_uncompressed_buffer_size")
    }

    // Set parquet_uncompressed_buffer_size.
    pub fn set_parquet_uncompressed_buffer_size(&self, val: u64) -> Result<()> {
        self.try_set_u64("parquet_uncompressed_buffer_size", val)
    }

    pub fn get_max_memory_usage(&self) -> Result<u64> {
        self.try_get_u64("max_memory_usage")
    }

    pub fn set_max_memory_usage(&self, val: u64) -> Result<()> {
        self.try_set_u64("max_memory_usage", val)
    }

    pub fn set_retention_period(&self, hours: u64) -> Result<()> {
        self.try_set_u64("retention_period", hours)
    }

    pub fn get_retention_period(&self) -> Result<u64> {
        self.try_get_u64("retention_period")
    }

    pub fn get_max_storage_io_requests(&self) -> Result<u64> {
        self.try_get_u64("max_storage_io_requests")
    }

    pub fn set_max_storage_io_requests(&self, val: u64) -> Result<()> {
        if val > 0 {
            self.try_set_u64("max_storage_io_requests", val)
        } else {
            Err(ErrorCode::BadArguments("Value must be greater than 0"))
        }
    }

    pub fn get_storage_io_min_bytes_for_seek(&self) -> Result<u64> {
        self.try_get_u64("storage_io_min_bytes_for_seek")
    }

    pub fn set_storage_io_min_bytes_for_seek(&self, val: u64) -> Result<()> {
        self.try_set_u64("storage_io_min_bytes_for_seek", val)
    }

    pub fn get_storage_io_max_page_bytes_for_read(&self) -> Result<u64> {
        self.try_get_u64("storage_io_max_page_bytes_for_read")
    }

    pub fn set_storage_io_max_page_bytes_for_read(&self, val: u64) -> Result<()> {
        self.try_set_u64("storage_io_max_page_bytes_for_read", val)
    }

    // Get max_execute_time.
    pub fn get_max_execute_time(&self) -> Result<u64> {
        self.try_get_u64("max_execute_time")
    }

    // Set max_execute_time.
    pub fn set_max_execute_time(&self, val: u64) -> Result<()> {
        self.try_set_u64("max_execute_time", val)
    }

    // Get flight client timeout.
    pub fn get_flight_client_timeout(&self) -> Result<u64> {
        self.try_get_u64("flight_client_timeout")
    }

    // Get storage read buffer size.
    pub fn get_storage_read_buffer_size(&self) -> Result<u64> {
        self.try_get_u64("storage_read_buffer_size")
    }

    pub fn get_input_read_buffer_size(&self) -> Result<u64> {
        self.try_get_u64("input_read_buffer_size")
    }

    pub fn get_enable_bushy_join(&self) -> Result<u64> {
        self.try_get_u64("enable_bushy_join")
    }

    pub fn get_timezone(&self) -> Result<String> {
        self.try_get_string("timezone")
    }

    // Get group by two level threshold
    pub fn get_group_by_two_level_threshold(&self) -> Result<u64> {
        self.try_get_u64("group_by_two_level_threshold")
    }

    // Set group by two level threshold
    pub fn set_group_by_two_level_threshold(&self, val: u64) -> Result<()> {
        self.try_set_u64("group_by_two_level_threshold", val)
    }

    pub fn get_max_inlist_to_or(&self) -> Result<u64> {
        self.try_get_u64("max_inlist_to_or")
    }

    pub fn get_unquoted_ident_case_sensitive(&self) -> Result<bool> {
        Ok(self.try_get_u64("unquoted_ident_case_sensitive")? != 0)
    }

    pub fn set_unquoted_ident_case_sensitive(&self, val: bool) -> Result<()> {
        self.try_set_u64("unquoted_ident_case_sensitive", u64::from(val))
    }

    pub fn get_quoted_ident_case_sensitive(&self) -> Result<bool> {
        Ok(self.try_get_u64("quoted_ident_case_sensitive")? != 0)
    }

    pub fn set_quoted_ident_case_sensitive(&self, val: bool) -> Result<()> {
        self.try_set_u64("quoted_ident_case_sensitive", u64::from(val))
    }

    pub fn get_enable_distributed_eval_index(&self) -> Result<bool> {
        Ok(self.try_get_u64("enable_distributed_eval_index")? != 0)
    }

    pub fn get_max_result_rows(&self) -> Result<u64> {
        self.try_get_u64("max_result_rows")
    }

    pub fn set_enable_distributed_eval_index(&self, val: bool) -> Result<()> {
        self.try_set_u64("enable_distributed_eval_index", u64::from(val))
    }

    pub fn get_enable_dphyp(&self) -> Result<bool> {
        Ok(self.try_get_u64("enable_dphyp")? != 0)
    }

    pub fn set_enable_dphyp(&self, val: bool) -> Result<()> {
        self.try_set_u64("enable_dphyp", u64::from(val))
    }

    pub fn get_enable_cbo(&self) -> Result<bool> {
        Ok(self.try_get_u64("enable_cbo")? != 0)
    }

    pub fn set_enable_cbo(&self, val: bool) -> Result<()> {
        self.try_set_u64("enable_cbo", u64::from(val))
    }

    pub fn get_runtime_filter(&self) -> Result<bool> {
        Ok(self.try_get_u64("enable_runtime_filter")? != 0)
    }

    pub fn set_runtime_filter(&self, val: bool) -> Result<()> {
        self.try_set_u64("enable_runtime_filter", u64::from(val))
    }

    pub fn get_prefer_broadcast_join(&self) -> Result<bool> {
        Ok(self.try_get_u64("prefer_broadcast_join")? != 0)
    }

    pub fn set_prefer_broadcast_join(&self, val: bool) -> Result<()> {
        self.try_set_u64("join_distribution_type", u64::from(val))
    }

    pub fn get_sql_dialect(&self) -> Result<Dialect> {
        match self.try_get_string("sql_dialect")?.as_str() {
            "hive" => Ok(Dialect::Hive),
            "mysql" => Ok(Dialect::MySQL),
            _ => Ok(Dialect::PostgreSQL),
        }
    }

    pub fn get_collation(&self) -> Result<&str> {
        match self.try_get_string("collation")?.as_str() {
            "utf8" => Ok("utf8"),
            _ => Ok("binary"),
        }
    }

    pub fn get_enable_hive_parquet_predict_pushdown(&self) -> Result<u64> {
        self.try_get_u64("enable_hive_parquet_predict_pushdown")
    }

    pub fn get_hive_parquet_chunk_size(&self) -> Result<u64> {
        self.try_get_u64("hive_parquet_chunk_size")
    }

    pub fn set_load_file_metadata_expire_hours(&self, val: u64) -> Result<()> {
        self.try_set_u64("load_file_metadata_expire_hours", val)
    }

    pub fn get_load_file_metadata_expire_hours(&self) -> Result<u64> {
        self.try_get_u64("load_file_metadata_expire_hours")
    }

    pub fn get_sandbox_tenant(&self) -> Result<String> {
        self.try_get_string("sandbox_tenant")
    }

    pub fn get_hide_options_in_show_create_table(&self) -> Result<bool> {
        Ok(self.try_get_u64("hide_options_in_show_create_table")? != 0)
    }

    pub fn get_enable_query_result_cache(&self) -> Result<bool> {
        Ok(self.try_get_u64("enable_query_result_cache")? != 0)
    }

    pub fn get_query_result_cache_max_bytes(&self) -> Result<usize> {
        Ok(self.try_get_u64("query_result_cache_max_bytes")? as usize)
    }

    pub fn get_query_result_cache_ttl_secs(&self) -> Result<u64> {
        self.try_get_u64("query_result_cache_ttl_secs")
    }

    pub fn get_query_result_cache_allow_inconsistent(&self) -> Result<bool> {
        Ok(self.try_get_u64("query_result_cache_allow_inconsistent")? != 0)
    }

    pub fn get_spilling_bytes_threshold_per_proc(&self) -> Result<usize> {
        Ok(self.try_get_u64("spilling_bytes_threshold_per_proc")? as usize)
    }

    pub fn set_spilling_bytes_threshold_per_proc(&self, value: usize) -> Result<()> {
        self.try_set_u64("spilling_bytes_threshold_per_proc", value as u64)
    }

    pub fn get_group_by_shuffle_mode(&self) -> Result<String> {
        self.try_get_string("group_by_shuffle_mode")
    }

    pub fn get_efficiently_memory_group_by(&self) -> Result<bool> {
        Ok(self.try_get_u64("efficiently_memory_group_by")? == 1)
    }

    pub fn set_lazy_topn_threshold(&self, value: u64) -> Result<()> {
        self.try_set_u64("lazy_topn_threshold", value)
    }

    pub fn get_lazy_topn_threshold(&self) -> Result<u64> {
        self.try_get_u64("lazy_topn_threshold")
    }

    pub fn set_parquet_fast_read_bytes(&self, value: u64) -> Result<()> {
        self.try_set_u64("parquet_fast_read_bytes", value)
    }

    pub fn get_parquet_fast_read_bytes(&self) -> Result<u64> {
        self.try_get_u64("parquet_fast_read_bytes")
    }

    pub fn get_enterprise_license(&self) -> Result<String> {
        self.try_get_string("enterprise_license")
    }

    pub fn set_enterprise_license(&self, val: String) -> Result<()> {
        self.set_setting("enterprise_license".to_string(), val)
    }
}
