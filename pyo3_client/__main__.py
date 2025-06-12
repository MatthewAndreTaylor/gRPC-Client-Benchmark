import asyncio
from . import list_images, stream_images
from PIL import Image
import argparse
import io

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Client for the Image Service",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="Display images using PIL",
    )
    args = parser.parse_args()

    print("Calling list_images")
    image_names = asyncio.run(list_images())

    print(f"Response: {image_names}")

    print("Calling stream_images")
    images = asyncio.run(stream_images(image_names))

    for img in images:
        print(img[0])
        img_data = io.BytesIO(bytes(img[1]))
        image = Image.open(img_data)

        print(f"Image size: {image.size}, Format: {image.format}")
        if args.show:
            image.show()
