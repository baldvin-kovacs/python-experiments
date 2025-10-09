#!/usr/bin/env python3

import gi
gi.require_version('Soup', '3.0')
gi.require_version('GLib', '2.0')
gi.require_version('Gio', '2.0')
from gi.repository import Soup, GLib, GObject, Gio
import json
import sys
import termios
import tty
import select

class WebSocketClient:
    """WebSocket client using libsoup."""
    
    def __init__(self, uri: str):
        self.uri = uri
        self.session = Soup.Session()
        self.websocket = None
        self.main_loop = GLib.MainLoop()
        
    def connect(self):
        """Connect to the WebSocket server."""
        print(f"Connecting to {self.uri}...")
        
        # Create WebSocket connection
        message = Soup.Message.new("GET", self.uri)
        self.session.websocket_connect_async(
            message, 
            None, 
            [], 
            0, 
            Gio.Cancellable(),
            self.on_websocket_connected,
            None
        )
    
    def on_websocket_connected(self, session, result, user_data):
        """Handle WebSocket connection result."""
        try:
            self.websocket = session.websocket_connect_finish(result)
            print("Connected! Start typing...")
            
            # Connect to message signal
            self.websocket.connect("message", self.on_message_received)
            self.websocket.connect("closed", self.on_websocket_closed)
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.main_loop.quit()
    
    def on_message_received(self, websocket, type, message):
        """Handle incoming WebSocket message."""
        if type == Soup.WebsocketDataType.TEXT:
            try:
                data = json.loads(message.get_data().decode('utf-8'))
                char = data.get('char', '')
                
                # Print received character to terminal
                print(char, end='', flush=True)
                
            except json.JSONDecodeError:
                pass
    
    def on_websocket_closed(self, websocket):
        """Handle WebSocket connection closed."""
        print("\nWebSocket connection closed.")
        self.main_loop.quit()
    
    def send_character(self, char):
        """Send a character to the server."""
        if self.websocket:
            message = json.dumps({'char': char})
            self.websocket.send_text(message)
    
    def run(self):
        """Run the client."""
        # Set up terminal for raw input
        self.setup_terminal()
        
        # Connect to server
        self.connect()
        
        # Add stdin to GLib main loop
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_stdin_data)
        
        # Run the main loop
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.restore_terminal()
    
    def setup_terminal(self):
        """Set up terminal for raw input."""
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
    
    def restore_terminal(self):
        """Restore terminal settings."""
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def on_stdin_data(self, source, condition):
        """Handle data available on stdin."""
        if condition & GLib.IO_IN:
            char = sys.stdin.read(1)
            
            # Handle Ctrl+C
            if ord(char) == 3:  # Ctrl+C
                self.main_loop.quit()
                return False
            
            # Send character to server
            self.send_character(char)
            
            # Echo locally
            print(char, end='', flush=True)
        
        return True  # Keep watching

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        uri = sys.argv[1]
    else:
        uri = "ws://localhost:8765"
    
    client = WebSocketClient(uri)
    client.run()

if __name__ == "__main__":
    main()