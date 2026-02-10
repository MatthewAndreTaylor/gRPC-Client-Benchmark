# gRPC Python client performance benchmarking

This library intends to bench mark the performance of various [gRPC](https://grpc.io/) and [Protocol Buffer](https://protobuf.dev/) libraries in Python. 

## The Benchmark Experiment

This experiment explores the efficiency and feasibility of streaming images to Python clients using gRPC.
Image streaming is crucial in various real-world applications, such as remote sensing, medical imaging, and video surveillance, where low-latency and high-performance data transmission are essential.
By benchmarking this experiment, we aim to evaluate the scalability and responsiveness of each different Python library implementation. The test images used are of 4K resolution, simulating large payloads.

The proposed `image_service` implements two key endpoints:

- `/ListImages` => returns the names of the images the server can stream.
- `/StreamImages` => returns a **stream** of images, given requested image names.


## Client Libraries Tested

| Client package name | Protocol Buffer Library | Grpc Library |
|--------------------------------------------------------------|-------------------|------------------------------------------------|
| [`betterproto_grpclib_client`](/betterproto_grpclib_client/) | `betterproto`     | [`grpclib`](https://pypi.org/project/grpclib/) |
| [`protobuf_grpcio_client`](/protobuf_grpcio_client/)         | `google.protobuf` | [`grpcio`](https://pypi.org/project/grpcio/)   |
| [`protobuf_grpclib_client`](/protobuf_grpclib_client/)       | `google.protobuf` | [`grpclib`](https://pypi.org/project/grpclib/) |
| [`pyo3_client`](/pyo3_client/)                               | `prost`           | [`tonic`](https://docs.rs/tonic/latest/tonic/) |



## Getting started

### Setting Up the test server

Use the following commands to build and run the `image_service` test c++ server as a container:

```bash
cd test-server/cpp
./build.sh
./run
```


### Setting up the client profiler

Use the following commands to run the client benchmarking profiler:

```bash
sudo apt install python3-full python-dev pipx
poetry install
poetry run python grpc_python_profile.py
```

Running the profiler will create a set of graphs inside the `_profiles` directory.
The graphs are titled `GRPC Client Performance: <client-platform> : <service-implementation> - <type>`

<img src="https://github.com/MatthewAndreTaylor/protoWrap/blob/main/_profiles/grpc_python_profile_fps-81.png" />


## Client profiler metrics

The client profiler first imports each of the client wrapper packages.
Each wrapper package implements `list_images()` and `stream_images(image_names: list[str])` which call their respected endpoint.
The benchmark script runs multiple trials for random arrangements of profiles enforcing fairness.


### Running the example python clients

Add the `--show` argument to visualize the streamed images and have a display available.

```bash
# betterproto + grpclib client
poetry run python -m betterproto_grpclib_client

# google.protobuf + grpcio client
poetry run python -m protobuf_grpcio_client

# google.protobuf + grpclib client
poetry run python -m protobuf_grpclib_client

# rust / python bindings have extra install step
poetry run python -m pip install ./pyo3_client

# tonic + tokio client
poetry run python -m pyo3_client
```
