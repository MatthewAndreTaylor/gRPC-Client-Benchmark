#!/bin/bash


_pcb_dir=$(dirname "${BASH_SOURCE[0]}")
_CLIENT_ROOT=$(realpath "${_pcb_dir}")

build-client()
{
    local files
    local files_array

    pushd ${_CLIENT_ROOT} > /dev/null

    proto_folder="${_CLIENT_ROOT}/../"
    files=$(find "$proto_folder" -name '*.proto')
    IFS=$'\n' read -r -d '' -a files_array <<< "$files"

    echo files_array: "${files_array[@]}"

    poetry run python -m grpc_tools.protoc -I"$proto_folder" \
           --experimental_allow_proto3_optional \
            --python_out="${_CLIENT_ROOT}" \
            --grpc_python_out="${_CLIENT_ROOT}" \
           "${files_array[@]}"


    popd > /dev/null

    return $?
}

build-client "$@"