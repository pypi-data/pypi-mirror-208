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

mod input_format_csv;
mod input_format_ndjson;
mod input_format_parquet;
mod input_format_tsv;
mod input_format_xml;

pub use input_format_csv::InputFormatCSV;
pub use input_format_ndjson::InputFormatNDJson;
pub use input_format_parquet::InputFormatParquet;
pub use input_format_tsv::InputFormatTSV;
pub use input_format_xml::InputFormatXML;
