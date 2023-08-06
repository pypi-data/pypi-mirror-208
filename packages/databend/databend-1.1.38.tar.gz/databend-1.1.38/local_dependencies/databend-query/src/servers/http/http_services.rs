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

use std::net::SocketAddr;
use std::path::Path;
use std::time::Duration;

use common_config::GlobalConfig;
use common_config::InnerConfig;
use common_exception::ErrorCode;
use common_http::HttpError;
use common_http::HttpShutdownHandler;
use common_meta_types::anyerror::AnyError;
use poem::get;
use poem::listener::RustlsCertificate;
use poem::listener::RustlsConfig;
use poem::middleware::CatchPanic;
use poem::middleware::NormalizePath;
use poem::middleware::TrailingSlash;
use poem::put;
use poem::Endpoint;
use poem::EndpointExt;
use poem::Route;
use tracing::info;

use super::v1::upload_to_stage;
use crate::auth::AuthMgr;
use crate::servers::http::middleware::HTTPSessionMiddleware;
use crate::servers::http::v1::clickhouse_router;
use crate::servers::http::v1::query_route;
use crate::servers::http::v1::streaming_load;
use crate::servers::Server;

#[derive(Copy, Clone)]
pub enum HttpHandlerKind {
    Query,
    Clickhouse,
}

impl HttpHandlerKind {
    pub fn usage(&self, sock: SocketAddr) -> String {
        match self {
            HttpHandlerKind::Query => {
                format!(
                    r#" curl -u root: --request POST '{:?}/v1/query/' --header 'Content-Type: application/json' --data-raw '{{"sql": "SELECT avg(number) FROM numbers(100000000)"}}'
"#,
                    sock,
                )
            }
            HttpHandlerKind::Clickhouse => {
                let json = r#"{"foo": "bar"}"#;
                format!(
                    r#" echo 'create table test(foo string)' | curl -u root: '{:?}' --data-binary  @-
echo '{}' | curl -u root: '{:?}/?query=INSERT%20INTO%20test%20FORMAT%20JSONEachRow' --data-binary @-"#,
                    sock, json, sock,
                )
            }
        }
    }
}

pub struct HttpHandler {
    shutdown_handler: HttpShutdownHandler,
    kind: HttpHandlerKind,
}

impl HttpHandler {
    pub fn create(kind: HttpHandlerKind) -> Box<dyn Server> {
        Box::new(HttpHandler {
            kind,
            shutdown_handler: HttpShutdownHandler::create("http handler".to_string()),
        })
    }

    fn wrap_auth(&self, ep: Route) -> impl Endpoint {
        let auth_manager = AuthMgr::instance();
        let session_middleware = HTTPSessionMiddleware::create(self.kind, auth_manager);
        ep.with(session_middleware).boxed()
    }

    #[async_backtrace::framed]
    async fn build_router(&self, sock: SocketAddr) -> impl Endpoint {
        let ep_v1 = Route::new()
            .nest("/query", query_route())
            .at("/streaming_load", put(streaming_load))
            .at("/upload_to_stage", put(upload_to_stage));
        let ep_v1 = self.wrap_auth(ep_v1);

        let ep_clickhouse = Route::new().nest("/", clickhouse_router());
        let ep_clickhouse = self.wrap_auth(ep_clickhouse);

        let ep_usage = Route::new().at(
            "/",
            get(poem::endpoint::make_sync(move |_| {
                HttpHandlerKind::Query.usage(sock)
            })),
        );
        let ep_health = Route::new().at("/", get(poem::endpoint::make_sync(move |_| "ok")));

        let ep = match self.kind {
            HttpHandlerKind::Query => Route::new()
                .at("/", ep_usage)
                .nest("/health", ep_health)
                .nest("/v1", ep_v1)
                .nest("/clickhouse", ep_clickhouse),
            HttpHandlerKind::Clickhouse => Route::new()
                .nest("/", ep_clickhouse)
                .nest("/health", ep_health),
        };
        ep.with(NormalizePath::new(TrailingSlash::Trim))
            .with(CatchPanic::new())
            .boxed()
    }

    fn build_tls(config: &InnerConfig) -> Result<RustlsConfig, std::io::Error> {
        let certificate = RustlsCertificate::new()
            .cert(std::fs::read(
                config.query.http_handler_tls_server_cert.as_str(),
            )?)
            .key(std::fs::read(
                config.query.http_handler_tls_server_key.as_str(),
            )?);
        let mut cfg = RustlsConfig::new().fallback(certificate);
        if Path::new(&config.query.http_handler_tls_server_root_ca_cert).exists() {
            cfg = cfg.client_auth_required(std::fs::read(
                config.query.http_handler_tls_server_root_ca_cert.as_str(),
            )?);
        }
        Ok(cfg)
    }

    #[async_backtrace::framed]
    async fn start_with_tls(&mut self, listening: SocketAddr) -> Result<SocketAddr, HttpError> {
        info!("Http Handler TLS enabled");

        let config = GlobalConfig::instance();

        let tls_config = Self::build_tls(config.as_ref())
            .map_err(|e: std::io::Error| HttpError::TlsConfigError(AnyError::new(&e)))?;

        let router = self.build_router(listening).await;
        self.shutdown_handler
            .start_service(
                listening,
                Some(tls_config),
                router,
                Some(Duration::from_millis(1000)),
            )
            .await
    }

    #[async_backtrace::framed]
    async fn start_without_tls(&mut self, listening: SocketAddr) -> Result<SocketAddr, HttpError> {
        let router = self.build_router(listening).await;
        self.shutdown_handler
            .start_service(listening, None, router, Some(Duration::from_millis(1000)))
            .await
    }
}

#[async_trait::async_trait]
impl Server for HttpHandler {
    #[async_backtrace::framed]
    async fn shutdown(&mut self, graceful: bool) {
        self.shutdown_handler.shutdown(graceful).await;
    }

    #[async_backtrace::framed]
    async fn start(&mut self, listening: SocketAddr) -> Result<SocketAddr, ErrorCode> {
        let config = GlobalConfig::instance();

        let res = match config.query.http_handler_tls_server_key.is_empty()
            || config.query.http_handler_tls_server_cert.is_empty()
        {
            true => self.start_without_tls(listening).await,
            false => self.start_with_tls(listening).await,
        };

        res.map_err(|e: HttpError| match e {
            HttpError::BadAddressFormat(any_err) => {
                ErrorCode::BadAddressFormat(any_err.to_string())
            }
            le @ HttpError::ListenError { .. } => ErrorCode::CannotListenerPort(le.to_string()),
            HttpError::TlsConfigError(any_err) => {
                ErrorCode::TLSConfigurationFailure(any_err.to_string())
            }
        })
    }
}
