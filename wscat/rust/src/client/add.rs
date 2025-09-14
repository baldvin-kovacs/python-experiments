use prost::Message;
use std::error::Error;
use wscat_rust::proto::{AddRequest, AddResponse};

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let add_req = AddRequest { a: 100, b: 50 };
    let payload = add_req.encode_to_vec();
    
    let client = reqwest::Client::new();
    let response = client
        .post("http://127.0.0.1:8000/add")
        .header("Content-Type", "application/protobuf")
        .body(payload)
        .send()
        .await?;
    
    if !response.status().is_success() {
        eprintln!("Error: HTTP {}", response.status());
        std::process::exit(1);
    }
    
    let response_bytes = response.bytes().await?;
    let add_resp = AddResponse::decode(&response_bytes[..])?;
    
    println!("Success! Result from server: {}", add_resp.result);
    
    Ok(())
}