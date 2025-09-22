from blessed import Terminal
import textwrap
import argparse

term = Terminal()

def print_in_box(row, col, width, height, text):
    wrapped_lines = textwrap.wrap(text.strip(), width=width)
    wrapped_lines = wrapped_lines[:height]

    with term.location():  
        for i, line in enumerate(wrapped_lines):
            with term.location(x=col, y=row + i):
                print(line.ljust(width), end='')

def main():
    parser = argparse.ArgumentParser(description='Display text in a terminal box.')
    parser.add_argument('row', type=int, help='Starting row position')
    parser.add_argument('col', type=int, help='Starting column position')
    parser.add_argument('width', type=int, help='Width of the box')
    parser.add_argument('height', type=int, help='Height of the box')
    parser.add_argument('filename', type=str, help='Path to the text file')

    args = parser.parse_args()

    try:
        with open(args.filename, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"File not found: {args.filename}")
        return

    print(term.clear)
    print_in_box(row=args.row, col=args.col, width=args.width, height=args.height, text=text)

if __name__ == '__main__':
    main()

#if __name__ == '__main__':
#    print(term.clear)
#    print_in_box(row=5, col=10, width=30, height=4, text="""
#I was born in a water moon. Some people, especially its inhabitants, called it a planet, but as it was only a little over two hundred kilometres in diameter “moon’ seems the more accurate term.
#""")