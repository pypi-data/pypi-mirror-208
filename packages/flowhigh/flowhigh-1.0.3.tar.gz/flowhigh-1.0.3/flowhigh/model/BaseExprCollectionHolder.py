
from flowhigh.model.CoordinateBlock import CoordinateBlock
from flowhigh.model.ExprCollectionHolder import ExprCollectionHolder


class BaseExprCollectionHolder(CoordinateBlock, ExprCollectionHolder):
    pos: str = None
    exprs: list = []

    def __init__(self):
        super().__init__()



