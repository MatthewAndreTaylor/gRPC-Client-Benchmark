use futures_util::TryStreamExt;
use image_service::image_service_client::ImageServiceClient;
use image_service::{ListImagesRequest, StreamImagesRequest};
use pyo3::prelude::*;
use tokio::runtime::Runtime;
use tonic::transport::Channel;

pub mod image_service {
    tonic::include_proto!("image_service");
}

#[pyclass]
struct GrpcClient {
    client: ImageServiceClient<Channel>,
    runtime: Runtime,
}

#[pymethods]
impl GrpcClient {
    #[new]
    fn new(url: String) -> PyResult<Self> {
        let runtime = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()?;

        let client = runtime.block_on(async {
            ImageServiceClient::connect(url).await.map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Connect error: {e}"))
            })
        })?;

        Ok(Self {
            client: client,
            runtime: runtime,
        })
    }

    fn list_images(&mut self) -> PyResult<Vec<String>> {
        self.runtime.block_on(async {
            let response = self
                .client
                .list_images(tonic::Request::new(ListImagesRequest {}))
                .await
                .map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("RPC error: {e}"))
                })?;

            Ok(response.into_inner().image_names)
        })
    }

    fn stream_images(&mut self, image_names: Vec<String>) -> PyResult<Vec<(String, Vec<u8>)>> {
        self.runtime.block_on(async {
            let request = tonic::Request::new(StreamImagesRequest { image_names });
            let stream = self
                .client
                .stream_images(request)
                .await
                .map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("RPC error: {e}"))
                })?
                .into_inner();

            let images: Vec<_> = stream
                .map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Stream error: {e}"))
                })
                .map_ok(|image| (image.name, image.content))
                .try_collect()
                .await?;

            Ok(images)
        })
    }
}

#[pymodule]
fn rs_image_client(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<GrpcClient>()?;
    Ok(())
}
