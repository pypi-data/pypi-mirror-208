import curses

from .colors import Colors
from .layouts import Qwerty
from .levels import Level


class Level1(Level):
    top_row_keys = set()
    home_row_keys = {3, 6}
    bottom_row_keys = set()
    description = "Home row: index fingers."


class Level2(Level):
    top_row_keys = set()
    home_row_keys = {2, 7}
    bottom_row_keys = set()
    description = "Home row: middle fingers."


class Level3(Level):
    top_row_keys = set()
    home_row_keys = {2, 3, 6, 7}
    bottom_row_keys = set()
    description = "Comprehensive - Home row: index and middle fingers."


class Level4(Level):
    top_row_keys = set()
    home_row_keys = {1, 8}
    bottom_row_keys = set()
    description = "Home row: ring fingers."


class Level5(Level):
    top_row_keys = set()
    home_row_keys = {1, 2, 3, 6, 7, 8}
    bottom_row_keys = set()
    description = "Comprehensive - Home row: index, middle and ring fingers."


class Level6(Level):
    top_row_keys = set()
    home_row_keys = {0, 9}
    bottom_row_keys = set()
    description = "Home row: pinky fingers."


class Level7(Level):
    top_row_keys = set()
    home_row_keys = {0, 1, 2, 3, 6, 7, 8, 9}
    bottom_row_keys = set()
    description = "Comprehensive - Home row: all fingers."


def init_colors() -> Colors:
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    return Colors(curses.color_pair(1), curses.color_pair(2))


tutorial = [Level1, Level2, Level3, Level4, Level5, Level6, Level7]


def start(screen: curses.window) -> None:
    layout = Qwerty()
    colors = init_colors()
    for level in tutorial:
        level.play(screen, layout, colors)
