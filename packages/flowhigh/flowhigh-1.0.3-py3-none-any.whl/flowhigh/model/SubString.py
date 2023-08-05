
from flowhigh.model.Expr import Expr
from flowhigh.model.BaseExpr import BaseExpr


class SubString(BaseExpr):
    string: Expr = None
    length: Expr = None
    position: Expr = None

    def __init__(self):
        super().__init__()



