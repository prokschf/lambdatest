use lambda_runtime::{handler_fn, Context, Error};
use nalgebra::{DMatrix, Matrix2x3};
use serde_json::{json, Value};

async fn matrix_inverse(event: Value, _: Context) -> Result<Value, Error> {
    // Example: Deserializing and working with a fixed-size matrix
    // You'll need to adapt this for dynamic matrices based on your input
    let matrix_data: Vec<Vec<f64>> = serde_json::from_value(event)?;
    let n = matrix_data.len();
    let m = DMatrix::from_fn(n, n, |i, j| matrix_data[i][j]);
    let inverse = m.try_inverse().ok_or_else(|| "Matrix is not invertible")?;

    Ok(json!(inverse.data.as_vec()))
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    let func = handler_fn(matrix_inverse);
    lambda_runtime::run(func).await?;
    Ok(())
}
