# -*- coding: utf-8 -*-

__all__ = ["TypeRegistry", "isnamedtuple"]


class TypeRegistry(object):

    def __init__(self):
        self.type_map = dict()
        self.type_aliases = dict()

    def lookup_value_for_type(self, type_object, default=None, no_base_types=False):

        for t in type_object.__mro__:
            if t in self.type_map:
                return self.type_map[t]

            if no_base_types:
                break

        return default

    def register_value_for_type(self, type_object, value):
        self.type_map[type_object] = value

    def delete_value_for_type(self, type_object):
        return self.type_map.pop(type_object)

    def lookup_value_for_alias(self, alias, default=None, no_base_types=False):
        type_object = self.lookup_type_for_alias(alias, None)
        return self.lookup_value_for_type(type_object, default, no_base_types)

    def register_value_for_alias(self, alias, value):
        type_object = self.lookup_type_for_alias(alias, None)
        self.register_value_for_type(type_object, value)

    def delete_value_for_alias(self, alias):
        type_object = self.lookup_type_for_alias(alias, None)
        return self.type_map.pop(type_object)

    def lookup_type_for_alias(self, alias, default=None):
        return self.type_aliases.get(alias, default)

    def register_alias_for_type(self, type_object, alias):
        self.type_aliases[alias] = type_object

    def delete_alias(self, alias):
        return self.type_aliases.pop(alias)


def isnamedtuple(operand):

    operand_type = type(operand)

    if operand_type is type:
        operand_type = operand

    is_namedtuple = False

    while True:

        if not issubclass(operand_type, tuple):
            break

        fields = getattr(operand_type, '_fields', None)

        if fields is None:
            break

        if not isinstance(fields, tuple):
            break

        if any(not isinstance(name, str) for name in fields):
            break

        is_namedtuple = True
        break

    return is_namedtuple
