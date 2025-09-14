import asyncio
import websockets
import sys
from wscat.server import simple_math_pb2

async def handle_initial_problem(websocket, data):
    """Handle initial math problem from server."""
    problem = simple_math_pb2.MathProblem()
    problem.ParseFromString(data)
    print(f"Problem: {problem.a} + {problem.b} = ?")
    
    answer = int(input("Your answer: "))
    
    # Send solution
    solution = simple_math_pb2.MathSolution(answer=answer)
    await websocket.send(solution.SerializeToString())

async def handle_response(websocket, data):
    """Handle MathResponse from server (congratulations or new problem)."""
    response = simple_math_pb2.MathResponse()
    response.ParseFromString(data)
    
    if response.HasField('congratulations'):
        print(response.congratulations)
        return True

    if response.HasField('new_problem'):
        print(f"Wrong! New problem: {response.new_problem.a} + {response.new_problem.b} = ?")
        answer = int(input("Your answer: "))
        # Send solution
        solution = simple_math_pb2.MathSolution(answer=answer)
        await websocket.send(solution.SerializeToString())

    return False
    
async def game_client():
    uri = "ws://127.0.0.1:8000/math"
    
    try:
        async with websockets.connect(uri) as websocket:
            data = await websocket.recv()
            await handle_initial_problem(websocket, data)
            while True:
              data = await websocket.recv()
              if await handle_response(websocket, data):
                break
                        
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by server")

def main():
    asyncio.run(game_client())

if __name__ == "__main__":
    main()
