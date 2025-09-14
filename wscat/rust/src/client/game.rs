use futures_util::{SinkExt, StreamExt};
use prost::Message;
use std::io::{self, Write};
use tokio_tungstenite::{connect_async, tungstenite::Message as WsMessage};
use wscat_rust::proto::{MathProblem, MathResponse, MathSolution};

async fn handle_initial_problem(
    ws_sender: &mut futures_util::stream::SplitSink<
        tokio_tungstenite::WebSocketStream<tokio_tungstenite::MaybeTlsStream<tokio::net::TcpStream>>,
        WsMessage,
    >,
    data: &[u8],
) -> Result<(), Box<dyn std::error::Error>> {
    let problem = MathProblem::decode(data)?;
    println!("Problem: {} + {} = ?", problem.a, problem.b);
    
    print!("Your answer: ");
    io::stdout().flush()?;
    let mut input = String::new();
    io::stdin().read_line(&mut input)?;
    
    let answer: i32 = input.trim().parse().map_err(|_| "Please enter a valid number!")?;
    
    let solution = MathSolution { answer };
    let solution_bytes = solution.encode_to_vec();
    ws_sender.send(WsMessage::Binary(solution_bytes.into())).await?;
    
    Ok(())
}

async fn handle_response(
    ws_sender: &mut futures_util::stream::SplitSink<
        tokio_tungstenite::WebSocketStream<tokio_tungstenite::MaybeTlsStream<tokio::net::TcpStream>>,
        WsMessage,
    >,
    data: &[u8],
) -> Result<bool, Box<dyn std::error::Error>> {
    let response = MathResponse::decode(data)?;
    
    match response.response_type {
        Some(wscat_rust::proto::math_response::ResponseType::Congratulations(msg)) => {
            println!("{}", msg);
            Ok(true) // Game finished
        }
        Some(wscat_rust::proto::math_response::ResponseType::NewProblem(problem)) => {
            println!("Wrong! New problem: {} + {} = ?", problem.a, problem.b);
            
            print!("Your answer: ");
            io::stdout().flush()?;
            let mut input = String::new();
            io::stdin().read_line(&mut input)?;
            
            let answer: i32 = input.trim().parse().map_err(|_| "Please enter a valid number!")?;
            
            let solution = MathSolution { answer };
            let solution_bytes = solution.encode_to_vec();
            ws_sender.send(WsMessage::Binary(solution_bytes.into())).await?;
            
            Ok(false) // Continue game
        }
        None => {
            println!("Received empty response from server");
            Ok(false)
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let url = "ws://127.0.0.1:8000/math";
    
    let (ws_stream, _) = connect_async(url).await?;
    println!("Connected to math game server!");
    
    let (mut ws_sender, mut ws_receiver) = ws_stream.split();
    
    // Handle initial problem
    if let Some(msg) = ws_receiver.next().await {
        match msg? {
            WsMessage::Binary(data) => {
                if let Err(e) = handle_initial_problem(&mut ws_sender, &data).await {
                    eprintln!("Error handling initial problem: {}", e);
                    return Ok(());
                }
            }
            _ => {
                eprintln!("Expected binary message for initial problem");
                return Ok(());
            }
        }
    }
    
    // Handle subsequent responses
    while let Some(msg) = ws_receiver.next().await {
        match msg? {
            WsMessage::Binary(data) => {
                match handle_response(&mut ws_sender, &data).await {
                    Ok(true) => break, // Game finished
                    Ok(false) => continue, // Continue game
                    Err(e) => {
                        eprintln!("Error handling response: {}", e);
                        break;
                    }
                }
            }
            WsMessage::Close(_) => {
                println!("Connection closed by server");
                break;
            }
            _ => {} // Ignore other message types
        }
    }
    
    Ok(())
}