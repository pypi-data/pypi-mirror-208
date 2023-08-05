
from flowhigh.model.JoinType import JoinType
from flowhigh.model.JoinSubType import JoinSubType
from flowhigh.model.DefinedAsType import DefinedAsType
from flowhigh.model.Ds import Ds
from flowhigh.model.Expr import Expr
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class Join(BaseExpr):
    op: Expr = None
    definedAs: DefinedAsType = None
    subType: JoinSubType = None
    type_: JoinType = None
    ds: Ds = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class JoinBuilder (object):
    construction: Join

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Join()
    
    def with_op(self, op: Expr):
        child = op
        if TreeNode in Expr.mro():
            self.construction.add_child(child)
        self.construction.op = child
    
    def with_definedAs(self, definedAs: DefinedAsType):
        child = definedAs
        self.construction.definedAs = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_subType(self, subType: JoinSubType):
        child = subType
        self.construction.subType = child
    
    def with_type(self, type_: JoinType):
        child = type_
        self.construction.type_ = child
    
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
