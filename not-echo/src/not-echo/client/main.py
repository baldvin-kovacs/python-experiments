import asyncio
import termios
import websockets
import tty
import sys

async def send_chars()
    uri = "ws://localhost:8000/socket"
    async with websockets.connect(uri) as websocket:
     print('[CLIENT] Connected: Start typing...')
     fd = sys.stdin.fileno()
