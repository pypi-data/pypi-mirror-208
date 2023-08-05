
from flowhigh.model.Direction import Direction
from flowhigh.model.BaseExpr import BaseExpr


class Insert(BaseExpr):
    isElse: bool = None
    ctes: list = []
    elseIntos: list = []
    insert_type: str = None
    conditionalIntos: list = []
    overwrite: bool = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class InsertBuilder (object):
    construction: Insert

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Insert()
    
    def with_ctes(self, ctes: list):
        child = ctes
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), ctes)):
            self.construction.add_child(node)
        self.construction.ctes = child
    
    def with_isElse(self, isElse: bool):
        child = isElse
        self.construction.isElse = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_elseIntos(self, elseIntos: list):
        child = elseIntos
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), elseIntos)):
            self.construction.add_child(node)
        self.construction.elseIntos = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_insert_type(self, insert_type: str):
        child = insert_type
        self.construction.insert_type = child
    
    def with_conditionalIntos(self, conditionalIntos: list):
        child = conditionalIntos
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), conditionalIntos)):
            self.construction.add_child(node)
        self.construction.conditionalIntos = child
    
    def with_overwrite(self, overwrite: bool):
        child = overwrite
        self.construction.overwrite = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
