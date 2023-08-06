from enum import Enum, auto


class Command(Enum):
    RIGHTARC = auto(0)
    LEFTARC = auto(1)
    SHIFT = auto(2)
    REDUCE = auto(3)
