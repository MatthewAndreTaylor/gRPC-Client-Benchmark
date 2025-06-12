import grpc
from . import (
    image_service_pb2_grpc as image_service_pb2_grpc,
    image_service_pb2 as image_service_pb2,
)


async def list_images() -> list[str]:
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        client = image_service_pb2_grpc.ImageServiceStub(channel)
        return (
            await client.ListImages(image_service_pb2.ListImagesRequest())
        ).image_names


async def stream_images(image_names: list[str]):
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        client = image_service_pb2_grpc.ImageServiceStub(channel)
        images: list[image_service_pb2.Image] = []

        streaming_request = image_service_pb2.StreamImagesRequest(
            image_names=image_names
        )

        async for response_image in client.StreamImages(streaming_request):
            images.append(response_image)

        return images
