DOCKER_IMAGE=grpc-cpp:latest
CONTAINER_NAME=grpc-cpp-image-server
PROTO_PATH=../../
PROTO_FILE=image_service.proto
DOCKER_RUN="docker run --rm -v //$PWD://$PWD -w //$PWD"