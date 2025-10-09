#!/usr/bin/env python3

import asyncio
import websockets
import json
from typing import Set

# Store connected clients
connected_clients: Set[websockets.WebSocketServerProtocol] = set()

async def handle_client(websocket: websockets.WebSocketServerProtocol):
    """Handle a new client connection."""
    global connected_clients
    print(f"Client connected from {websocket.remote_address}")
    connected_clients.add(websocket)
    
    try:
        async for message in websocket:
            try:
                # Parse the message
                data = json.loads(message)
                char = data.get('char', '')
                
                print(f"Received '{char}' from {websocket.remote_address}")
                
                # Broadcast to all other clients (except sender)
                if connected_clients:
                    # Create response message
                    response = json.dumps({'char': char})
                    
                    # Send to all clients except the sender
                    disconnected = set()
                    for client in connected_clients:
                        if client != websocket:
                            try:
                                await client.send(response)
                            except websockets.exceptions.ConnectionClosed:
                                disconnected.add(client)
                    
                    # Remove disconnected clients
                    connected_clients -= disconnected
                    
            except json.JSONDecodeError:
                print(f"Invalid JSON from {websocket.remote_address}: {message}")
            except Exception as e:
                print(f"Error handling message from {websocket.remote_address}: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket.remote_address} disconnected")
    finally:
        connected_clients.discard(websocket)

async def main():
    """Start the websocket server."""
    print("Starting WebSocket server on ws://localhost:8765")
    print("Waiting for clients to connect...")
    
    async with websockets.serve(handle_client, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutting down...")