import dataclasses
from dataclasses import dataclass
from typing import Literal

CORE_TYPES = Literal["int", "float", "str", "bool"]


class MetaType(type):
    """register supported types in metasys"""

    TYPE_REGISTRY = {}

    def __new__(mcs, cls_name, bases, cls_dict):
        cls = super().__new__(mcs, cls_name, bases, cls_dict)
        mcs.TYPE_REGISTRY[cls_name] = cls
        return cls

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MetaTypeBase(metaclass=MetaType):
    pass


class IntType(MetaTypeBase):
    pass


class FloatType(MetaTypeBase):
    pass


class FileType(MetaTypeBase):
    pass


class StringType(MetaTypeBase):
    pass


print(MetaType.TYPE_REGISTRY)


@dataclass
class MetaField:
    """how to describe an attribute of a class"""

    name: str = dataclasses.field(init=False)
    type: CORE_TYPES = dataclasses.field()


class MetaModel(type):
    pass


class MetaRule(type):
    pass


class MetaSys(type):
    """act as a model factory"""

    def __new__(mcs, cls_name, bases, cls_dict):
        return super().__new__(mcs, cls_name, bases, cls_dict)


class MetaBase(metaclass=MetaSys):
    pass
