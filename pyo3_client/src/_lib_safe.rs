// use image_service::image_service_client::ImageServiceClient;
// use image_service::{ListImagesRequest, StreamImagesRequest};
// use pyo3::prelude::*;
// use std::sync::Arc;
// use tokio::{runtime::Runtime, sync::Mutex};
// use tonic::transport::Channel;

// pub mod image_service {
//     tonic::include_proto!("image_service");
// }

// #[pyclass]
// struct GrpcClient {
//     client: Arc<Mutex<ImageServiceClient<Channel>>>,
//     runtime: Runtime,
// }

// #[pymethods]
// impl GrpcClient {
//     #[new]
//     fn new(url: String) -> PyResult<Self> {
//         let runtime = tokio::runtime::Builder::new_current_thread()
//             .enable_all()
//             .build()?;

//         // NOTE: there is only a few differences, since we are using a single-threaded runtime Mutex is not necessary,
//         // I will keep it incase I find a way to use a multi-threaded runtime in the future.
//         // tokio = { version = "1.9", features = ["rt-multi-thread"] }
//         // let runtime = tokio::runtime::Builder::new_multi_thread()
//         //     .enable_all()
//         //     .build()?;

//         let client = runtime.block_on(async {
//             ImageServiceClient::connect(url)
//                 .await
//                 .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Connect error: {e}")))
//         })?;

//         Ok(Self {
//             client: Arc::new(Mutex::new(client)),
//             runtime,
//         })
//     }

//     fn list_images(&self) -> PyResult<Vec<String>> {
//         let client = self.client.clone();

//         self.runtime.block_on(async {
//             let mut client = client.lock().await;
//             let response = client
//                 .list_images(tonic::Request::new(ListImagesRequest {}))
//                 .await
//                 .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("RPC error: {e}")))?;

//             Ok(response.into_inner().image_names)
//         })
//     }

//     fn stream_images(&self, image_names: Vec<String>) -> PyResult<Vec<(String, Vec<u8>)>> {
//         let client = self.client.clone();

//         self.runtime.block_on(async {
//             let mut client = client.lock().await;
//             let request = tonic::Request::new(StreamImagesRequest { image_names });
//             let mut stream = client
//                 .stream_images(request)
//                 .await
//                 .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("RPC error: {e}")))?
//                 .into_inner();

//             let mut images = Vec::new();
//             while let Some(image) = stream
//                 .message()
//                 .await
//                 .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Stream error: {e}")))?
//             {
//                 images.push((image.name, image.content));
//             }

//             Ok(images)
//         })
//     }
// }

// #[pymodule]
// fn rs_image_client(m: &Bound<PyModule>) -> PyResult<()> {
//     m.add_class::<GrpcClient>()?;
//     Ok(())
// }