
from flowhigh.model.TreeNode import TreeNode


class AntiPatterns(TreeNode):
    antiPattern: list = []

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class AntiPatternsBuilder (object):
    construction: AntiPatterns

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = AntiPatterns()
    
    def with_antiPattern(self, antiPattern: list):
        child = antiPattern
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), antiPattern)):
            self.construction.add_child(node)
        self.construction.antiPattern = child

    def build(self):
        return self.construction
