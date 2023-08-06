import curses
import sys

from . import tutorial


def main() -> None:
    """Entry point for the application script."""
    try:
        curses.wrapper(tutorial.start)
    except KeyboardInterrupt:
        sys.exit(0)
