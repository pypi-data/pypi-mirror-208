
from flowhigh.model.FuncType import FuncType
from flowhigh.model.FuncSubType import FuncSubType
from flowhigh.model.Quantifier import Quantifier
from flowhigh.model.Sort import Sort
from flowhigh.model.WrappedExpr import WrappedExpr
from flowhigh.model.Frame import Frame
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr
from flowhigh.model.Named import Named
from flowhigh.model.TypeCast import TypeCast


class Func(BaseExpr, Named, TypeCast):
    partition: list = []
    name: str = None
    withinGroup: Sort = None
    exprs: list = []
    subType: FuncSubType = None
    expr: WrappedExpr = None
    sort: Sort = None
    type_: FuncType = None
    quantifier: Quantifier = None
    frame: Frame = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class FuncBuilder (object):
    construction: Func

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Func()
    
    def with_partition(self, partition: list):
        child = partition
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), partition)):
            self.construction.add_child(node)
        self.construction.partition = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_withinGroup(self, withinGroup: Sort):
        child = withinGroup
        if TreeNode in Sort.mro():
            self.construction.add_child(child)
        self.construction.withinGroup = child
    
    def with_name(self, name: str):
        child = name
        self.construction.name = child
    
    def with_exprs(self, exprs: list):
        child = exprs
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), exprs)):
            self.construction.add_child(node)
        self.construction.exprs = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_expr(self, expr: WrappedExpr):
        child = expr
        if TreeNode in WrappedExpr.mro():
            self.construction.add_child(child)
        self.construction.expr = child
    
    def with_subType(self, subType: FuncSubType):
        child = subType
        self.construction.subType = child
    
    def with_sort(self, sort: Sort):
        child = sort
        if TreeNode in Sort.mro():
            self.construction.add_child(child)
        self.construction.sort = child
    
    def with_quantifier(self, quantifier: Quantifier):
        child = quantifier
        self.construction.quantifier = child
    
    def with_type(self, type_: FuncType):
        child = type_
        self.construction.type_ = child
    
    def with_frame(self, frame: Frame):
        child = frame
        if TreeNode in Frame.mro():
            self.construction.add_child(child)
        self.construction.frame = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
