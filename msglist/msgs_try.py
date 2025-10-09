import sys
from msgs import Msgs

def format_message_bubble(message, index):
    max_width = 60
    lines = []
    words = message.split()
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= max_width - 4:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    bubble_width = max(len(line) for line in lines) + 4
    
    print("┌" + "─" * (bubble_width - 2) + "┐")
    for line in lines:
        padding = bubble_width - len(line) - 4
        print(f"│ {line}{' ' * padding} │")
    print("└" + "─" * (bubble_width - 2) + "┘")
    print()

ms = Msgs(7, int(sys.argv[1]))

print(f"Total messages: {len(ms)}")
print()

for i, s in enumerate(ms):
    format_message_bubble(s, i)
