# Grpc Python client performance benchmarking

This library intends to bench mark the performance of various [Grpc](https://grpc.io/) and [Protocol Buffer](https://protobuf.dev/) libraries in Python. 

## The Benchmark Experiment

This experiment explores the efficiency and feasibility of streaming images to Python clients using Grpc.
Image streaming is crucial in various real-world applications, such as remote sensing, medical imaging, and video surveillance, where low-latency and high-performance data transmission are essential.
By benchmarking this experiment, we aim to evaluate the scalability and responsiveness of each different Python library implementation.

The proposed `image_service` implements two key endpoints:

- `/ListImages` => returns the names of the images the server can stream.
- `/StreamImages` => returns a **stream** of images, given requested image names.


## Client Libraries Tested

| Client package name | Protocol Buffer Library | Grpc Library |
|--------------------------------------------------------------|-------------------|------------------------------------------------|
| [`betterproto_grpclib_client`](/betterproto_grpclib_client/) | `betterproto`     | [`grpclib`](https://pypi.org/project/grpclib/) |
| [`protobuf_grpcio_client`](/protobuf_grpcio_client/)         | `google.protobuf` | [`grpcio`](https://pypi.org/project/grpcio/)   |
| [`protobuf_grpclib_client`](/protobuf_grpclib_client/)       | `google.protobuf` | [`grpclib`](https://pypi.org/project/grpclib/) |
| [`pyo3_client`](/pyo3_client/)                               | `tonic`           | [`tokio`](https://crates.io/crates/tokio)      |



## Getting started

### Setting Up the test server

Use the following commands to build and run the `image_service` test server:

```bash
cd test-server/cpp
./build
./run
```


### Setting up the client profiler

Use the following commands to run the client profiler:

```bash
poetry install
poetry run python grpc_python_profile.py 
```

Running the profiler will create a set of graphs inside the `_profiles` directory.


<img src="https://github.com/MatthewAndreTaylor/protoWrap/blob/main/_profiles/grpc_python_profile-46.png" />


## Client profiler metrics

The client profiler first imports each of the client wrapper packages.
Each wrapper package implements `list_images()` and `stream_images(image_names: list[str])` which call their respected endpoint.
The benchmark script runs multiple trials for random arrangements of profiles enforcing fairness.
