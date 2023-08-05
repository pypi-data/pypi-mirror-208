use pyo3::prelude::*;

mod client;

#[pymodule]
fn viazoom(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<client::ZoomOAuthClient>()?;
    Ok(())
}
