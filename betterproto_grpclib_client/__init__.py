import asyncio
from . import image_service

from grpclib.client import Channel

display = False

if display:
    from PIL import Image
    import io


async def list_images() -> list[str]:
    async with Channel("localhost", 50051) as channel:
        client = image_service.ImageServiceStub(channel)
        return (await client.list_images(image_service.ListImagesRequest())).image_names
    

async def stream_images(image_names: list[str]):
    async with Channel("localhost", 50051) as channel:
        client = image_service.ImageServiceStub(channel)
        images: list[image_service.Image] = []

        streaming_request = image_service.StreamImagesRequest(image_names=image_names)

        async for response in client.stream_images(streaming_request):
            images.append(response.image)

        return images


if __name__ == "__main__":
    print("Calling list_images")
    image_names = asyncio.run(list_images())

    print(f"Response: {image_names}")

    print("Calling stream_images")

    images = asyncio.run(stream_images(image_names))

    for img in images:
        print(img.name)
        
        if display:
            img_data = io.BytesIO(bytes(img.content))
            image = Image.open(img_data)
            image.show()
            

