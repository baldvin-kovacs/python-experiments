#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Pango
from typing import List, Optional
import threading
import time
from msgs import Msgs


class ChatUI(Gtk.ApplicationWindow):
    """A chat-like interface with three areas: past messages, typing messages, and input."""
    
    def __init__(self, app: Gtk.Application) -> None:
        super().__init__(application=app, title="Mock Chat UI")
        self.set_default_size(800, 600)
        
        # Initialize message source
        self.msgs = Msgs(70, 12345)
        self.past_message_index = 0
        self.typing_messages: List[str] = []
        
        self.setup_ui()
        self.simulate_typing()
    
    def setup_ui(self) -> None:
        """Set up the main UI layout."""
        # Setup CSS for rounded message boxes
        self.setup_css()
        
        # Main vertical box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.set_child(main_box)
        
        # Past messages area
        past_label = Gtk.Label(label="Past Messages")
        past_label.set_markup("<b>Past Messages</b>")
        past_label.set_halign(Gtk.Align.START)
        main_box.append(past_label)
        
        # Scrolled window for past messages
        past_scroll = Gtk.ScrolledWindow()
        past_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        past_scroll.set_size_request(-1, 200)
        
        # Container for message boxes
        self.past_messages_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.past_messages_box.set_margin_top(10)
        self.past_messages_box.set_margin_bottom(10)
        self.past_messages_box.set_margin_start(10)
        self.past_messages_box.set_margin_end(10)
        past_scroll.set_child(self.past_messages_box)
        main_box.append(past_scroll)
        
        # Typing messages area
        typing_label = Gtk.Label(label="Currently Typing...")
        typing_label.set_markup("<b>Currently Typing...</b>")
        typing_label.set_halign(Gtk.Align.START)
        main_box.append(typing_label)
        
        # Scrolled window for typing messages
        typing_scroll = Gtk.ScrolledWindow()
        typing_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        typing_scroll.set_size_request(-1, 150)
        
        self.typing_messages_view = Gtk.TextView()
        self.typing_messages_view.set_editable(False)
        self.typing_messages_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.typing_messages_buffer = self.typing_messages_view.get_buffer()
        
        # Style typing messages with italics
        italic_tag = self.typing_messages_buffer.create_tag("italic")
        italic_tag.set_property("style", Pango.Style.ITALIC)
        italic_tag.set_property("foreground", "#666666")
        
        typing_scroll.set_child(self.typing_messages_view)
        main_box.append(typing_scroll)
        
        # Input area
        input_label = Gtk.Label(label="Your message:")
        input_label.set_markup("<b>Your message:</b>")
        input_label.set_halign(Gtk.Align.START)
        main_box.append(input_label)
        
        # Input area with scrolled text view
        input_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Scrolled window for input text view
        input_scroll = Gtk.ScrolledWindow()
        input_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        input_scroll.set_size_request(-1, 80)  # About 3 lines high
        
        self.message_text_view = Gtk.TextView()
        self.message_text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.message_buffer = self.message_text_view.get_buffer()
        
        # Set placeholder text using buffer
        self.message_buffer.set_text("Type your message here...")
        
        # Connect to focus events to handle placeholder
        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect("enter", self.on_input_focus_in)
        focus_controller.connect("leave", self.on_input_focus_out)
        self.message_text_view.add_controller(focus_controller)
        
        input_scroll.set_child(self.message_text_view)
        input_container.append(input_scroll)
        
        # Send button below the text area
        send_button = Gtk.Button(label="Send")
        send_button.connect("clicked", self.on_send_message)
        send_button.set_halign(Gtk.Align.END)
        input_container.append(send_button)
        
        main_box.append(input_container)
        
        # Load initial past messages
        self.load_past_messages()
    
    def setup_css(self) -> None:
        """Set up CSS styling for rounded message boxes."""
        css_provider = Gtk.CssProvider()
        css = """
        .message-box {
            background-color: #e3f2fd;
            border-radius: 12px;
            padding: 8px 12px;
            margin: 2px 40px 2px 2px;
        }
        
        .message-box.own {
            background-color: #c8e6c9;
            margin: 2px 2px 2px 40px;
        }
        
        .message-sender {
            font-weight: bold;
            font-size: 0.85em;
            color: #666;
            margin-bottom: 2px;
        }
        
        .message-content {
            color: #333;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def load_past_messages(self) -> None:
        """Load some initial past messages."""
        for i in range(5):  # Show first 5 messages as past messages
            message = self.msgs[i]
            self.add_past_message(f"User {i % 3 + 1}", message)
            self.past_message_index = i + 1
    
    def add_past_message(self, sender: str, message: str) -> None:
        """Add a message to the past messages area."""
        # Create message box container
        message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        message_box.get_style_context().add_class("message-box")
        
        # Add "own" class for messages from "You"
        if sender == "You":
            message_box.get_style_context().add_class("own")
        
        # Create sender label
        sender_label = Gtk.Label(label=sender)
        sender_label.set_halign(Gtk.Align.START if sender != "You" else Gtk.Align.END)
        sender_label.get_style_context().add_class("message-sender")
        message_box.append(sender_label)
        
        # Create message content label
        content_label = Gtk.Label(label=message)
        content_label.set_wrap(True)
        content_label.set_wrap_mode(Pango.WrapMode.WORD)
        content_label.set_halign(Gtk.Align.START if sender != "You" else Gtk.Align.END)
        content_label.set_xalign(0.0 if sender != "You" else 1.0)
        content_label.get_style_context().add_class("message-content")
        message_box.append(content_label)
        
        # Add to past messages box
        self.past_messages_box.append(message_box)
        
        # Auto-scroll to bottom
        def scroll_to_bottom():
            adj = self.past_messages_box.get_parent().get_vadjustment()
            adj.set_value(adj.get_upper() - adj.get_page_size())
        
        GLib.idle_add(scroll_to_bottom)
    
    def update_typing_messages(self) -> None:
        """Update the typing messages display."""
        self.typing_messages_buffer.set_text("")
        
        for i, message in enumerate(self.typing_messages):
            if i > 0:
                end_iter = self.typing_messages_buffer.get_end_iter()
                self.typing_messages_buffer.insert(end_iter, "\n")
            
            end_iter = self.typing_messages_buffer.get_end_iter()
            user_num = (i % 3) + 1
            self.typing_messages_buffer.insert_with_tags_by_name(
                end_iter, f"User {user_num} is typing: {message}...", "italic"
            )
    
    def simulate_typing(self) -> None:
        """Simulate other users typing messages in a separate thread."""
        def typing_simulation() -> None:
            while True:
                # Add a new typing message
                if len(self.typing_messages) < 3 and self.past_message_index < len(self.msgs):
                    new_message = self.msgs[self.past_message_index]
                    # Show partial message (simulate typing)
                    words = new_message.split()
                    partial_message = ' '.join(words[:len(words)//2 + 1])
                    self.typing_messages.append(partial_message)
                    self.past_message_index += 1
                    
                    GLib.idle_add(self.update_typing_messages)
                
                time.sleep(2.0)
                
                # Complete a typing message and move it to past messages
                if self.typing_messages:
                    completed_message = self.typing_messages.pop(0)
                    # Get the full message
                    full_message = self.msgs[self.past_message_index - len(self.typing_messages) - 1]
                    user_num = (len(self.typing_messages) % 3) + 1
                    
                    GLib.idle_add(self.add_past_message, f"User {user_num}", full_message)
                    GLib.idle_add(self.update_typing_messages)
                
                time.sleep(3.0)
        
        thread = threading.Thread(target=typing_simulation, daemon=True)
        thread.start()
    
    def on_input_focus_in(self, controller: Gtk.EventControllerFocus) -> None:
        """Handle focus in event for input text view."""
        text = self.message_buffer.get_text(
            self.message_buffer.get_start_iter(),
            self.message_buffer.get_end_iter(),
            False
        )
        if text == "Type your message here...":
            self.message_buffer.set_text("")
    
    def on_input_focus_out(self, controller: Gtk.EventControllerFocus) -> None:
        """Handle focus out event for input text view."""
        text = self.message_buffer.get_text(
            self.message_buffer.get_start_iter(),
            self.message_buffer.get_end_iter(),
            False
        ).strip()
        if not text:
            self.message_buffer.set_text("Type your message here...")
    
    def on_send_message(self, widget: Optional[Gtk.Widget] = None) -> None:
        """Handle sending a message."""
        text = self.message_buffer.get_text(
            self.message_buffer.get_start_iter(),
            self.message_buffer.get_end_iter(),
            False
        ).strip()
        if text and text != "Type your message here...":
            self.add_past_message("You", text)
            self.message_buffer.set_text("")


class ChatApp(Gtk.Application):
    """Main application class."""
    
    def __init__(self) -> None:
        super().__init__(application_id="com.example.MockChat")
        self.connect("activate", self.on_activate)
    
    def on_activate(self, app: Gtk.Application) -> None:
        """Create and show the main window."""
        window = ChatUI(app)
        window.present()


def main() -> None:
    """Main entry point."""
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()