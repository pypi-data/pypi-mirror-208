// Copyright 2023 Datafuse Labs.
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

// The servers module used for external communication with user, such as MySQL wired protocol, etc.

use std::fs;
use std::io::Write;

use arrow_cast::pretty::pretty_format_batches;
use arrow_flight::flight_service_server::FlightServiceServer;
use arrow_flight::sql::client::FlightSqlServiceClient;
use arrow_flight::utils::flight_data_to_batches;
use arrow_flight::FlightData;
use arrow_schema::ArrowError;
use common_base::base::tokio;
use common_config::InnerConfig;
use common_exception::Result;
use common_meta_app::principal::AuthInfo;
use common_meta_app::principal::PasswordHashMethod;
use databend_query::servers::flight_sql::flight_sql_service::FlightSqlServiceImpl;
use databend_query::test_kits::ConfigBuilder;
use databend_query::test_kits::TestGlobalServices;
use futures::TryStreamExt;
use goldenfile::Mint;
use tempfile::NamedTempFile;
use tokio::net::UnixListener;
use tokio::net::UnixStream;
use tokio_stream::wrappers::UnixListenerStream;
use tonic::transport::Channel;
use tonic::transport::Endpoint;
use tonic::transport::Server;
use tower::service_fn;
use tracing::debug;

const TEST_USER: &str = "test_user";
const TEST_PASSWORD: &str = "test_password";

async fn client_with_uds(path: String) -> FlightSqlServiceClient<Channel> {
    let connector = service_fn(move |_| UnixStream::connect(path.clone()));
    let channel = Endpoint::try_from("http://example.com")
        .unwrap()
        .connect_with_connector(connector)
        .await
        .unwrap();
    FlightSqlServiceClient::new(channel)
}

async fn run_query(
    client: &mut FlightSqlServiceClient<Channel>,
    sql: &str,
) -> std::result::Result<String, ArrowError> {
    let mut stmt = client.prepare(sql.to_string()).await?;
    let res = if stmt.dataset_schema()?.fields.is_empty() {
        let affected_rows = client.execute_update(sql.to_string()).await?;
        affected_rows.to_string()
    } else {
        let flight_info = stmt.execute().await?;
        let ticket = flight_info.endpoint[0].ticket.as_ref().unwrap().clone();
        let flight_data = client.do_get(ticket).await?;
        let flight_data: Vec<FlightData> = flight_data.try_collect().await.unwrap();
        let batches = flight_data_to_batches(&flight_data)?;
        pretty_format_batches(batches.as_slice())?.to_string()
    };
    Ok(res)
}

fn prepare_config() -> InnerConfig {
    let hash_method = PasswordHashMethod::DoubleSha1;
    let hash_value = hash_method.hash(TEST_PASSWORD.as_bytes());

    let auth_info = AuthInfo::Password {
        hash_value,
        hash_method,
    };
    ConfigBuilder::create()
        .add_user(TEST_USER, auth_info)
        .build()
}

#[tokio::test]
async fn test_query() -> Result<()> {
    let _guard = TestGlobalServices::setup(prepare_config()).await?;

    let file = NamedTempFile::new().unwrap();
    let path = file.into_temp_path().to_str().unwrap().to_string();
    let _ = fs::remove_file(path.clone());

    let uds = UnixListener::bind(path.clone()).unwrap();
    let stream = UnixListenerStream::new(uds);

    // We would just listen on TCP, but it seems impossible to know when tonic is ready to serve
    let service = FlightSqlServiceImpl::create();
    let (shutdown_tx, shutdown_rx) = tokio::sync::oneshot::channel::<()>();
    let serve_future = Server::builder()
        .add_service(FlightServiceServer::new(service))
        .serve_with_incoming_shutdown(stream, async { shutdown_rx.await.unwrap() });

    let request_future = async {
        let mut mint = Mint::new("tests/it/servers/flight_sql/testdata");
        let mut file = mint.new_goldenfile("query.txt").unwrap();
        let mut client = client_with_uds(path).await;
        let token = client.handshake(TEST_USER, TEST_PASSWORD).await.unwrap();
        debug!("Auth succeeded with token: {:?}", token);
        let cases = [
            "select 1, 'abc', 1.1, 1.1::float32, 1::nullable(int)",
            "select [1, 2]",
            "select (1, 1.1)",
            "select {1: 11, 2: 22}",
            "show tables",
            "drop table if exists test1",
            "create table test1(a int, b string)",
            "insert into table test1(a, b) values (1, 'x'), (2, 'y')",
            "select * from test1",
        ];
        for case in cases {
            writeln!(file, "---------- Input ----------").unwrap();
            writeln!(file, "{}", case).unwrap();
            writeln!(file, "---------- Output ---------").unwrap();
            let res = match run_query(&mut client, case).await {
                Ok(s) => s,
                Err(e) => format!("{e:?}"),
            };
            writeln!(file, "{}", res).unwrap();
        }
    };
    tokio::pin!(serve_future);

    tokio::select! {
        _ = &mut serve_future => panic!("server returned first"),
        _ = request_future => {
            debug!("Client finished!");
        }
    }
    shutdown_tx.send(()).unwrap();
    serve_future.await.unwrap();
    debug!("Server shutdown!");

    Ok(())
}
