from . import image_service
from grpclib.client import Channel


async def list_images() -> list[str]:
    async with Channel("localhost", 50051) as channel:
        client = image_service.ImageServiceStub(channel)
        return (await client.list_images(image_service.ListImagesRequest())).image_names


async def stream_images(image_names: list[str]):
    async with Channel("localhost", 50051) as channel:
        client = image_service.ImageServiceStub(channel)
        images: list[image_service.Image] = []
        streaming_request = image_service.StreamImagesRequest(image_names=image_names)

        async for response_image in client.stream_images(streaming_request):
            images.append(response_image)

        return images
