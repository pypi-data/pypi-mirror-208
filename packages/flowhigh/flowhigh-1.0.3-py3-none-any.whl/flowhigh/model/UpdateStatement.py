
from flowhigh.model.Statement import Statement
from flowhigh.model.TypeCast import TypeCast


class UpdateStatement(Statement, TypeCast):
    type_: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class UpdateStatementBuilder (object):
    construction: UpdateStatement

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = UpdateStatement()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_merge(self, merge: list):
        child = merge
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), merge)):
            self.construction.add_child(node)
        self.construction.merge = child
    
    def with_create(self, create: list):
        child = create
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), create)):
            self.construction.add_child(node)
        self.construction.create = child
    
    def with_antiPatterns(self, antiPatterns: list):
        child = antiPatterns
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), antiPatterns)):
            self.construction.add_child(node)
        self.construction.antiPatterns = child
    
    def with_createStage(self, createStage: list):
        child = createStage
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), createStage)):
            self.construction.add_child(node)
        self.construction.createStage = child
    
    def with_insert(self, insert: list):
        child = insert
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), insert)):
            self.construction.add_child(node)
        self.construction.insert = child
    
    def with_update(self, update: list):
        child = update
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), update)):
            self.construction.add_child(node)
        self.construction.update = child
    
    def with_rawInput(self, rawInput: str):
        child = rawInput
        self.construction.rawInput = child
    
    def with_copy(self, copy: list):
        child = copy
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), copy)):
            self.construction.add_child(node)
        self.construction.copy = child
    
    def with_createView(self, createView: list):
        child = createView
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), createView)):
            self.construction.add_child(node)
        self.construction.createView = child
    
    def with_type(self, type_: str):
        child = type_
        self.construction.type_ = child
    
    def with_delete(self, delete: list):
        child = delete
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), delete)):
            self.construction.add_child(node)
        self.construction.delete = child
    
    def with_ds(self, ds: list):
        child = ds
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), ds)):
            self.construction.add_child(node)
        self.construction.ds = child

    def build(self):
        return self.construction
