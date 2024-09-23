FROM ubuntu:latest

RUN apt update && apt install -y \
	build-essential \
	autoconf \
	libprotobuf-dev \
	libgrpc++-dev \
	libtool \
	pkg-config \
	protobuf-compiler \
	protobuf-compiler-grpc \
	&& apt clean \
	&& rm -rf /var/lib/apt/lists/*