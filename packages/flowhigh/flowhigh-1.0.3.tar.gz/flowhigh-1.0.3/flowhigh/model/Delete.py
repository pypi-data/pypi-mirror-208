
from flowhigh.model.Ds import Ds
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class Delete(BaseExpr):
    ds: Ds = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class DeleteBuilder (object):
    construction: Delete

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Delete()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_ds(self, ds: Ds):
        child = ds
        if TreeNode in Ds.mro():
            self.construction.add_child(child)
        self.construction.ds = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
