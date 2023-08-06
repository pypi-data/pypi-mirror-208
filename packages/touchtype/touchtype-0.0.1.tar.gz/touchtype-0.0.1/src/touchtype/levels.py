from abc import ABC
from collections import deque
from itertools import cycle, product
from typing import Set

import curses

from .colors import Colors
from .layouts import KeyboardLayout


class Level(ABC):
    top_row_keys: Set[int]
    home_row_keys: Set[int]
    bottom_row_keys: Set[int]
    description: str

    @classmethod
    def play(cls, screen: curses.window, layout: KeyboardLayout, colors: Colors) -> None:
        cls.draw_status_bar(screen)
        cls.draw_keyboard(screen, layout)
        for queue in cls.generate_character_combos(layout):
            screen.move(1, 0)
            screen.clrtoeol()
            screen.addstr("".join(queue))
            screen.move(1, 0)
            screen.refresh()
            while queue:
                expected = queue.popleft()
                typed = screen.getch()
                if typed == ord("\n"):
                    return
                color = colors.green if chr(typed) == expected else colors.red
                screen.echochar(expected, color)

    @classmethod
    def draw_status_bar(cls, screen: curses.window) -> None:
        window = screen.subwin(1, curses.COLS - 1, 0, 0)
        window.addstr(f"{cls.description}", curses.A_REVERSE)

    @classmethod
    def draw_keyboard(cls, screen: curses.window, layout: KeyboardLayout) -> None:
        window = screen.subwin(5, 39, 2, 0)
        top = (
            x if i in cls.top_row_keys else " " for i, x in enumerate(layout.top_row)
        )
        home = (
            x if i in cls.home_row_keys else " " for i, x in enumerate(layout.home_row)
        )
        bot = (
            x if i in cls.bottom_row_keys else " "
            for i, x in enumerate(layout.bottom_row)
        )
        window.move(1, 1)
        window.addstr(" | ".join(top))
        window.move(2, 1)
        window.addstr(" | ".join(home))
        window.move(3, 1)
        window.addstr(" | ".join(bot))
        window.border()

    @classmethod
    def generate_character_combos(cls, layout: KeyboardLayout):
        available_characters = set()
        for char in cls.top_row_keys:
            available_characters.add(layout.top_row[char])
        for char in cls.home_row_keys:
            available_characters.add(layout.home_row[char])
        for char in cls.bottom_row_keys:
            available_characters.add(layout.bottom_row[char])

        one_char_combos = product(available_characters)
        for combo in one_char_combos:
            queue = deque()
            text = " ".join("".join(combo) for _ in range(4))
            for char in text:
                queue.append(char)
            yield queue

        two_char_combos = product(available_characters, repeat=2)
        for combo in two_char_combos:
            queue = deque()
            text = " ".join("".join(combo) for _ in range(4))
            for char in text:
                queue.append(char)
            yield queue

        three_char_combos = product(available_characters, repeat=3)
        for combo in three_char_combos:
            queue = deque()
            text = " ".join("".join(combo) for _ in range(4))
            for char in text:
                queue.append(char)
            yield queue

        four_char_combos = product(available_characters, repeat=4)
        for combo in cycle(four_char_combos):
            queue = deque()
            text = " ".join("".join(combo) for _ in range(4))
            for char in text:
                queue.append(char)
            yield queue
