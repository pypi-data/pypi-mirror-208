
from flowhigh.model.Expr import Expr
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class Position(BaseExpr):
    string: Expr = None
    subString: Expr = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class PositionBuilder (object):
    construction: Position

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Position()
    
    def with_string(self, string: Expr):
        child = string
        if TreeNode in Expr.mro():
            self.construction.add_child(child)
        self.construction.string = child
    
    def with_subString(self, subString: Expr):
        child = subString
        if TreeNode in Expr.mro():
            self.construction.add_child(child)
        self.construction.subString = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
