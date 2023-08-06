import itertools

from types import FunctionType

from vecdb.collections.field import Field


def list_methods(cls):
    return set(x for x, y in cls.__dict__.items() if isinstance(y, (FunctionType, classmethod, staticmethod)))


def list_parent_methods(cls):
    return set(itertools.chain.from_iterable(list_methods(c).union(list_parent_methods(c)) for c in cls.__bases__))


def list_subclass_methods(cls, is_narrow: bool = False):
    methods = list_methods(cls)
    if is_narrow:
        parentMethods = list_parent_methods(cls)
        return set(cls for cls in methods if not (cls in parentMethods))
    else:
        return methods


class TestField:
    FIELD_METHODS = list_subclass_methods(Field)
