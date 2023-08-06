"""tty for mint shell, defined by OS
"""

import os
import sys
from typing import TextIO

TTY_SUPPORTED = False


class TTY:  # pyright: ignore
    """TTY to be used in the mint shell
    """

    fd: int = 0

    def __init__(self, stdin: TextIO = sys.stdin):
        self.fd = stdin.fileno()

    def setup(self):
        """Setup the TTY
        """
        pass

    def reset(self):
        """Reset the TTY to the original settings
        """
        pass

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, *args):
        del args
        self.reset()


if os.name != 'nt' and os.environ.get("SKIP_TTY", "false").lower() != "true":
    # termios and tty only supported for Unix versions that support Posix termios style tty I/O control
    import termios
    import tty

    TTY_SUPPORTED = True

    class TTY:  # pylint: disable=function-redefined
        """Unix TTY to be used in the mint shell
        """

        fd: int = 0
        old_settings = None

        def __init__(self, stdin: TextIO = sys.stdin):
            self.fd = stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)

        def setup(self, when=termios.TCSAFLUSH):
            # Only setup the TTY if we are in a TTY
            if not os.isatty(self.fd):
                return

            mode = termios.tcgetattr(self.fd)

            # See: https://man7.org/linux/man-pages/man3/termios.3.html
            mode[tty.LFLAG] &= ~(
                # Disable signals so they are sent through to MINT
                termios.ISIG |
                # Turn off "echo" so we don't see the characters we type
                # (they will come from STDOUT through MINT)
                termios.ECHO |
                # Turn off "canonical" mode so we can read single characters
                termios.ICANON)
            # Disable translation of carriabe return to newline
            # This fixes issues with "Enter" not being read properly in some applications
            mode[tty.IFLAG] &= ~termios.ICRNL
            # Set minimum number of characters to read to 0
            # This fixes issues with some characters (e.g. Arrow keys) getting buffered improperly
            mode[tty.CC][termios.VMIN] = 0
            mode[tty.CC][termios.VTIME] = 0

            # Set the mode
            termios.tcsetattr(self.fd, when, mode)

        def reset(self):
            if self.old_settings:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

        def __enter__(self):
            self.setup()
            return self

        def __exit__(self, *args):
            del args
            self.reset()
