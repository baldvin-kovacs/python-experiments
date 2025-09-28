from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


class Broker():
    def __init__(self):
        self.num_clients = 0
    def register(self):
        self.num_clients += 1
        print(f"{self.num_clients=}",flush = True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.broker = Broker()
    print('[Server]: Broker initialized')
    yield
    print('[Server]: Shutting down...')

    

app = FastAPI(lifespan=lifespan)
@app.websocket("/socket")

async def websocket_endpoint(websocket: WebSocket):
    print('xxx',flush=True)
    await websocket.accept()
    print("[Server]: Client connected.")
    
    broker: Broker = websocket.app.state.broker
    broker.register()
    
    try:
        while True:
            data = await websocket.receive_text()
            for char in data:
                print(char,end='',flush=True)
    except:
        print("[Server]: Client disconnected")

#option 1: add global service 
#client should introduce itself + register func should then take a name 
