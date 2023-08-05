
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr
from flowhigh.model.TypeCast import TypeCast


class Current(BaseExpr, TypeCast):
    type_: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class CurrentBuilder (object):
    construction: Current

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Current()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_type(self, type_: str):
        child = type_
        self.construction.type_ = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
