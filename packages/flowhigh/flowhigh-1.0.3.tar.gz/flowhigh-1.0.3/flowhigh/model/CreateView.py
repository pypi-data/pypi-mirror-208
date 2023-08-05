
from flowhigh.model.Ds import Ds
from flowhigh.model.CoordinateBlock import CoordinateBlock


class CreateView(CoordinateBlock):
    columns: list = []
    query: Ds = None
    replace: bool = None
    notExists: bool = None
    dataset: Ds = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class CreateViewBuilder (object):
    construction: CreateView

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = CreateView()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_columns(self, columns: list):
        child = columns
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), columns)):
            self.construction.add_child(node)
        self.construction.columns = child
    
    def with_query(self, query: Ds):
        child = query
        if TreeNode in Ds.mro():
            self.construction.add_child(child)
        self.construction.query = child
    
    def with_notExists(self, notExists: bool):
        child = notExists
        self.construction.notExists = child
    
    def with_replace(self, replace: bool):
        child = replace
        self.construction.replace = child
    
    def with_dataset(self, dataset: Ds):
        child = dataset
        if TreeNode in Ds.mro():
            self.construction.add_child(child)
        self.construction.dataset = child

    def build(self):
        return self.construction
