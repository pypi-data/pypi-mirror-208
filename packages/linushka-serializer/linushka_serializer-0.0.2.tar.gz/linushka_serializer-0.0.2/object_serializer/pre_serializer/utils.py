import inspect
import types
from enum import StrEnum, auto

PRIMITIVES = (int, str, bool, float, types.NoneType)


class TYPE(StrEnum):
    BYTES = auto()
    FUNCTION = auto()
    CELL = auto()
    CLASS = auto()
    ITERATOR = auto()
    CODE = auto()
    OBJECT = auto()
    MODULE = auto()
    TUPLE = auto()
    SET = auto()
    PROPERTY = auto()
    GENERATOR = auto()
    MAP = auto()
    FILTER = auto()

UNSERIALIZABLE_DUNDER = (
    "__mro__",
    "__base__",
    "__basicsize__",
    "__class__",
    "__dictoffset__",
    "__name__",
    "__qualname__",
    "__text_signature__",
    "__itemsize__",
    "__flags__",
    "__weakrefoffset__",
    "__objclass__",
)

UNSERIALIZABLE_TYPES = (
    types.WrapperDescriptorType,
    types.MethodDescriptorType,
    types.BuiltinFunctionType,
    types.MappingProxyType,
    types.GetSetDescriptorType,
)

UNSERIALIZABLE_CODE_TYPES = (
    "co_positions",
    "co_lines",
    "co_exceptiontable",
    "co_lnotab",
)


def is_iterable(obj):
    return hasattr(obj, "__iter__") and hasattr(obj, "__next__") and callable(obj.__iter__) and obj.__iter__() is obj


class _C:
    @property
    def value(self, val):
        pass


PropertyType = type(_C.__dict__["value"])


def get_class_by_method(meth):
    cls = getattr(
        inspect.getmodule(meth),
        meth.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0],
        None,
    )
    if isinstance(cls, type):
        return cls
