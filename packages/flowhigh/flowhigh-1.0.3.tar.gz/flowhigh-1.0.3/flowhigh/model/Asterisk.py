
from flowhigh.model.Direction import Direction
from flowhigh.model.ExprExprCollectionHolder import ExprExprCollectionHolder
from flowhigh.model.ReferencableExpr import ReferencableExpr
from flowhigh.model.TreeNode import TreeNode


class Asterisk(ExprExprCollectionHolder, ReferencableExpr, TreeNode):
    refsch: str = None
    fullref: str = None
    refdb: str = None
    refds: str = None
    refatt: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class AsteriskBuilder (object):
    construction: Asterisk

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Asterisk()
    
    def with_refsch(self, refsch: str):
        child = refsch
        self.construction.refsch = child
    
    def with_fullref(self, fullref: str):
        child = fullref
        self.construction.fullref = child
    
    def with_refdb(self, refdb: str):
        child = refdb
        self.construction.refdb = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_refds(self, refds: str):
        child = refds
        self.construction.refds = child
    
    def with_refatt(self, refatt: str):
        child = refatt
        self.construction.refatt = child
    
    def with_exprs(self, exprs: list):
        child = exprs
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), exprs)):
            self.construction.add_child(node)
        self.construction.exprs = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
