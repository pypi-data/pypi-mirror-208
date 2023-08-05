
from flowhigh.model.FilterType import FilterType
from flowhigh.model.Op import Op
from flowhigh.model.CoordinateBlock import CoordinateBlock


class Filter(CoordinateBlock):
    op: Op = None
    type_: FilterType = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class FilterBuilder (object):
    construction: Filter

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Filter()
    
    def with_op(self, op: Op):
        child = op
        if TreeNode in Op.mro():
            self.construction.add_child(child)
        self.construction.op = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_type(self, type_: FilterType):
        child = type_
        self.construction.type_ = child

    def build(self):
        return self.construction
