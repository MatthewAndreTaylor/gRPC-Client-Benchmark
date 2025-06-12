use image_service::image_service_client::ImageServiceClient;
use image_service::{ListImagesRequest, StreamImagesRequest};

mod image_service {
    tonic::include_proto!("image_service");
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = ImageServiceClient::connect("http://localhost:50051").await?;

    // Call ListImages
    println!("Calling list_images...");
    let request = tonic::Request::new(ListImagesRequest {});
    let response = client.list_images(request).await?;
    
    let image_names = response.into_inner().image_names;
    println!("Response: {:?}", image_names);

    // Call StreamImages
    println!("Calling stream_images...");
    let request = tonic::Request::new(StreamImagesRequest {
        image_names: image_names.clone(),
    });

    let mut stream = client.stream_images(request).await?.into_inner();

    while let Some(response_image) = stream.message().await? {
        println!("Received image: {}", response_image.name);
        // Print the first 10 bytes of the image
        let image_data = response_image.content;
        let first_10_bytes = &image_data[..10];
        println!("First 10 bytes: {:?}", first_10_bytes);
    }

    Ok(())
}