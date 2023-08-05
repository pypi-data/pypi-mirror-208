
from flowhigh.model.PageType import PageType
from flowhigh.model.Const import Const
from flowhigh.model.CoordinateBlock import CoordinateBlock
from flowhigh.model.TypeCast import TypeCast


class Page(CoordinateBlock, TypeCast):
    type_: PageType = None
    value: Const = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class PageBuilder (object):
    construction: Page

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Page()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_type(self, type_: PageType):
        child = type_
        self.construction.type_ = child
    
    def with_value(self, value: Const):
        child = value
        if TreeNode in Const.mro():
            self.construction.add_child(child)
        self.construction.value = child

    def build(self):
        return self.construction
