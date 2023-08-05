
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class Merge(BaseExpr):
    ds: list = []

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class MergeBuilder (object):
    construction: Merge

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Merge()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_ds(self, ds: list):
        child = ds
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), ds)):
            self.construction.add_child(node)
        self.construction.ds = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
