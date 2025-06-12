#include <vector>
#include <fstream>
#include <filesystem>
#include <iostream>
#include <grpc++/grpc++.h>

#include "image_service.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using image_service::ImageService;
using image_service::ListImagesRequest;
using image_service::ListImagesResponse;
using image_service::StreamImagesRequest;
using image_service::StreamImageResponse;

// Read images from a directory and save them
std::unordered_map<std::string, StreamImageResponse> images;

std::unordered_map<std::string, StreamImageResponse> ReadImages(const std::string& directory) {
    std::unordered_map<std::string, StreamImageResponse> images;
    size_t num_images = 0;
    for (const auto& entry : std::filesystem::directory_iterator(directory)) {
        if (entry.is_regular_file()) {
            num_images++;
        }
    }
    
    images.reserve(num_images);

    for (const auto& entry : std::filesystem::directory_iterator(directory)) {
        std::ifstream file(entry.path(), std::ios::binary);
        if (!file) {
            std::cerr << "Failed to open file: " << entry.path() << std::endl;
            continue;
        }

        std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        auto name = entry.path().filename().string();
        auto format = entry.path().extension().string();

        StreamImageResponse image_response;
        image_response.set_name(name);
        image_response.set_format(format);
        image_response.set_content(content);
        images[name] = std::move(image_response);
    }
    return images;
}



class ImageServiceImpl final : public ImageService::Service {
    Status ListImages(ServerContext* context, const ListImagesRequest* request, ListImagesResponse* reply) override {
        for (const auto& image: images) {
            reply->add_image_names(image.first);
        }
        return Status::OK;
    }
    Status StreamImages(ServerContext* context, const StreamImagesRequest* request, grpc::ServerWriter<StreamImageResponse>* writer) override {
        for (const auto& image_name : request->image_names()) {
            auto it = images.find(image_name);
            if (it != images.end()) {
                writer->Write(it->second);
            }
        }
        return Status::OK;
    }
};

void RunServer() {
    images = ReadImages("test_images");
    const std::string server_address("0.0.0.0:50051");
    ImageServiceImpl service;

    ServerBuilder builder;
    // Listen on the given address without any authentication mechanism.
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    // Register "service" as the instance through which we'll communicate with
    // clients. In this case it corresponds to an *synchronous* service.
    builder.RegisterService(&service);
    // Finally assemble the server.
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Server listening on " << server_address << std::endl;

    // Wait for the server to shutdown. Note that some other thread must be
    // responsible for shutting down the server for this call to ever return.
    server->Wait();
}

int main(int argc, char** argv) {
    RunServer();
    return 0;
}