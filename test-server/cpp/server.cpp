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
using image_service::StreamImagesResponse;
using image_service::Image;

struct ImageData {
    std::string name;
    std::string content;
    std::string format;
    int size_bytes;
};

// Read images from a directory and save them 
std::vector <ImageData> images;

std::vector <ImageData> ReadImages(const std::string& directory) {
    std::vector <ImageData> images;
    for (const auto& entry : std::filesystem::directory_iterator(directory)) {
        std::ifstream file(entry.path(), std::ios::binary);
        if (!file) {
            std::cerr << "Failed to open file: " << entry.path() << std::endl;
            continue;
        }
        ImageData image;
        image.name = entry.path().filename().string();
        file.seekg(0, std::ios::end);
        image.size_bytes = file.tellg();
        file.seekg(0, std::ios::beg);
        image.content.resize(image.size_bytes);
        file.read(image.content.data(), image.size_bytes);
        image.format = entry.path().extension().string();
        images.push_back(image);
    }
    return images;
}



class ImageServiceImpl final : public ImageService::Service {
    Status ListImages(ServerContext* context, const ListImagesRequest* request, ListImagesResponse* reply) override {
        for (const auto& image : images) {
            reply->add_image_names(image.name);
        }
        return Status::OK;
    }
    Status StreamImages(ServerContext* context, const StreamImagesRequest* request, grpc::ServerWriter<StreamImagesResponse>* writer) override {

        for (const auto& image_name: request->image_names()) {
            auto image = std::find_if(images.begin(), images.end(), [&image_name](const ImageData& image) {
                return image.name == image_name;
            });

            if (image == images.end()) {
                continue;
            }

            Image image_message;
            image_message.set_name(image->name);
            image_message.set_content(image->content);
            image_message.set_format(image->format);
            image_message.set_size_in_bytes(image->size_bytes);

            StreamImagesResponse response;
            response.mutable_image()->CopyFrom(image_message);
            writer->Write(response);
        }

        return Status::OK;
    }
};

void RunServer() {
    images = ReadImages("test_images");

    std::string server_address("0.0.0.0:50051");
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