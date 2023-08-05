
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class MatchRecognize(BaseExpr):
    partitionBy: str = None
    measures: str = None
    pattern: str = None
    define: str = None
    orderBy: str = None
    rowMatchAction: str = None
    rowMatchCondition: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class MatchRecognizeBuilder (object):
    construction: MatchRecognize

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = MatchRecognize()
    
    def with_partitionBy(self, partitionBy: str):
        child = partitionBy
        self.construction.partitionBy = child
    
    def with_measures(self, measures: str):
        child = measures
        self.construction.measures = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_define(self, define: str):
        child = define
        self.construction.define = child
    
    def with_pattern(self, pattern: str):
        child = pattern
        self.construction.pattern = child
    
    def with_rowMatchAction(self, rowMatchAction: str):
        child = rowMatchAction
        self.construction.rowMatchAction = child
    
    def with_orderBy(self, orderBy: str):
        child = orderBy
        self.construction.orderBy = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_rowMatchCondition(self, rowMatchCondition: str):
        child = rowMatchCondition
        self.construction.rowMatchCondition = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
