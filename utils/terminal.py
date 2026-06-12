import sys
import termios
import tty


class KEYS:
    QUIT_KEYS  = ["q", "\x03"]  # q + ctrl-c
    LEFT_KEYS  = ["\x1b[C"]     # left arrow
    RIGHT_KEYS = ["\x1b[D"]     # right arrow


def read_key() -> str:
    """
    Reads a key directly from the terminal in
    raw mode (i.e., no buffering, echos, etc.)

    Prevents users from having to press enter after
    key presses for the program to process

    NOTE:
        1. Saves terminal settings
        2. Switches to raw mode (no buffering, etc.)
        3. Reads 1 char
        4. If arrow key escape sequence, read 2 more chars
        5. Restores original terminal settings (always)
        6. Returns key
    """
    fd = sys.stdin.fileno()
    old_attr = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)  # read in 1 byte

        if char == "\x1b":  # escape sequence for arrow keys
            char += sys.stdin.read(2)  # read in 2 more bytes

            # NOTE: arrow keys return 3 chars in a sequence, not one:
            # left   = \x1b[C
            # right  = \x1b[D

        return char
    finally:
        # restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attr)


def render(render: str, erase_lines: int = 0):
    out = ""
    if erase_lines:
        out += f"\x1b[{erase_lines}A\x1b[0J"

    out += render
    sys.stdout.write(out)
    sys.stdout.flush()  # immediately flush buffer
