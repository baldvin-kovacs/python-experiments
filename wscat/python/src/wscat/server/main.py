import logging
from fastapi import FastAPI, Request, Response
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

@app.get("/")
def read_root():
    return {"message": "Protobuf service is running. POST to /add to use."}
