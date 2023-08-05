use base64;
use pyo3::prelude::*;
use reqwest::header::{HeaderValue, AUTHORIZATION};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct AccessTokenResponse {
    access_token: String,
    token_type: String,
    expires_in: u64,
    scope: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct AccessTokenErrorResponse {
    status: bool,
    error_code: String,
    error_message: u64,
    result: String,
}

#[pyclass]
pub struct ZoomOAuthClient {
    #[pyo3(get)]
    account_id: String,
    #[pyo3(get)]
    client_id: String,
    client_secret: String,
    #[pyo3(get)]
    expires_in: u64,
    access_token: String,
}

#[pymethods]
impl ZoomOAuthClient {
    #[new(args = "*", kwargs = "**")]
    pub fn new(account_id: &str, client_id: &str, client_secret: &str) -> Self {
        ZoomOAuthClient {
            account_id: account_id.to_owned(),
            client_id: client_id.to_owned(),
            client_secret: client_secret.to_owned(),
            expires_in: 0,
            access_token: "".to_owned(),
        }
    }

    pub fn get_access_token(&mut self) -> PyResult<String> {
        let auth_string = format!("{}:{}", &self.client_id, &self.client_secret);
        let auth_header_value =
            HeaderValue::from_str(&format!("Basic {}", base64::encode(auth_string))).map_err(
                |err| {
                    PyErr::new::<pyo3::exceptions::PyException, _>(format!(
                        "Error formatting header value: {}",
                        err
                    ))
                },
            )?;

        let client = reqwest::blocking::Client::new();
        let res = client
            .post("https://zoom.us/oauth/token")
            .header("Host", "zoom.us")
            .header(AUTHORIZATION, auth_header_value)
            .form(&[
                ("grant_type", "account_credentials"),
                ("account_id", &self.account_id.to_string()),
            ])
            .send()
            .map_err(|err| {
                PyErr::new::<pyo3::exceptions::PyException, _>(format!(
                    "Error sending HTTP request: {}",
                    err
                ))
            })?;

        let token_response = res.json::<AccessTokenResponse>().map_err(|err| {
            PyErr::new::<pyo3::exceptions::PyException, _>(format!(
                "Error parsing access token response: {}",
                err
            ))
        })?;

        self.expires_in = token_response.expires_in;
        self.access_token = token_response.access_token.clone();
        Ok(token_response.access_token)
    }

    fn __repr__(slf: &PyCell<Self>) -> PyResult<String> {
        let class_name: &str = slf.get_type().name()?;
        Ok(format!(
            "{}(account_id={}, client_id={}, expires_in={}, access_token={})",
            class_name,
            slf.borrow().account_id,
            slf.borrow().client_id,
            slf.borrow().expires_in,
            slf.borrow().access_token,
        ))
    }
}
