from abc import ABC
from typing import List


class KeyboardLayout(ABC):
    top_row: List[str]
    home_row: List[str]
    bottom_row: List[str]


class Qwerty(KeyboardLayout):
    top_row = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
    home_row = ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";"]
    bottom_row = ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"]
