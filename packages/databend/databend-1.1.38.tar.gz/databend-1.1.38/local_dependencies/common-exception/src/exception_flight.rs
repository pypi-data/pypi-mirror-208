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

use common_arrow::arrow_format::flight::data::FlightData;

use crate::exception::ErrorCodeBacktrace;
use crate::ErrorCode;
use crate::Result;
use crate::SerializedError;

impl From<ErrorCode> for FlightData {
    fn from(error: ErrorCode) -> Self {
        let serialized_error = serde_json::to_vec::<SerializedError>(&SerializedError {
            code: error.code(),
            message: error.message(),
            span: error.span(),
            backtrace: error.backtrace_str(),
        })
        .unwrap();

        FlightData {
            data_body: serialized_error,
            app_metadata: vec![0x02],
            data_header: error.code().to_be_bytes().to_vec(),
            flight_descriptor: None,
        }
    }
}

impl TryFrom<FlightData> for ErrorCode {
    type Error = ErrorCode;

    fn try_from(flight_data: FlightData) -> Result<Self> {
        match serde_json::from_slice::<SerializedError>(&flight_data.data_body) {
            Err(error) => Ok(ErrorCode::from(error)),
            Ok(serialized_error) => match serialized_error.backtrace.len() {
                0 => Ok(ErrorCode::create(
                    serialized_error.code,
                    serialized_error.message,
                    None,
                    None,
                )
                .set_span(serialized_error.span)),
                _ => Ok(ErrorCode::create(
                    serialized_error.code,
                    serialized_error.message,
                    None,
                    Some(ErrorCodeBacktrace::Serialized(Arc::new(
                        serialized_error.backtrace,
                    ))),
                )
                .set_span(serialized_error.span)),
            },
        }
    }
}
