use std::{io::Read, path::Path, sync::Arc};

use tokio::sync::mpsc;
use tonic::{transport::Server, Request, Response, Status};
use tonic::codegen::tokio_stream::wrappers::ReceiverStream;

use image_service::image_service_server::{ImageService, ImageServiceServer};
use image_service::{ListImagesRequest, ListImagesResponse, StreamImagesRequest, StreamImageResponse, ServiceMetadataRequest, ServiceMetadataResponse};

pub mod image_service {
    tonic::include_proto!("image_service");
}

struct ImageServiceImpl {
    images: Arc<Vec<StreamImageResponse>>,
}

impl ImageServiceImpl {
    fn read_images(directory: &str) -> Vec<StreamImageResponse> {
        let mut images = Vec::new();
        let path = Path::new(directory);

        if let Ok(entries) = std::fs::read_dir(path) {
            for entry in entries.flatten() {
                let path = entry.path();
                println!("Processing file: {:?}", path);

                if path.is_file() {
                    let mut file = match std::fs::File::open(&path) {
                        Ok(f) => f,
                        Err(_) => continue,
                    };
                    let mut content = Vec::new();
                    if file.read_to_end(&mut content).is_err() {
                        continue;
                    }
                    images.push(StreamImageResponse {
                        name: path.file_name().unwrap().to_string_lossy().to_string(),
                        format: path.extension().unwrap_or_default().to_string_lossy().to_string(),
                        content: content,
                    });
                }
            }
        }
        images
    }
}

#[tonic::async_trait]
impl ImageService for ImageServiceImpl {

    async fn service_metadata(
        &self,
        _request: Request<ServiceMetadataRequest>,
    ) -> Result<Response<ServiceMetadataResponse>, Status> {
        let response = ServiceMetadataResponse {
            metadata: "image_service-rust-alpha".to_string(),
        };
        Ok(Response::new(response))
    }

    async fn list_images(
        &self,
        _request: Request<ListImagesRequest>,
    ) -> Result<Response<ListImagesResponse>, Status> {
        let mut response = ListImagesResponse::default();
        for image in self.images.iter() {
            response.image_names.push(image.name.clone());
        }
        Ok(Response::new(response))
    }

    type StreamImagesStream = ReceiverStream<Result<StreamImageResponse, Status>>;

    async fn stream_images(
        &self,
        request: Request<StreamImagesRequest>,
    ) -> Result<Response<Self::StreamImagesStream>, Status> {
        let (tx, rx) = mpsc::channel(128);
        let image_names = request.into_inner().image_names;
        let images = Arc::clone(&self.images);

        tokio::spawn(async move {
            for name in image_names {
                if let Some(image) = images.iter().find(|img| img.name == name) {
                    if tx.send(Ok(image.clone())).await.is_err() {
                        break;
                    }
                }
            }
        });

        Ok(Response::new(ReceiverStream::new(rx)))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "0.0.0.0:50051".parse()?;
    let service = ImageServiceImpl {
        images: Arc::new(ImageServiceImpl::read_images("images")),
    };

    println!("Server listening on {}", addr);
    Server::builder()
        .add_service(ImageServiceServer::new(service))
        .serve(addr)
        .await?;

    Ok(())
}
