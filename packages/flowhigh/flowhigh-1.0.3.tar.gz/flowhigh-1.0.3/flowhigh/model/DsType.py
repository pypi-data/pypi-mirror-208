from enum import Enum


class DsType(Enum):
    cte = 1
    table = 2
    reference = 3
    parenthesis = 4
    view = 5
    root = 6
    anonymous = 7

