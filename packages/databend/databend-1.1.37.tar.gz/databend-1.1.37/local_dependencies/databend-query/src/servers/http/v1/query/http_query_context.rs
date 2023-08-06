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

use poem::FromRequest;
use poem::Request;
use poem::RequestBody;
use poem::Result as PoemResult;

use crate::sessions::Session;
use crate::sessions::SessionType;

pub struct HttpQueryContext {
    session: Arc<Session>,
}

impl HttpQueryContext {
    pub fn new(session: Arc<Session>) -> Self {
        HttpQueryContext { session }
    }

    pub fn get_session(&self, session_type: SessionType) -> Arc<Session> {
        self.session.set_type(session_type);
        self.session.clone()
    }
}

#[async_trait::async_trait]
impl<'a> FromRequest<'a> for &'a HttpQueryContext {
    #[async_backtrace::framed]
    async fn from_request(req: &'a Request, _body: &mut RequestBody) -> PoemResult<Self> {
        Ok(req.extensions().get::<HttpQueryContext>().expect(
            "To use the `HttpQueryContext` extractor, the `HTTPSessionMiddleware` is required",
        ))
    }
}
