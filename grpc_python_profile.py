import random
import time
import sys
import logging
from pandas import DataFrame
import matplotlib.pyplot as plt
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_import(module_name, name):
    try:
        module = __import__(module_name)
        return getattr(module, name)
    except Exception as e:
        logger.warning(f"Failed to import {name} from {module_name}: {e}")
        return None


unary_methods = [
    safe_import("betterproto_grpclib_client", "list_images"),
    safe_import("protobuf_grpclib_client", "list_images"),
    safe_import("protobuf_grpcio_client", "list_images"),
    safe_import("pyo3_client", "list_images"),
]

streaming_methods = [
    safe_import("betterproto_grpclib_client", "stream_images"),
    safe_import("protobuf_grpclib_client", "stream_images"),
    safe_import("protobuf_grpcio_client", "stream_images"),
    safe_import("pyo3_client", "stream_images"),
]

unary_methods = [method for method in unary_methods if method is not None]
streaming_methods = [method for method in streaming_methods if method is not None]


class GrpcOperationProfile:
    def __init__(self, op, size, constructor_params=[]):
        self.size = size
        self.test_operation = op
        self.execution_times = []
        self.constructor_params = constructor_params

    def as_tuple(self) -> tuple:
        return (
            self.size,
            self.test_operation.__module__,
            self.test_operation.__name__,
            self.execution_times,
        )

    def run(self, *args, **kwargs) -> None:
        start = time.perf_counter_ns()
        asyncio.run(self.test_operation(*self.constructor_params, *args, **kwargs))
        end = time.perf_counter_ns()
        self.execution_times.append(end - start)


def run_profiles(profiles: GrpcOperationProfile, trials: int) -> None:
    for i in range(trials):
        logger.info(f"Trial: {i + 1}/{trials}")
        random.shuffle(profiles)
        for profile in profiles:
            profile.run()


def to_dataframe(profiles: GrpcOperationProfile):
    frame = DataFrame.from_records(
        data=map(lambda profile: profile.as_tuple(), profiles),
        columns=["arg_size", "module", "operation", "time"],
    )
    frame = frame.explode("time")
    frame["time"] = frame["time"].astype(float)
    frame["time"] /= 10**3
    return frame


def execute_profiles(profiles, num_trials):
    run_profiles(profiles, num_trials)
    df = to_dataframe(profiles)
    return df


def plot_profiles(df, seed: int, service_metadata: str):
    # Plotting time as a function of argument size
    _, ax = plt.subplots()
    plt.title(
        f"GRPC Client Performance : {sys.platform} : {service_metadata} - Total Time"
    )
    ax.set_xlabel("Number of frames")
    ax.set_ylabel("Time (microseconds)")

    grouped = df.groupby(["module", "operation"])
    for name, group in grouped:
        means = group.groupby("arg_size")["time"].mean()
        ax.plot(means, label=str(name))
    ax.legend()

    plt.savefig(f"_profiles/grpc_python_profile-{seed}.png")
    plt.close()


def plot_fps(df, seed: int, service_metadata: str):
    # Plotting fps
    _, ax = plt.subplots()
    plt.title(f"GRPC Client Performance : {sys.platform} : {service_metadata} - FPS")
    ax.set_xlabel("Number of frames")
    ax.set_ylabel("FPS")

    grouped = df.groupby("module")
    for name, group in grouped:
        time_for_frames = group.groupby("arg_size")["time"].mean()

        frames = []
        fps_values = []
        for num_frames, time in time_for_frames.items():
            seconds = time / 10**6
            fps_values.append(num_frames / seconds)
            frames.append(num_frames)

        ax.plot(frames, fps_values, label=name, marker="o")

        # Annotate every second point with its FPS value
        # for x, y in zip(frames[::2], fps_values[::2]):
        #     ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0,5), ha='center', fontsize=10)

        # Annotate the last point with its FPS value
        x, y = frames[-1], fps_values[-1]
        ax.annotate(
            f"{y:.1f}",
            (x, y),
            textcoords="offset points",
            xytext=(40, 0),
            ha="center",
            fontsize=10,
        )

    ax.legend()
    plt.savefig(f"_profiles/grpc_python_profile_fps-{seed}.png")
    plt.close()


def unary_stream_profiles(stream_image_names: list[list[str]]):
    profiles = []
    for image_names in stream_image_names:
        for stream_method in streaming_methods:
            stream_profile = GrpcOperationProfile(
                stream_method,
                constructor_params=[image_names],
                size=len(image_names),
            )
            profiles.append(stream_profile)

    return profiles


def get_service_meta():
    import grpc
    from google.protobuf import empty_pb2

    channel = grpc.insecure_channel("localhost:50051")
    request = empty_pb2.Empty()
    response_bytes = channel.unary_unary(
        "/image_service.ImageService/ServiceMetadata",
        request_serializer=empty_pb2.Empty.SerializeToString,
        response_deserializer=lambda x: x,
    )(request)
    channel.close()

    response_bytes = response_bytes[2:]
    response_string = response_bytes.decode("utf-8").strip()
    logger.info(f"Service: {response_string}")
    return response_string


if __name__ == "__main__":
    metadata = get_service_meta()
    seed = 83
    random.seed(seed)
    # unary_profiles = unary_unary_profiles()

    base_image_names = ["image-0.jpg", "image-1.jpg", "image-2.jpg"]

    # smaller sub samples
    stream_image_names = [base_image_names * i for i in range(1, 100, 5)]
    random.shuffle(stream_image_names)

    stream_profiles = unary_stream_profiles(stream_image_names)

    df = execute_profiles(stream_profiles, 6)
    plot_profiles(df, seed, metadata)
    plot_fps(df, seed, metadata)
