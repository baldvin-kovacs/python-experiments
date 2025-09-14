use axum::{
    extract::{ws::WebSocket, WebSocketUpgrade},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::{get, post},
    Router,
};
use futures_util::StreamExt;
use prost::Message;
use rand::Rng;
use wscat_rust::proto::{AddRequest, AddResponse, MathProblem, MathResponse, MathSolution};

fn generate_math_problem() -> MathProblem {
    let mut rng = rand::thread_rng();
    MathProblem {
        a: rng.gen_range(1..20),
        b: rng.gen_range(1..20),
    }
}

async fn add_handler(body: axum::body::Bytes) -> Result<Response, StatusCode> {
    let add_request = AddRequest::decode(&body[..]).map_err(|_| StatusCode::BAD_REQUEST)?;
    
    let result = add_request.a + add_request.b;
    println!("Received request: a={}, b={}. Result: {}", add_request.a, add_request.b, result);
    
    let add_response = AddResponse { result };
    let response_bytes = add_response.encode_to_vec();
    
    Ok((
        [("content-type", "application/protobuf")],
        response_bytes,
    ).into_response())
}

async fn websocket_handler(ws: WebSocketUpgrade) -> Response {
    ws.on_upgrade(handle_socket)
}

async fn handle_socket(mut socket: WebSocket) {
    println!("WebSocket connection established for math problems");
    
    // Send initial math problem
    let mut problem = generate_math_problem();
    println!("Sending problem: {} + {}", problem.a, problem.b);
    let problem_bytes = problem.encode_to_vec();
    
    if socket.send(axum::extract::ws::Message::Binary(problem_bytes)).await.is_err() {
        println!("Failed to send initial problem");
        return;
    }
    
    while let Some(msg) = socket.next().await {
        match msg {
            Ok(axum::extract::ws::Message::Binary(data)) => {
                // Parse solution
                let solution = match MathSolution::decode(&data[..]) {
                    Ok(sol) => sol,
                    Err(_) => {
                        println!("Failed to parse solution");
                        break;
                    }
                };
                
                let expected = problem.a + problem.b;
                println!("Received answer: {}, expected: {}", solution.answer, expected);
                
                if solution.answer == expected {
                    // Correct answer - send congratulations
                    let response = MathResponse {
                        response_type: Some(wscat_rust::proto::math_response::ResponseType::Congratulations(
                            "Congratulations! Correct answer!".to_string()
                        )),
                    };
                    let response_bytes = response.encode_to_vec();
                    
                    if socket.send(axum::extract::ws::Message::Binary(response_bytes)).await.is_err() {
                        println!("Failed to send congratulations");
                        break;
                    }
                    
                    println!("Sent congratulations message");
                    break;
                } else {
                    // Wrong answer - send new problem
                    problem = generate_math_problem();
                    let response = MathResponse {
                        response_type: Some(wscat_rust::proto::math_response::ResponseType::NewProblem(
                            problem.clone()
                        )),
                    };
                    let response_bytes = response.encode_to_vec();
                    
                    if socket.send(axum::extract::ws::Message::Binary(response_bytes)).await.is_err() {
                        println!("Failed to send new problem");
                        break;
                    }
                    
                    println!("Wrong answer. Sending new problem: {} + {}", problem.a, problem.b);
                }
            }
            Ok(axum::extract::ws::Message::Close(_)) => {
                println!("Connection closed by client");
                break;
            }
            Err(e) => {
                println!("WebSocket error: {}", e);
                break;
            }
            _ => {} // Ignore other message types
        }
    }
    
    println!("WebSocket connection closed");
}

async fn root_handler() -> &'static str {
    "Protobuf service is running. POST to /add to use. WebSocket math game at /math."
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(root_handler))
        .route("/add", post(add_handler))
        .route("/math", get(websocket_handler));

    let listener = tokio::net::TcpListener::bind("127.0.0.1:8000")
        .await
        .unwrap();
    
    println!("Server running on http://127.0.0.1:8000");
    println!("POST to /add for addition, WebSocket at /math for math game");
    
    axum::serve(listener, app).await.unwrap();
}