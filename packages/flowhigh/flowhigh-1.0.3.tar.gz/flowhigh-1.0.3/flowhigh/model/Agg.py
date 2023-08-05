
from flowhigh.model.AggType import AggType
from flowhigh.model.CoordinateBlock import CoordinateBlock
from flowhigh.model.Searchable import Searchable


class Agg(CoordinateBlock, Searchable):
    filter_: list = []
    exprs: list = []
    type_: AggType = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class AggBuilder (object):
    construction: Agg

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Agg()
    
    def with_filter(self, filter_: list):
        child = filter_
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), filter_)):
            self.construction.add_child(node)
        self.construction.filter_ = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_exprs(self, exprs: list):
        child = exprs
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), exprs)):
            self.construction.add_child(node)
        self.construction.exprs = child
    
    def with_type(self, type_: AggType):
        child = type_
        self.construction.type_ = child

    def build(self):
        return self.construction
