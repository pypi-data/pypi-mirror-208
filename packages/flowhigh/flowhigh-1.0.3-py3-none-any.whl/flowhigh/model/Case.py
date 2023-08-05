
from flowhigh.model.WrappedExpr import WrappedExpr
from flowhigh.model.Else import Else
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class Case(BaseExpr):
    Else: Else = None
    expr: WrappedExpr = None
    when: list = []

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class CaseBuilder (object):
    construction: Case

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Case()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_Else(self, Else: Else):
        child = Else
        if TreeNode in Else.mro():
            self.construction.add_child(child)
        self.construction.Else = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_expr(self, expr: WrappedExpr):
        child = expr
        if TreeNode in WrappedExpr.mro():
            self.construction.add_child(child)
        self.construction.expr = child
    
    def with_when(self, when: list):
        child = when
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), when)):
            self.construction.add_child(node)
        self.construction.when = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
