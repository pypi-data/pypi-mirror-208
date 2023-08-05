
from flowhigh.model.TreeNode import TreeNode


class DBOHier(TreeNode):
    dbo: list = []

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class DBOHierBuilder (object):
    construction: DBOHier

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = DBOHier()
    
    def with_dbo(self, dbo: list):
        child = dbo
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), dbo)):
            self.construction.add_child(node)
        self.construction.dbo = child

    def build(self):
        return self.construction
