
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExprCollectionHolder import BaseExprCollectionHolder
from flowhigh.model.Expr import Expr


class ExprExprCollectionHolder(BaseExprCollectionHolder, Expr):
    pos: str = None
    alias: str = None
    exprs: list = []
    direction: Direction = None

    def __init__(self):
        super().__init__()



