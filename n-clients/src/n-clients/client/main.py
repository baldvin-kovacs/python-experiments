import asyncio
import websockets
import sys
import tty
import termios


async def send_chars(name):
    uri = "ws://127.0.0.1:8000/socket"
    async with websockets.connect(uri) as websocket:
        print(f"[CLIENT {name}] Connected: Start typing...")
        await websocket.send(f"[Name]{name}: ")

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
    if len(sys.argv) < 2:
        print("Usage: python src/n-clients/client/main.py <name>")
        sys.exit(1)

    client_name = sys.argv[1]
    asyncio.run(send_chars(client_name))