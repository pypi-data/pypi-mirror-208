
from flowhigh.model.CoordinateBlock import CoordinateBlock
from flowhigh.model.Named import Named


class ColumnDef(CoordinateBlock, Named):
    precision: int = None
    name: str = None
    scale: int = None
    type_: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class ColumnDefBuilder (object):
    construction: ColumnDef

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = ColumnDef()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_precision(self, precision: int):
        child = precision
        self.construction.precision = child
    
    def with_name(self, name: str):
        child = name
        self.construction.name = child
    
    def with_scale(self, scale: int):
        child = scale
        self.construction.scale = child
    
    def with_type(self, type_: str):
        child = type_
        self.construction.type_ = child

    def build(self):
        return self.construction
