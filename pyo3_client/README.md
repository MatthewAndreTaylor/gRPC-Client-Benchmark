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
| `tonic`           | [`tokio`](https://crates.io/crates/tokio)      |