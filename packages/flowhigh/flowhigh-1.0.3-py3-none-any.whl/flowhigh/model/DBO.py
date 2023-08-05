
from flowhigh.model.DBOType import DBOType
from flowhigh.model.DBOSubType import DBOSubType
from flowhigh.model.TreeNode import TreeNode


class DBO(TreeNode):
    dbo: list = []
    name: str = None
    subType: DBOSubType = None
    oid: str = None
    href: str = None
    type_: DBOType = None
    poidArr: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class DBOBuilder (object):
    construction: DBO

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = DBO()
    
    def with_dbo(self, dbo: list):
        child = dbo
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), dbo)):
            self.construction.add_child(node)
        self.construction.dbo = child
    
    def with_name(self, name: str):
        child = name
        self.construction.name = child
    
    def with_subType(self, subType: DBOSubType):
        child = subType
        self.construction.subType = child
    
    def with_href(self, href: str):
        child = href
        self.construction.href = child
    
    def with_oid(self, oid: str):
        child = oid
        self.construction.oid = child
    
    def with_type(self, type_: DBOType):
        child = type_
        self.construction.type_ = child
    
    def with_poidArr(self, poidArr: str):
        child = poidArr
        self.construction.poidArr = child

    def build(self):
        return self.construction
