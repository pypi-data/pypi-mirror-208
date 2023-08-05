
from flowhigh.model.CoordinateBlock import CoordinateBlock


class CreateStage(CoordinateBlock):
    with_: bool = None
    stageName: str = None
    comments: str = None
    directoryParam: str = None
    location: str = None
    tag: list = []
    fileFormat: str = None
    copyOptions: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class CreateStageBuilder (object):
    construction: CreateStage

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = CreateStage()
    
    def with_with(self, with_: bool):
        child = with_
        self.construction.with_ = child
    
    def with_comments(self, comments: str):
        child = comments
        self.construction.comments = child
    
    def with_stageName(self, stageName: str):
        child = stageName
        self.construction.stageName = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_directoryParam(self, directoryParam: str):
        child = directoryParam
        self.construction.directoryParam = child
    
    def with_location(self, location: str):
        child = location
        self.construction.location = child
    
    def with_tag(self, tag: list):
        child = tag
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), tag)):
            self.construction.add_child(node)
        self.construction.tag = child
    
    def with_copyOptions(self, copyOptions: str):
        child = copyOptions
        self.construction.copyOptions = child
    
    def with_fileFormat(self, fileFormat: str):
        child = fileFormat
        self.construction.fileFormat = child

    def build(self):
        return self.construction
