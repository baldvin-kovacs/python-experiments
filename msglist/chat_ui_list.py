#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, GLib, Pango, GObject, Gio
from typing import List, Optional
import threading
import time
from msgs import Msgs


class Message(GObject.Object):
    """Message object for the list model."""
    
    def __init__(self, sender: str, content: str, timestamp: Optional[float] = None):
        super().__init__()
        self.sender = sender
        self.content = content
        self.timestamp = timestamp or time.time()
        self.is_own = sender == "You"


class MessageListModel(GObject.Object, Gio.ListModel):
    """Custom list model for chat messages."""
    
    def __init__(self):
        super().__init__()
        self._messages: List[Message] = []
    
    def do_get_item_type(self):
        return Message
    
    def do_get_n_items(self):
        return len(self._messages)
    
    def do_get_item(self, position):
        if 0 <= position < len(self._messages):
            return self._messages[position]
        return None
    
    def add_message(self, message: Message):
        """Add a message to the model and notify views."""
        position = len(self._messages)
        self._messages.append(message)
        self.items_changed(position, 0, 1)
    
    def clear(self):
        """Clear all messages."""
        count = len(self._messages)
        if count > 0:
            self._messages.clear()
            self.items_changed(0, count, 0)


class ChatUIList(Gtk.ApplicationWindow):
    """A chat-like interface using ListView with custom ListModel."""
    
    def __init__(self, app: Gtk.Application) -> None:
        super().__init__(application=app, title="Mock Chat UI (ListView)")
        self.set_default_size(800, 600)
        
        # Initialize message source and model
        self.msgs = Msgs(70, 12345)
        self.past_message_index = 0
        self.typing_messages: List[str] = []
        self.message_model = MessageListModel()
        
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
        
        # Scrolled window for past messages ListView
        past_scroll = Gtk.ScrolledWindow()
        past_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        past_scroll.set_size_request(-1, 200)
        
        # Create ListView with custom factory
        self.message_list_view = Gtk.ListView()
        self.message_list_view.set_model(Gtk.NoSelection(model=self.message_model))
        
        # Create factory for message widgets
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.on_factory_setup)
        factory.connect("bind", self.on_factory_bind)
        self.message_list_view.set_factory(factory)
        
        past_scroll.set_child(self.message_list_view)
        main_box.append(past_scroll)
        
        # Typing messages area (keeping TextView for simplicity)
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
        
        .message-list-item {
            margin: 4px 0;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def on_factory_setup(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem) -> None:
        """Setup the list item widget structure."""
        # Create a container for the message
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        container.get_style_context().add_class("message-list-item")
        
        # Create message box container
        message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        message_box.get_style_context().add_class("message-box")
        
        # Create sender label
        sender_label = Gtk.Label()
        sender_label.get_style_context().add_class("message-sender")
        message_box.append(sender_label)
        
        # Create message content label
        content_label = Gtk.Label()
        content_label.set_wrap(True)
        content_label.set_wrap_mode(Pango.WrapMode.WORD)
        content_label.get_style_context().add_class("message-content")
        message_box.append(content_label)
        
        container.append(message_box)
        list_item.set_child(container)
    
    def on_factory_bind(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem) -> None:
        """Bind data to the list item widget."""
        message = list_item.get_item()
        if not message:
            return
        
        container = list_item.get_child()
        message_box = container.get_first_child()
        sender_label = message_box.get_first_child()
        content_label = sender_label.get_next_sibling()
        
        # Update sender label
        sender_label.set_text(message.sender)
        sender_label.set_halign(Gtk.Align.START if not message.is_own else Gtk.Align.END)
        
        # Update content label
        content_label.set_text(message.content)
        content_label.set_halign(Gtk.Align.START if not message.is_own else Gtk.Align.END)
        content_label.set_xalign(0.0 if not message.is_own else 1.0)
        
        # Update message box styling
        if message.is_own:
            message_box.get_style_context().add_class("own")
        else:
            message_box.get_style_context().remove_class("own")
    
    def load_past_messages(self) -> None:
        """Load some initial past messages."""
        for i in range(5):  # Show first 5 messages as past messages
            message_text = self.msgs[i]
            sender = f"User {i % 3 + 1}"
            message = Message(sender, message_text)
            self.message_model.add_message(message)
            self.past_message_index = i + 1
    
    def add_past_message(self, sender: str, message_text: str) -> None:
        """Add a message to the past messages area."""
        message = Message(sender, message_text)
        self.message_model.add_message(message)
        
        # Auto-scroll to bottom
        def scroll_to_bottom():
            # Get the adjustment from the scrolled window
            scroll = self.message_list_view.get_parent()
            if isinstance(scroll, Gtk.ScrolledWindow):
                adj = scroll.get_vadjustment()
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


class ChatAppList(Gtk.Application):
    """Main application class."""
    
    def __init__(self) -> None:
        super().__init__(application_id="com.example.MockChatList")
        self.connect("activate", self.on_activate)
    
    def on_activate(self, app: Gtk.Application) -> None:
        """Create and show the main window."""
        window = ChatUIList(app)
        window.present()


def main() -> None:
    """Main entry point."""
    app = ChatAppList()
    app.run()


if __name__ == "__main__":
    main()