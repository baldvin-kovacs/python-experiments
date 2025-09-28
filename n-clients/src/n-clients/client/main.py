import asyncio
import websockets
import sys
import tty
import termios


async def send_chars():
    uri = "ws://127.0.0.1:8000/socket"
    async with websockets.connect(uri) as websocket:
        print("[CLIENT] Connected: Start typing...")

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                char = sys.stdin.read(1)
                if char == '\x03':
                    break
                print(char, end='', flush=True)
                await websocket.send(char)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
if __name__ == '__main__':
    asyncio.run(send_chars())