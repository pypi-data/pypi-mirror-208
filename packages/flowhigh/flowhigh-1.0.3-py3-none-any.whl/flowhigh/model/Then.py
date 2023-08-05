
from flowhigh.model.Direction import Direction
from flowhigh.model.Expr import Expr
from flowhigh.model.ExprExprHolder import ExprExprHolder


class Then(ExprExprHolder):

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class ThenBuilder (object):
    construction: Then

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Then()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_expr(self, expr: Expr):
        child = expr
        if TreeNode in Expr.mro():
            self.construction.add_child(child)
        self.construction.expr = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
