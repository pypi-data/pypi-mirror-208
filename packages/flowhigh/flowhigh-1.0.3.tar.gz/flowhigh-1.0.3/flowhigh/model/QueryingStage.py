
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class QueryingStage(BaseExpr):
    pattern: str = None
    location: str = None
    fileFormat: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class QueryingStageBuilder (object):
    construction: QueryingStage

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = QueryingStage()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_pattern(self, pattern: str):
        child = pattern
        self.construction.pattern = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_location(self, location: str):
        child = location
        self.construction.location = child
    
    def with_fileFormat(self, fileFormat: str):
        child = fileFormat
        self.construction.fileFormat = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
