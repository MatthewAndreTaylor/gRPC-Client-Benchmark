// This protoc to compile the protobuf definitions for the gRPC service.
// This uses the `protoc-bin-vendored` crate to if `protoc` is not installed on the system.
// fn main() -> Result<(), Box<dyn std::error::Error>> {
//     tonic_build::compile_protos("proto/image_service.proto")?;
//     Ok(())
// }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Try to compile using tonic_build directly
    if let Err(e) = tonic_build::compile_protos("proto/image_service.proto") {
        eprintln!("Error compiling protos with tonic_build: {}", e);

        // Fallback to setting PROTOC manually
        let protoc_path = protoc_bin_vendored::protoc_bin_path()
            .map_err(|e| format!("Failed to get protoc: {}", e))?;

        std::env::set_var("PROTOC", protoc_path);
        tonic_build::configure()
            .compile_protos(&["proto/image_service.proto"], &["proto"])
            .map_err(|e| format!("Fallback compilation failed: {}", e))?;
    }

    Ok(())
}