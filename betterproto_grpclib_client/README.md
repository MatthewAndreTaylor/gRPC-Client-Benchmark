# betterproto_grpclib_client

Pure Python messages, no tricks, very pythonic style

example:

```py
@dataclass(eq=False, repr=False)
class ListImagesRequest(betterproto.Message):
    """Request message for ListImages RPC"""

    pass
```

```py
async with Channel("localhost", 50051) as channel:
    ...
```


| Protocol Buffer Library | Grpc Library |
|-------------------|------------------------------------------------|
| `betterproto`     | [`grpclib`](https://pypi.org/project/grpclib/) |