import asyncio

from . import (
    image_service_grpc as image_service,
    image_service_pb2 as image_service_pb2,
)

from grpclib.client import Channel

display = False

if display:
    from PIL import Image
    import io


async def list_images() -> list[str]:
    async with Channel("localhost", 50051) as channel:
        client = image_service.ImageServiceStub(channel)
        return (await client.ListImages(image_service_pb2.ListImagesRequest())).image_names
    

async def stream_images(image_names: list[str]):
    async with Channel("localhost", 50051) as channel:
        client = image_service.ImageServiceStub(channel)
        images: list[image_service_pb2.Image] = []

        streaming_request = image_service_pb2.StreamImagesRequest(image_names=image_names)

        async with client.StreamImages.open() as stream:
            await stream.send_message(streaming_request)
            async for response in stream:
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