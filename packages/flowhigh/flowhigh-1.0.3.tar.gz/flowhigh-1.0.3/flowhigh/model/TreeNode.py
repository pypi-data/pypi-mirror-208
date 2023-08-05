import weakref
from weakref import WeakSet


class RegistryBase(object):
    ENTITY_REGISTRY = WeakSet()

    def __new__(cls, *args, **kwargs):
        pass

    @classmethod
    def get_registry(cls):
        return cls.ENTITY_REGISTRY

    @classmethod
    def push_to_registry(cls, instance):
        cls.ENTITY_REGISTRY.add(instance)

    @classmethod
    def search(cls, node_id):
        return next(filter(lambda x: x.get_id() == node_id, cls.get_registry()), None)


class AutoIncrementID(object):
    id: int = 0

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'id'):
            cls = super(AutoIncrementID, cls).__new__(cls)
        cls.id = cls.id + 1
        return cls.id


class TreeNode(object):
    _id: int
    _parent: weakref = None
    _children: WeakSet

    def __init__(self):
        self._id = AutoIncrementID()
        self._children = WeakSet()
        RegistryBase.push_to_registry(self)

    def get_id(self):
        return self._id

    def get_children(self) -> WeakSet:
        return self._children

    def get_parent(self):
        return self._parent

    def add_child(self, child) -> None:
        self._children.add(child)
        child._parent = weakref.proxy(self)

    def accept(self):
        pass

