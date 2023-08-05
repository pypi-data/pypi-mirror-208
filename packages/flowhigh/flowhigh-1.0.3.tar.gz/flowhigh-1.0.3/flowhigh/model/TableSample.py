
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class TableSample(BaseExpr):
    sampleMethod: str = None
    seedType: str = None
    seed: str = None
    probability: str = None
    num: str = None
    sampleType: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class TableSampleBuilder (object):
    construction: TableSample

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = TableSample()
    
    def with_sampleMethod(self, sampleMethod: str):
        child = sampleMethod
        self.construction.sampleMethod = child
    
    def with_seed(self, seed: str):
        child = seed
        self.construction.seed = child
    
    def with_seedType(self, seedType: str):
        child = seedType
        self.construction.seedType = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_probability(self, probability: str):
        child = probability
        self.construction.probability = child
    
    def with_num(self, num: str):
        child = num
        self.construction.num = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_sampleType(self, sampleType: str):
        child = sampleType
        self.construction.sampleType = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
