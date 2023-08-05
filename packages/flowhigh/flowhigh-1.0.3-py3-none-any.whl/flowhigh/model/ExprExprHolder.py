
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExprHolder import BaseExprHolder
from flowhigh.model.Expr import Expr


class ExprExprHolder(BaseExprHolder, Expr):
    alias: str = None
    expr: Expr = None
    direction: Direction = None

    def __init__(self):
        super().__init__()



