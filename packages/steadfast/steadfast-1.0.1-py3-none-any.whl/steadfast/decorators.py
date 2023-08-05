# -*- coding: utf-8 -*-

import inspect

from .core import *
from .common import *
from .archive import *
from .types import isnamedtuple

__all__ = ['decl_serializable']


def create_verb_method(verb, delegate):

    if verb not in CLASS_VERBS:

        def verb_method_impl(self):
            if type(self) is not delegate.type:
                raise DerivedClassNotSerializable()

            return delegate.handle(self, verb, ArchiveContext())

    else:

        def verb_method_impl(cls, operand):
            if cls is not delegate.type:
                raise DerivedClassNotSerializable()

            return delegate.handle(operand, verb, ArchiveContext())

        verb_method_impl = classmethod(verb_method_impl)

    return verb_method_impl


def verb_name(verb):
    return str(verb.name).lower()


# noinspection PyShadowingBuiltins
def inherited_operators(type, registry):

    super_types = list(reversed(type.__mro__))

    for type in super_types:

        delegate = registry.lookup_value_for_type(type, no_base_types=True)

        if delegate is None:
            continue

        yield from delegate.declared_operators  # noqa


# noinspection PyShadowingBuiltins
def build_composite_operator(type, declared_operators, registry, inherit_operators=True):

    tmp = []

    if inherit_operators:
        for operator in inherited_operators(type, registry):
            operator = operator.copy()

            if isinstance(operator, TypeAttachableMixin):
                operator.type = type

            tmp.append(operator)

    tmp.extend(declared_operators)

    operator = CompositeOperator(parent_operator=tmp[0], child_operators=tmp[1:])
    return operator


class DecoratorTypeDelegate(TypeDelegate):

    # noinspection PyShadowingBuiltins
    def __init__(self, type, composite_operator, declared_operators, type_identifier=None):
        super(DecoratorTypeDelegate, self).__init__(type, composite_operator, type_identifier)
        self.declared_operators = declared_operators


def decl_serializable(*args, **kwargs):

    def decorator(cls):

        declared_operators = []

        for arg in args:
            if isinstance(arg, Operator):

                if isinstance(arg, TypeAttachableMixin):
                    arg.type = cls

                declared_operators.append(arg)

        inherit_operators = kwargs.get('inherit_operators', False)
        type_identifier = kwargs.get('type_identifier', None)
        delegate_registry = kwargs.get('delegate_registry', DELEGATE_REGISTRY)

        composite_operator = build_composite_operator(cls, declared_operators, delegate_registry, inherit_operators=inherit_operators)

        delegate = DecoratorTypeDelegate(cls, composite_operator, declared_operators, type_identifier=type_identifier)
        # setattr(cls, SERIALIZABLE_ATTRIBUTE, delegate)

        if isinstance(composite_operator.parent_operator, DelegateAttachableMixin):
            composite_operator.parent_operator.delegate = delegate

        for operator in composite_operator.child_operators:
            if isinstance(operator, DelegateAttachableMixin):
                operator.delegate = delegate

        delegate_registry.register_value_for_type(cls, delegate)
        delegate_registry.register_alias_for_type(cls, delegate.type_identifier)

        for verb in Mode:

            method_name = verb_name(verb)
            verb_method = cls.__dict__.get(method_name, None)

            if verb_method is None:
                setattr(cls, method_name, create_verb_method(verb, delegate))
            elif not inspect.isfunction(verb_method):
                raise ExpectedVerbToBeMethod()

        return cls

    if isinstance(args[0], type) and len(args) == 1 and len(kwargs) == 0:
        cls_arg = args[0]

        # noinspection PyUnusedLocal
        args = []

        if isnamedtuple(cls_arg):
            args.append(SaveInitArguments())

        return decorator(cls_arg)
    else:
        return decorator

