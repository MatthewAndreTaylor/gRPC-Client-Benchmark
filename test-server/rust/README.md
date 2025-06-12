# Rust local process client server

## prerequisites

```bash
sudo apt update
sudo apt install build-essential protobuf-compiler
```

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```


## server

```
cargo run --bin image-service-server
```

## client

```
cargo run --bin image-service-client
```