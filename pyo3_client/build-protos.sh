#!/bin/bash

echo "Building proto files"

_pcb_dir=$(dirname "${BASH_SOURCE[0]}")
_CLIENT_ROOT=$(realpath "${_pcb_dir}")

build-client()
{
    local files
    local files_array

    pushd ${_CLIENT_ROOT} > /dev/null

    proto_folder="${_CLIENT_ROOT}/../"
    files=$(find "$proto_folder" -maxdepth 1 -name '*.proto')
    IFS=$'\n' read -r -d '' -a files_array <<< "$files"

    echo files_array: "${files_array[@]}"

    mkdir -p "${_CLIENT_ROOT}/proto"

    # Copy all proto files to proto folder
    for file in "${files_array[@]}"; do
        cp "$file" "${_CLIENT_ROOT}/proto"
    done

    popd > /dev/null

    return $?
}

build-client "$@"


cargo install maturin
maturin build

# maturin develop
# maturin build --release