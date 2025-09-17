import logging
import random
from fastapi import FastAPI, Request, Response, WebSocket
from . import simple_math_pb2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/add", response_class=Response)
async def add_numbers(request: Request) -> Response:
    body = await request.body()

    add_request = simple_math_pb2.AddRequest()
    add_request.ParseFromString(body)

    result = add_request.a + add_request.b
    logger.info(f"Received request: a={add_request.a}, b={add_request.b}. Result: {result}")

    # 3. Create the response object and serialize it to binary Protobuf
    add_response = simple_math_pb2.AddResponse(result=result)
    
    return Response(
        content=add_response.SerializeToString(),
        media_type="application/protobuf"
    )

def generate_math_problem():
    """Generate a random math problem with two integers below 20."""
    a = random.randint(1, 19)
    b = random.randint(1, 19)
    return simple_math_pb2.MathProblem(a=a, b=b)

@app.websocket("/math")
async def websocket_math_endpoint(websocket: WebSocket):
    #print('yyy', flush=True)
    await websocket.accept()
    logger.info("WebSocket connection established for math problems")
    
    try:
        # Send initial math problem
        problem = generate_math_problem()
        logger.info(f"Sending problem: {problem.a} + {problem.b}")
        await websocket.send_bytes(problem.SerializeToString())
        
        while True:
            # Wait for solution
            data = await websocket.receive_bytes()
            solution = simple_math_pb2.MathSolution()
            solution.ParseFromString(data)
            
            expected = problem.a + problem.b
            logger.info(f"Received answer: {solution.answer}, expected: {expected}")
            
            if solution.answer == expected:
                # Correct answer - send congratulations
                response = simple_math_pb2.MathResponse()
                response.congratulations = "Congratulations! Correct answer!"
                await websocket.send_bytes(response.SerializeToString())
                logger.info("Sent congratulations message")
                break
            else:
                # Wrong answer - send new problem
                problem = generate_math_problem()
                response = simple_math_pb2.MathResponse()
                response.new_problem.CopyFrom(problem)
                await websocket.send_bytes(response.SerializeToString())
                logger.info(f"Wrong answer. Sending new problem: {problem.a} + {problem.b}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")

@app.get("/")
def read_root():
    return {"message": "Protobuf service is running. POST to /add to use. WebSocket math game at /math."}
