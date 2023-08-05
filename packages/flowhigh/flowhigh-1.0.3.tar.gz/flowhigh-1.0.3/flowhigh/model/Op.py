
from flowhigh.model.OpType import OpType
from flowhigh.model.Direction import Direction
from flowhigh.model.ExprExprCollectionHolder import ExprExprCollectionHolder
from flowhigh.model.TypeCast import TypeCast


class Op(ExprExprCollectionHolder, TypeCast):
    exprs: list = []
    type_: OpType = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class OpBuilder (object):
    construction: Op

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Op()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_exprs(self, exprs: list):
        child = exprs
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), exprs)):
            self.construction.add_child(node)
        self.construction.exprs = child
    
    def with_type(self, type_: OpType):
        child = type_
        self.construction.type_ = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
