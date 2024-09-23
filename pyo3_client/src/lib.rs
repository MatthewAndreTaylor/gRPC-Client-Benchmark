use image_service::image_service_client::ImageServiceClient;
use image_service::ListImagesRequest;
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use tokio::runtime::Runtime;
use tonic::transport::Channel;


pub mod image_service {
    tonic::include_proto!("image_service");
}

#[pyclass]
struct GrpcClient {
    client: Option<Arc<Mutex<ImageServiceClient<Channel>>>>,
    runtime: Runtime,
}

#[pymethods]
impl GrpcClient {
    #[new]
    fn new() -> Self {
        Self {
            client: None,
            runtime: Runtime::new().unwrap(),
        }
    }

    fn open(&mut self, url: String) -> PyResult<()> {
        let rt = &self.runtime;
        let client = rt.block_on(async { 
            ImageServiceClient::connect(url).await.ok()
        });

        if let Some(client) = client {
            self.client = Some(Arc::new(Mutex::new(client)));
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Failed to connect to server"))
        }
    }

    fn close(&mut self) {
        self.client = None;
    }

    fn list_images(&self) -> PyResult<Vec<String>> {
        if let Some(client_arc) = &self.client {
            let client = client_arc.clone();
            let rt = &self.runtime;

            let result = rt.block_on(async {
                let mut client = client.lock().unwrap();
                let request = tonic::Request::new(ListImagesRequest {});
                client.list_images(request).await.ok().map(|resp| resp.into_inner().image_names)
            });

            result.ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Failed to get response"))
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Client not connected"))
        }
    }

    fn stream_images(&self, image_names: Vec<String>) -> PyResult<Vec<(String, Vec<u8>)>> {
        if let Some(client_arc) = &self.client {
            let client = client_arc.clone();
            let rt = &self.runtime;
    
            let result = rt.block_on(async {
                let mut client = client.lock().unwrap();
                let request = tonic::Request::new(image_service::StreamImagesRequest {
                    image_names,
                });
    
                let mut stream = client.stream_images(request).await.ok()?.into_inner();
                let mut images = Vec::new();
    
                while let Some(response) = stream.message().await.ok()? {
                    if let Some(image) = response.image {
                        images.push((image.name, image.content));
                    }
                }
    
                Some(images)
            });
    
            result.ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Failed to get response"))
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Client not connected"))
        }
    }
}

#[pymodule]
fn rs_image_client(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<GrpcClient>()?;
    Ok(())
}