
from flowhigh.model.CoordinateBlock import CoordinateBlock


class Error(CoordinateBlock):
    message: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class ErrorBuilder (object):
    construction: Error

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Error()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_message(self, message: str):
        child = message
        self.construction.message = child

    def build(self):
        return self.construction
