
from flowhigh.model.Sort import Sort
from flowhigh.model.Frame import Frame
from flowhigh.model.Ds import Ds
from flowhigh.model.DsType import DsType
from flowhigh.model.DsSubType import DsSubType
from flowhigh.model.DsAction import DsAction
from flowhigh.model.Out import Out
from flowhigh.model.In import In
from flowhigh.model.MatchRecognize import MatchRecognize
from flowhigh.model.TableSample import TableSample
from flowhigh.model.Direction import Direction
from flowhigh.model.Ordered import Ordered


class TableFunc(Ds, Ordered):
    names: list = []
    partition: list = []
    options: list = []
    sort: Sort = None
    tableFuncType: str = None
    frame: Frame = None
    subQuery: Ds = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class TableFuncBuilder (object):
    construction: TableFunc

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = TableFunc()
    
    def with_type(self, type_: DsType):
        child = type_
        self.construction.type_ = child
    
    def with_modifiers(self, modifiers: list):
        child = modifiers
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), modifiers)):
            self.construction.add_child(node)
        self.construction.modifiers = child
    
    def with_out(self, out: Out):
        child = out
        if TreeNode in Out.mro():
            self.construction.add_child(child)
        self.construction.out = child
    
    def with_partition(self, partition: list):
        child = partition
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), partition)):
            self.construction.add_child(node)
        self.construction.partition = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_refds(self, refds: str):
        child = refds
        self.construction.refds = child
    
    def with_options(self, options: list):
        child = options
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), options)):
            self.construction.add_child(node)
        self.construction.options = child
    
    def with_action(self, action: DsAction):
        child = action
        self.construction.action = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_refTo(self, refTo: str):
        child = refTo
        self.construction.refTo = child
    
    def with_tableFuncType(self, tableFuncType: str):
        child = tableFuncType
        self.construction.tableFuncType = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child
    
    def with_refsch(self, refsch: str):
        child = refsch
        self.construction.refsch = child
    
    def with_fullref(self, fullref: str):
        child = fullref
        self.construction.fullref = child
    
    def with_refdb(self, refdb: str):
        child = refdb
        self.construction.refdb = child
    
    def with_in(self, in_: In):
        child = in_
        if TreeNode in In.mro():
            self.construction.add_child(child)
        self.construction.in_ = child
    
    def with_matchRecognize(self, matchRecognize: MatchRecognize):
        child = matchRecognize
        if TreeNode in MatchRecognize.mro():
            self.construction.add_child(child)
        self.construction.matchRecognize = child
    
    def with_setOp(self, setOp: list):
        child = setOp
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), setOp)):
            self.construction.add_child(node)
        self.construction.setOp = child
    
    def with_sort(self, sort: Sort):
        child = sort
        if TreeNode in Sort.mro():
            self.construction.add_child(child)
        self.construction.sort = child
    
    def with_subQuery(self, subQuery: Ds):
        child = subQuery
        if TreeNode in Ds.mro():
            self.construction.add_child(child)
        self.construction.subQuery = child
    
    def with_tableSample(self, tableSample: TableSample):
        child = tableSample
        if TreeNode in TableSample.mro():
            self.construction.add_child(child)
        self.construction.tableSample = child
    
    def with_names(self, names: list):
        child = names
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), names)):
            self.construction.add_child(node)
        self.construction.names = child
    
    def with_name(self, name: str):
        child = name
        self.construction.name = child
    
    def with_subType(self, subType: DsSubType):
        child = subType
        self.construction.subType = child
    
    def with_dboref(self, dboref: str):
        child = dboref
        self.construction.dboref = child
    
    def with_frame(self, frame: Frame):
        child = frame
        if TreeNode in Frame.mro():
            self.construction.add_child(child)
        self.construction.frame = child

    def build(self):
        return self.construction
