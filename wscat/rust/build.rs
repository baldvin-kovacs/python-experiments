use std::io::Result;

fn main() -> Result<()> {
    prost_build::compile_protos(&["../proto/simple_math.proto"], &["../proto/"])?;
    Ok(())
}