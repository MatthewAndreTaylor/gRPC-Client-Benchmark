# protobuf_grpcio_client

Rust implementation using pyo3 bindings.

```rs
let request = tonic::Request::new(ListImagesRequest {});
```

```py
client.open("http://localhost:50051")
...
```



| Protocol Buffer Library | Grpc Library |
|-------------------|------------------------------------------------|
| `prost`           | [`tonic`](https://docs.rs/tonic/latest/tonic/) |