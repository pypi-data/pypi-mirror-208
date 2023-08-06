// Copyright 2021 Datafuse Labs
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

use common_base::base::tokio;
use databend_query::api::http::v1::config::config_handler;
use databend_query::test_kits::TestGlobalServices;
use poem::get;
use poem::http::Method;
use poem::http::StatusCode;
use poem::http::Uri;
use poem::Endpoint;
use poem::Request;
use poem::Route;
use pretty_assertions::assert_eq; // for `app.oneshot()`

#[tokio::test(flavor = "multi_thread")]
async fn test_config() -> common_exception::Result<()> {
    let _guard =
        TestGlobalServices::setup(databend_query::test_kits::ConfigBuilder::create().build())
            .await?;
    let cluster_router = Route::new().at("/v1/config", get(config_handler));

    let response = cluster_router
        .call(
            Request::builder()
                .uri(Uri::from_static("/v1/config"))
                .method(Method::GET)
                .finish(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
    Ok(())
}
