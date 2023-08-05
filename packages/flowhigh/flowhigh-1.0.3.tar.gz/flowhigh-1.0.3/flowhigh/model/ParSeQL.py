
from flowhigh.model.ParSeQLStatus import ParSeQLStatus
from flowhigh.model.DBOHier import DBOHier
from flowhigh.model.CoordinateBlock import CoordinateBlock


class ParSeQL(CoordinateBlock):
    namespace: str = None
    statement: list = []
    location: str = None
    error: list = []
    DBOHier_: DBOHier = None
    version: str = None
    status: ParSeQLStatus = None
    ts: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class ParSeQLBuilder (object):
    construction: ParSeQL

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = ParSeQL()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_statement(self, statement: list):
        child = statement
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), statement)):
            self.construction.add_child(node)
        self.construction.statement = child
    
    def with_namespace(self, namespace: str):
        child = namespace
        self.construction.namespace = child
    
    def with_location(self, location: str):
        child = location
        self.construction.location = child
    
    def with_DBOHier(self, DBOHier_: DBOHier):
        child = DBOHier_
        if TreeNode in DBOHier.mro():
            self.construction.add_child(child)
        self.construction.DBOHier_ = child
    
    def with_error(self, error: list):
        child = error
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), error)):
            self.construction.add_child(node)
        self.construction.error = child
    
    def with_version(self, version: str):
        child = version
        self.construction.version = child
    
    def with_ts(self, ts: str):
        child = ts
        self.construction.ts = child
    
    def with_status(self, status: ParSeQLStatus):
        child = status
        self.construction.status = child

    def build(self):
        return self.construction
