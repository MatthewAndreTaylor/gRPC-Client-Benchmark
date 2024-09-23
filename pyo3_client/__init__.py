from rs_image_client import GrpcClient
import asyncio

display = False

if display:
    from PIL import Image
    import io
    import os # showing images is disabled in wsl
    os.makedirs("target/images", exist_ok=True)


async def list_images() -> list[str]:
    client = GrpcClient()
    client.open("http://localhost:50051")
    image_names = client.list_images()
    client.close()
    return image_names
    

async def stream_images(image_names: list[str]):
    client = GrpcClient()
    client.open("http://localhost:50051")
    images = client.stream_images(image_names)
    client.close()
    return images


if __name__ == "__main__":
    print("Calling list_images")
    image_names = asyncio.run(list_images())

    print(f"Response: {image_names}")

    print("Calling stream_images")

    images = asyncio.run(stream_images(image_names))

    for img_name, img_content in images:
        print(f"Image: {img_name}")

        if display:
            img_data = io.BytesIO(bytes(img_content))
            image = Image.open(img_data)
            image.save(f"target/images/{img_name}")
            