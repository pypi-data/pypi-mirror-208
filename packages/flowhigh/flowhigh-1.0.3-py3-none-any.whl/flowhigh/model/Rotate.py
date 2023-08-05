
from flowhigh.model.Expr import Expr
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class Rotate(BaseExpr):
    nameColumn: str = None
    valueColumn: str = None
    pivotColumn: Expr = None
    columnList: list = []
    type_: str = None
    columnAlias: list = []
    aggregate: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class RotateBuilder (object):
    construction: Rotate

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Rotate()
    
    def with_nameColumn(self, nameColumn: str):
        child = nameColumn
        self.construction.nameColumn = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_valueColumn(self, valueColumn: str):
        child = valueColumn
        self.construction.valueColumn = child
    
    def with_columnList(self, columnList: list):
        child = columnList
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), columnList)):
            self.construction.add_child(node)
        self.construction.columnList = child
    
    def with_pivotColumn(self, pivotColumn: Expr):
        child = pivotColumn
        if TreeNode in Expr.mro():
            self.construction.add_child(child)
        self.construction.pivotColumn = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_type(self, type_: str):
        child = type_
        self.construction.type_ = child
    
    def with_columnAlias(self, columnAlias: list):
        child = columnAlias
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), columnAlias)):
            self.construction.add_child(node)
        self.construction.columnAlias = child
    
    def with_aggregate(self, aggregate: str):
        child = aggregate
        self.construction.aggregate = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
