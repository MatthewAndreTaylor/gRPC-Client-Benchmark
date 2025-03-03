import random
import time
import sys
from pandas import DataFrame
import matplotlib.pyplot as plt
import asyncio

from betterproto_grpclib_client import (
    list_images as list_images_betterproto,
    stream_images as stream_images_betterproto,
)

from protobuf_grpclib_client import (
    list_images as list_images_protobuf,
    stream_images as stream_images_protobuf,
)

from protobuf_grpcio_client import (
    list_images as list_images_protobuf_grpcio,
    stream_images as stream_images_protobuf_grpcio,
)

from pyo3_client import (
    list_images as list_images_pyo3,
    stream_images as stream_images_pyo3,
)

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
        print(f"Trial: {i + 1}/{trials}")
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


def plot_profiles(df, seed : int):
    # Plotting time as a function of argument size
    _, ax = plt.subplots()
    plt.title(f"GRPC Client Performance : {sys.platform}")
    ax.set_xlabel("Size of the argument")
    ax.set_ylabel("Time (microseconds)")

    grouped = df.groupby(["module", "operation"])
    for name, group in grouped:
        means = group.groupby("arg_size")["time"].mean()
        ax.plot(means, label=str(name))
    ax.legend()

    plt.savefig(f"_profiles/grpc_python_profile-{seed}.png")
    plt.close()


def plot_fps(df, seed : int):
    # Plotting fps
    _, ax = plt.subplots()
    plt.title(f"GRPC Client Performance : {sys.platform} - FPS")
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

        ax.plot(frames, fps_values, label=name)

    ax.legend()
    plt.savefig(f"_profiles/grpc_python_profile_fps-{seed}.png")
    plt.close()



def unary_unary_profiles(call_numbers: list[int] = [1, 10, 100, 1000]):
    for call_number in call_numbers:
        def unary_unary_call(method):
            async def _():
                for _ in range(call_number):
                    await method()

            return _

        profiles = [
            GrpcOperationProfile(unary_unary_call(list_images_protobuf), size=call_number),
            GrpcOperationProfile(unary_unary_call(list_images_betterproto), size=call_number),
            GrpcOperationProfile(unary_unary_call(list_images_protobuf_grpcio), size=call_number),
            GrpcOperationProfile(unary_unary_call(list_images_pyo3), size=call_number),
        ]

    return profiles


def unary_stream_profiles(stream_image_names: list[list[str]]):
    profiles = []
    for image_names in stream_image_names:
        profiles.append(
            GrpcOperationProfile(stream_images_protobuf, constructor_params=[image_names], size=len(image_names))
        )
        profiles.append(
            GrpcOperationProfile(stream_images_betterproto, constructor_params=[image_names], size=len(image_names))
        )

        profiles.append(
            GrpcOperationProfile(stream_images_protobuf_grpcio, constructor_params=[image_names], size=len(image_names))
        )

        profiles.append(
            GrpcOperationProfile(stream_images_pyo3, constructor_params=[image_names], size=len(image_names))
        )
    
    return profiles

if __name__ == "__main__":
    seed = 50
    random.seed(seed)
    #unary_profiles = unary_unary_profiles()

    base_image_names = ["image-0.jpg", "image-1.jpg", "image-2.jpg"]

    # smaller sub samples
    stream_image_names = [ base_image_names* i for i in range(1, 100, 5)]
    random.shuffle(stream_image_names)

    stream_profiles = unary_stream_profiles(stream_image_names)

    df = execute_profiles(stream_profiles, 5)
    plot_profiles(df, seed)
    plot_fps(df, seed)
    