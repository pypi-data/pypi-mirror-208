
from flowhigh.model.Ds import Ds
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr
from flowhigh.model.ReferencableExpr import ReferencableExpr


class Create(BaseExpr, ReferencableExpr):
    refsch: str = None
    refdb: str = None
    scope: str = None
    refds: str = None
    query: Ds = None
    columnDef: list = []
    type_: str = None
    clusterBy: list = []
    ds: list = []

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class CreateBuilder (object):
    construction: Create

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Create()
    
    def with_refsch(self, refsch: str):
        child = refsch
        self.construction.refsch = child
    
    def with_refdb(self, refdb: str):
        child = refdb
        self.construction.refdb = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_scope(self, scope: str):
        child = scope
        self.construction.scope = child
    
    def with_refds(self, refds: str):
        child = refds
        self.construction.refds = child
    
    def with_query(self, query: Ds):
        child = query
        if TreeNode in Ds.mro():
            self.construction.add_child(child)
        self.construction.query = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_columnDef(self, columnDef: list):
        child = columnDef
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), columnDef)):
            self.construction.add_child(node)
        self.construction.columnDef = child
    
    def with_type(self, type_: str):
        child = type_
        self.construction.type_ = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child
    
    def with_clusterBy(self, clusterBy: list):
        child = clusterBy
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), clusterBy)):
            self.construction.add_child(node)
        self.construction.clusterBy = child
    
    def with_ds(self, ds: list):
        child = ds
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), ds)):
            self.construction.add_child(node)
        self.construction.ds = child

    def build(self):
        return self.construction
