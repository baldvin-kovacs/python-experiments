from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
@app.websocket("/socket")
async def websocket_endpoint(websocket: WebSocket):
    print('xxx',flush=True)
    await websocket.accept()
    print("[Server]: Client connected.")
    try:
        while True:
            data = await websocket.receive_text()
            for char in data:
                print(char,end='',flush=True)
    except:
        print("[Server]: Client disconnected")