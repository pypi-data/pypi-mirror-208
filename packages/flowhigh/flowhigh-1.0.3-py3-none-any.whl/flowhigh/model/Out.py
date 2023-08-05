
from flowhigh.model.BaseExprCollectionHolder import BaseExprCollectionHolder
from flowhigh.model.TypeCast import TypeCast


class Out(BaseExprCollectionHolder, TypeCast):
    type_: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class OutBuilder (object):
    construction: Out

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Out()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_exprs(self, exprs: list):
        child = exprs
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), exprs)):
            self.construction.add_child(node)
        self.construction.exprs = child
    
    def with_type(self, type_: str):
        child = type_
        self.construction.type_ = child

    def build(self):
        return self.construction
