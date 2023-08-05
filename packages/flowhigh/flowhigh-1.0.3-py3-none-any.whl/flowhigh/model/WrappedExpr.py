
from flowhigh.model.Expr import Expr
from flowhigh.model.TreeNode import TreeNode


class WrappedExpr(TreeNode):
    expr: Expr = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class WrappedExprBuilder (object):
    construction: WrappedExpr

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = WrappedExpr()
    
    def with_expr(self, expr: Expr):
        child = expr
        if TreeNode in Expr.mro():
            self.construction.add_child(child)
        self.construction.expr = child

    def build(self):
        return self.construction
