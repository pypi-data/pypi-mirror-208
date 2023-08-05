
from flowhigh.model.Ds import Ds
from flowhigh.model.CoordinateBlock import CoordinateBlock


class Copy(CoordinateBlock):
    fromExp: list = []
    targetColumns: list = []
    pattern: str = None
    copyOptions: str = None
    ds: list = []
    selectElements: list = []
    into: Ds = None
    fromStage: Ds = None
    partition: list = []
    file: str = None
    fromQuery: Ds = None
    header: bool = None
    fileFormat: str = None
    validation: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class CopyBuilder (object):
    construction: Copy

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = Copy()
    
    def with_fromExp(self, fromExp: list):
        child = fromExp
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), fromExp)):
            self.construction.add_child(node)
        self.construction.fromExp = child
    
    def with_targetColumns(self, targetColumns: list):
        child = targetColumns
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), targetColumns)):
            self.construction.add_child(node)
        self.construction.targetColumns = child
    
    def with_pattern(self, pattern: str):
        child = pattern
        self.construction.pattern = child
    
    def with_copyOptions(self, copyOptions: str):
        child = copyOptions
        self.construction.copyOptions = child
    
    def with_ds(self, ds: list):
        child = ds
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), ds)):
            self.construction.add_child(node)
        self.construction.ds = child
    
    def with_selectElements(self, selectElements: list):
        child = selectElements
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), selectElements)):
            self.construction.add_child(node)
        self.construction.selectElements = child
    
    def with_fromStage(self, fromStage: Ds):
        child = fromStage
        if TreeNode in Ds.mro():
            self.construction.add_child(child)
        self.construction.fromStage = child
    
    def with_into(self, into: Ds):
        child = into
        if TreeNode in Ds.mro():
            self.construction.add_child(child)
        self.construction.into = child
    
    def with_file(self, file: str):
        child = file
        self.construction.file = child
    
    def with_partition(self, partition: list):
        child = partition
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), partition)):
            self.construction.add_child(node)
        self.construction.partition = child
    
    def with_fromQuery(self, fromQuery: Ds):
        child = fromQuery
        if TreeNode in Ds.mro():
            self.construction.add_child(child)
        self.construction.fromQuery = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_header(self, header: bool):
        child = header
        self.construction.header = child
    
    def with_validation(self, validation: str):
        child = validation
        self.construction.validation = child
    
    def with_fileFormat(self, fileFormat: str):
        child = fileFormat
        self.construction.fileFormat = child

    def build(self):
        return self.construction
