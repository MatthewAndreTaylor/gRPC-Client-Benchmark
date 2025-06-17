from cpp_image_client import GrpcClient


async def list_images() -> list[str]:
    client = GrpcClient("http://localhost:50051")
    return client.list_images()


async def stream_images(image_names: list[str]):
    client = GrpcClient("http://localhost:50051")
    return client.stream_images(image_names)
