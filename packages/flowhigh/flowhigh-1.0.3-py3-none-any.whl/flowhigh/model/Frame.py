
from flowhigh.model.BetweenType import BetweenType
from flowhigh.model.Direction import Direction
from flowhigh.model.ExprExprCollectionHolder import ExprExprCollectionHolder
from flowhigh.model.TypeCast import TypeCast


class Frame(ExprExprCollectionHolder, TypeCast):
    low_val: str = None
    hi_rel: str = None
    exprs: list = []
    low_rel: str = None
    type_: BetweenType = None
    hi_val: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class FrameBuilder (object):
    construction: Frame

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Frame()
    
    def with_low_val(self, low_val: str):
        child = low_val
        self.construction.low_val = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_hi_rel(self, hi_rel: str):
        child = hi_rel
        self.construction.hi_rel = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_exprs(self, exprs: list):
        child = exprs
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), exprs)):
            self.construction.add_child(node)
        self.construction.exprs = child
    
    def with_low_rel(self, low_rel: str):
        child = low_rel
        self.construction.low_rel = child
    
    def with_type(self, type_: BetweenType):
        child = type_
        self.construction.type_ = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child
    
    def with_hi_val(self, hi_val: str):
        child = hi_val
        self.construction.hi_val = child

    def build(self):
        return self.construction
