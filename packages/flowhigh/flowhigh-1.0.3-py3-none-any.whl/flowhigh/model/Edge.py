
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class Edge(BaseExpr):
    generator: str = None
    exprs: list = []
    type_: str = None
    columnAlias: list = []

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class EdgeBuilder (object):
    construction: Edge

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Edge()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_exprs(self, exprs: list):
        child = exprs
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), exprs)):
            self.construction.add_child(node)
        self.construction.exprs = child
    
    def with_generator(self, generator: str):
        child = generator
        self.construction.generator = child
    
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
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
