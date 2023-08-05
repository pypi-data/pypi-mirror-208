
from flowhigh.model.Direction import Direction
from flowhigh.model.CoordinateBlock import CoordinateBlock
from flowhigh.model.Expr import Expr


class BaseExpr(CoordinateBlock, Expr):
    pos: str = None
    alias: str = None
    direction: Direction = None

    def __init__(self):
        super().__init__()



