#!/bin/bash

. $(dirname 0)/config.sh

rm -vf server *.o image_service.pb.cc image_service.pb.h image_service.grpc.pb.cc image_service.grpc.pb.h $PROTO_FILE
docker image rm -f $DOCKER_IMAGE

rm -rf test_images