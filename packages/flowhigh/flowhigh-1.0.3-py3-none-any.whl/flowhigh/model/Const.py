
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class Const(BaseExpr):
    value: object = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class ConstBuilder (object):
    construction: Const

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Const()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_value(self, value: object):
        child = value
        if TreeNode in object.mro():
            self.construction.add_child(child)
        self.construction.value = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
