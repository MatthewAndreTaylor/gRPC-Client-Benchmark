use tonic::{transport::Server, Request, Response, Status};
use tonic::codegen::tokio_stream::wrappers::ReceiverStream;
use tokio::sync::mpsc;
use std::fs;
use std::path::Path;
use std::io::Read;
use image_service::image_service_server::{ImageService, ImageServiceServer};
use image_service::{ListImagesRequest, ListImagesResponse, StreamImagesRequest, StreamImagesResponse, Image};

pub mod image_service {
    tonic::include_proto!("image_service");
}

#[derive(Debug, Clone)]
struct ImageData {
    name: String,
    content: Vec<u8>,
    format: String,
    size_bytes: usize,
}

struct ImageServiceImpl {
    images: Vec<ImageData>,
}

impl ImageServiceImpl {
    fn read_images(directory: &str) -> Vec<ImageData> {
        let mut images = Vec::new();
        let path = Path::new(directory);

        if let Ok(entries) = fs::read_dir(path) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_file() {
                    let mut file = match fs::File::open(&path) {
                        Ok(f) => f,
                        Err(_) => continue,
                    };
                    let mut content = Vec::new();
                    if file.read_to_end(&mut content).is_err() {
                        continue;
                    }
                    let size_bytes = content.len();
                    images.push(ImageData {
                        name: path.file_name().unwrap().to_string_lossy().to_string(),
                        content,
                        format: path.extension().unwrap_or_default().to_string_lossy().to_string(),
                        size_bytes,
                    });
                }
            }
        }
        images
    }
}

#[tonic::async_trait]
impl ImageService for ImageServiceImpl {
    async fn list_images(
        &self,
        _request: Request<ListImagesRequest>,
    ) -> Result<Response<ListImagesResponse>, Status> {
        let mut response = ListImagesResponse::default();
        for image in &self.images {
            response.image_names.push(image.name.clone());
        }
        Ok(Response::new(response))
    }

    type StreamImagesStream = ReceiverStream<Result<StreamImagesResponse, Status>>;

    async fn stream_images(
        &self,
        request: Request<StreamImagesRequest>,
    ) -> Result<Response<Self::StreamImagesStream>, Status> {
        let (tx, rx) = mpsc::channel(4);
        let image_names = request.into_inner().image_names;
        let images = self.images.clone();

        tokio::spawn(async move {
            for image_name in image_names {
                if let Some(image) = images.iter().find(|img| img.name == image_name) {
                    let image_message = Image {
                        name: image.name.clone(),
                        content: image.content.clone(),
                        format: image.format.clone(),
                        size_in_bytes: image.size_bytes as i32,
                    };
                    let response = StreamImagesResponse {
                        image: Some(image_message),
                    };
                    if tx.send(Ok(response)).await.is_err() {
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
        images: ImageServiceImpl::read_images("../test_images"),
    };

    println!("Server listening on {}", addr);

    Server::builder()
        .add_service(ImageServiceServer::new(service))
        .serve(addr)
        .await?;

    Ok(())
}
