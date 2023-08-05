from enum import Enum


class JoinType(Enum):
    outer = 1
    inner = 2
    cross = 3
    nonansi = 4

