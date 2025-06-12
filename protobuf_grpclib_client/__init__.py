from . import (
    image_service_grpc as image_service,
    image_service_pb2 as image_service_pb2,
)

from grpclib.client import Channel


async def list_images() -> list[str]:
    async with Channel("localhost", 50051) as channel:
        client = image_service.ImageServiceStub(channel)
        return (
            await client.ListImages(image_service_pb2.ListImagesRequest())
        ).image_names


async def stream_images(image_names: list[str]):
    async with Channel("localhost", 50051) as channel:
        client = image_service.ImageServiceStub(channel)
        images: list[image_service_pb2.Image] = []

        streaming_request = image_service_pb2.StreamImagesRequest(
            image_names=image_names
        )

        async with client.StreamImages.open() as stream:
            await stream.send_message(streaming_request)
            async for response_image in stream:
                images.append(response_image)

        return images
