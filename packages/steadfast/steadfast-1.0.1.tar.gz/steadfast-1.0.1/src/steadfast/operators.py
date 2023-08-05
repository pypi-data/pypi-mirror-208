# -*- coding: utf-8 -*-

import typing as tp
from types import SimpleNamespace, GeneratorType
from collections.abc import Iterator

from .core import *
from .common import *

# from .types import TypeRegistry
# from .identifiers import dot_identifier_for_type

__all__ = ['AtomicOperator', 'StrOperator', 'IntOperator', 'FloatOperator', 'BytesOperator', 'SingletonOperator',
           'TupleOperator', 'Field', 'DictOperator', 'DictModifierOperator', 'ListOperator', 'PolymorphicOperator',
           'ReferenceType', 'ReferenceOperator',
           'setup_builtin_delegates']


@log_operator
class AtomicOperator(Operator):

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def spread(self, task: Task) -> tp.Iterable[Task]:
        task.result = task.operand
        return ()


class StrOperator(AtomicOperator):
    pass


class IntOperator(AtomicOperator):
    pass


class FloatOperator(AtomicOperator):
    pass


class NoneOperator(AtomicOperator):
    pass


class BytesOperator(Operator):

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def spread(self, task: Task) -> tp.Iterable[Task]:

        if task.verb is Mode.PACK:

            task.result = {
                "type:": "bytes"
            }

        return ()

    def gather(self, task: Task):
        pass


class SingletonOperator(Operator):

    def __init__(self, type_identifier, singleton_provider):
        self.type_identifier = type_identifier
        self.singleton_provider = singleton_provider

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def spread(self, task: Task) -> tp.Iterable[Task]:

        if task.verb is Mode.PACK:

            singleton = self.singleton_provider()

            if task.operand is not singleton:
                raise NotSerializable

            task.result = self.type_identifier

        if task.verb is Mode.UNPACK:

            if task.operand != self.type_identifier:
                raise UnknownType

            task.result = self.singleton_provider()

        return ()


class Field:

    def __init__(self, value, operator, result_container):
        self.value = value
        self.operator = operator
        self.result_container = result_container


@log_operator
class DictOperator(Operator):

    TYPE_KEYWORD = 'type'
    ASSIGN_KEYWORD = 'assign'
    RESERVED_KEYWORDS = {TYPE_KEYWORD, ASSIGN_KEYWORD}

    ESCAPE_CHAR = '\\'

    def __init__(self, type_identifier="builtins.dict", require_type_identifier=False):
        super(DictOperator, self).__init__()
        self.pack_as_value = False
        self.type_identifier = type_identifier
        self.require_type_identifier = require_type_identifier

    def escape_field_name(self, name):

        if name.startswith(self.ESCAPE_CHAR) or name in self.RESERVED_KEYWORDS:
            return self.ESCAPE_CHAR + name

        return name

    def unescape_field_name(self, name):

        if name.startswith(self.ESCAPE_CHAR):
            return name[len(self.ESCAPE_CHAR):]

        return name

    # noinspection PyMethodMayBeStatic
    def pack_raw_dict(self, fields, metadata):

        result = dict(metadata)

        for name, value in fields.items():
            name = self.unescape_field_name(name)
            fields[name] = value

        return result

    # noinspection PyMethodMayBeStatic
    def unpack_raw_dict(self, operand):

        if not isinstance(operand, dict):
            raise ExpectedDictOperand()

        if self.TYPE_KEYWORD in operand:

            type_identifier = operand[self.TYPE_KEYWORD]

            if not isinstance(type_identifier, str):
                raise ExpectedStringValueForDictKey()
        elif not self.require_type_identifier:

            type_identifier = self.type_identifier

        else:
            raise ExpectedKeyInDict()

        fields = dict()
        metadata = dict()

        for name, value in operand.items():

            if name in self.RESERVED_KEYWORDS:
                metadata[name] = value
                continue

            name = self.unescape_field_name(name)
            fields[name] = value

        return type_identifier, fields, metadata

    def begin_packing(self, operand, context, state, type_identifier):

        result = {self.TYPE_KEYWORD: type_identifier}
        fields = []

        for name, value in operand.items():
            name = self.escape_field_name(name)
            field = Field(value, context.polymorphic_operator, SubscriptResult(result, name))
            fields.append(field)

        state.result = result
        return fields

    # noinspection PyMethodMayBeStatic
    def end_packing(self, operand, context, state):
        return state.result

    # noinspection PyMethodMayBeStatic
    def begin_unpacking(self, operand, context, state):

        state.type_identifier, state.result, state.reserved = self.unpack_raw_dict(operand)

        fields = []

        for name, value in state.result.items():
            field = Field(value, context.polymorphic_operator, SubscriptResult(state.result, name))
            fields.append(field)

        return fields

    # noinspection PyMethodMayBeStatic
    def end_unpacking(self, operand, context, state):
        return state.result

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def spread(self, task: Task) -> tp.Iterable[Task]:

        if task.verb not in Mode:
            raise UnknownVerb(task.verb)

        tasks = []

        # Create a fresh state attachment
        task.attachments.state = SimpleNamespace()

        parent_node = getattr(task.attachments, "parent_node", None)

        if task.verb is Mode.PACK:

            was_in_archive = False

            if not self.pack_as_value:

                # Check whether task.operand has already been archived in the current context and
                # acquire the archive_node for the operand

                was_in_archive, archive_node = task.context.archive_container_for(task.operand)

                # Register the task's result_container as a reference container for archive_node
                task.context.archive_record_reference_container(archive_node, task.result_container)

                # The parent_node for this operand requires the archive_node
                task.context.archive_record_required_node(parent_node, archive_node)

                # The archive_node is referenced by the parent_node
                task.context.archive_record_reference_node(archive_node, parent_node)

                task.attachments.result_container = archive_node if not was_in_archive else None

            else:
                archive_node = None
                task.attachments.result_container = task.result_container

            if not was_in_archive:

                fields = self.begin_packing(task.operand, task.context, task.attachments.state, self.type_identifier)

                for field in fields:
                    t = Task(task.context, task.verb, field.operator, field.value,
                             result_container=field.result_container)
                    t.attachments.parent_node = archive_node
                    tasks.append(t)

        elif task.verb is Mode.UNPACK:

            fields = self.begin_unpacking(task.operand, task.context, task.attachments.state)

            for field in fields:
                t = Task(task.context, task.verb, field.operator, field.value, result_container=field.result_container)
                tasks.append(t)

        return tasks

    def gather(self, task: Task):

        if task.verb is Mode.PACK:

            if task.attachments.result_container is not None:
                result = self.end_packing(task.operand, task.context, task.attachments.state)
                task.attachments.result_container.assign(result)

        elif task.verb is Mode.UNPACK:
            result = self.end_unpacking(task.operand, task.context, task.attachments.state)
            task.result_container.assign(result)


@log_operator
class DictModifierOperator(DictOperator):

    def __init__(self, type_identifier="builtins.dict", require_type_identifier=False):
        super(DictModifierOperator, self).__init__(type_identifier, require_type_identifier)

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def spread(self, task: Task) -> tp.Iterable[Task]:

        if task.verb not in Mode:
            raise UnknownVerb(task.verb)

        tasks = []

        if task.verb is Mode.PACK:

            if hasattr(task.attachments.state, 'result'):

                fields = self.begin_packing(task.operand, task.context, task.attachments.state, self.type_identifier)

                for field in fields:
                    t = Task(task.context, task.verb, field.operator, field.value,
                             result_container=field.result_container)
                    tasks.append(t)

        elif task.verb is Mode.UNPACK:

            fields = self.begin_unpacking(task.operand, task.context, task.attachments.state)

            for field in fields:
                t = Task(task.context, task.verb, field.operator, field.value, result_container=field.result_container)
                tasks.append(t)

        return tasks

    def gather(self, task: Task):

        if task.verb is Mode.PACK:

            if hasattr(task.attachments.state, 'result'):
                self.end_packing(task.operand, task.context, task.attachments.state)
                # task.result_container.assign(result)

        elif task.verb is Mode.UNPACK:
            self.end_unpacking(task.operand, task.context, task.attachments.state)
            # task.result_container.assign(result)


@log_operator
class ListOperator(DictOperator):

    def __init__(self, type_identifier="list"):
        super(ListOperator, self).__init__(type_identifier)

    def begin_packing(self, operand, context, state, type_identifier):

        result = [None] * len(operand)

        fields = []

        for index, value in enumerate(operand):
            field = Field(value, context.polymorphic_operator, SubscriptResult(result, index))
            fields.append(field)

        state.result = result
        return fields

    # noinspection PyMethodMayBeStatic
    def end_packing(self, operand, context, state):
        return state.result

    # noinspection PyMethodMayBeStatic
    def begin_unpacking(self, operand, context, state):

        result = [None] * len(operand)

        fields = []

        for index, value in enumerate(operand):
            field = Field(value, context.polymorphic_operator, SubscriptResult(result, index))
            fields.append(field)

        state.result = result
        return fields

    # noinspection PyMethodMayBeStatic
    def end_unpacking(self, operand, context, state):
        return state.result


class TupleOperator(ListOperator):

    def __init__(self, type_identifier="builtins.tuple"):
        super(TupleOperator, self).__init__(type_identifier)

    def begin_packing(self, operand, context, state, type_identifier):

        result = [None] * len(operand)

        fields = []

        for index, value in enumerate(operand):
            field = Field(value, context.polymorphic_operator, SubscriptResult(result, index))
            fields.append(field)

        state.result = {
            "type": type_identifier,
            "values": result
        }

        return fields

    # noinspection PyMethodMayBeStatic
    def end_packing(self, operand, context, state):
        return state.result

    # noinspection PyMethodMayBeStatic
    def begin_unpacking(self, operand, context, state):

        result = [None] * len(operand['values'])

        fields = []

        for index, value in enumerate(operand['values']):
            field = Field(value, context.polymorphic_operator, SubscriptResult(result, index))
            fields.append(field)

        state.result = result
        return fields

    # noinspection PyMethodMayBeStatic
    def end_unpacking(self, operand, context, state):
        return tuple(state.result)


@log_operator
class PolymorphicOperator(Operator):

    TYPE_KEYWORD = 'type'

    def __init__(self, registry, dict_type_identifier, require_type_identifier=False):
        super(PolymorphicOperator, self).__init__()
        self.registry = registry
        self.dict_type_identifier = dict_type_identifier
        self.require_type_identifier = require_type_identifier

    def determine_operator(self, task):

        if isinstance(task.operand, dict):

            if self.TYPE_KEYWORD in task.operand:

                type_identifier = task.operand[self.TYPE_KEYWORD]

                if not isinstance(type_identifier, str):
                    raise ExpectedStringValueForDictKey()

            elif not self.require_type_identifier:

                type_identifier = self.dict_type_identifier

            else:

                raise ExpectedKeyInDict()

            delegate = self.registry.lookup_value_for_alias(type_identifier)

        else:

            if isinstance(task.operand, GeneratorType) or \
                    isinstance(task.operand, Iterator) or \
                    isinstance(task.operand, slice):
                task.operand = list(task.operand)

            operand_type = type(task.operand)
            delegate = self.registry.lookup_value_for_type(operand_type)

        if delegate is None:
            raise UnknownType()

        operator = delegate.operator_for(task.operand, task.verb)
        return operator

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def spread(self, task: Task) -> tp.Iterable[Task]:

        if task.verb not in Mode:
            raise UnknownVerb(task.verb)

        tasks = []

        type_operator = self.determine_operator(task)

        if not hasattr(task.attachments, 'operator_queue'):
            task.attachments.operator_queue = []

        task.attachments.operator_queue.append(type_operator)
        tasks = type_operator.spread(task)

        return tasks

    def gather(self, task: Task):

        type_operator = task.attachments.operator_queue.pop(0)
        type_operator.gather(task)


def setup_builtin_delegates(registry, delegate_class):

    builtin_map = {

        list: ListOperator,
        tuple: TupleOperator,
        dict: DictOperator,
        str: StrOperator,
        bytes: BytesOperator,
        int: IntOperator,
        float: FloatOperator,
        type(None): NoneOperator
    }

    for operand_type, operator_class in builtin_map.items():

        operator = operator_class()
        delegate = delegate_class(operand_type, operator)

        registry.register_value_for_type(operand_type, delegate)
        registry.register_alias_for_type(operand_type, delegate.type_identifier)

    REFERENCE_DELEGATE = delegate_class(ReferenceType, ReferenceOperator(), ReferenceOperator.REFERENCE_TYPE)

    registry.register_alias_for_type(ReferenceType, ReferenceOperator.REFERENCE_TYPE)
    registry.register_value_for_alias(ReferenceOperator.REFERENCE_TYPE, REFERENCE_DELEGATE)


class ReferenceType:
    pass


@log_operator
class ReferenceOperator(Operator):

    TYPE_KEYWORD = 'type'
    INDEX_KEYWORD = 'index'
    REFERENCE_TYPE = 'ref'

    def __init__(self):
        super(ReferenceOperator, self).__init__()

    def encode(self, index):
        return {self.TYPE_KEYWORD: self.REFERENCE_TYPE, self.INDEX_KEYWORD: index}

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def spread(self, task: Task) -> tp.Iterable[Task]:

        if task.verb not in Mode:
            raise UnknownVerb(task.verb)

        if task.verb is Mode.PACK:
            pass

        elif task.verb is Mode.UNPACK:

            if not isinstance(task.operand, dict):
                raise ExpectedDictOperand()

            if self.TYPE_KEYWORD not in task.operand:
                raise ExpectedKeyInDict()

            type_identifier = task.operand[self.TYPE_KEYWORD]

            if not isinstance(type_identifier, str):
                raise ExpectedStringValueForDictKey()

            if type_identifier != self.REFERENCE_TYPE:
                raise UnknownType()

            archive_index = task.operand[self.INDEX_KEYWORD]

            if not isinstance(archive_index, int):
                raise ExpectedIntValueForDictKey()

            if archive_index < task.context.unpack_index or archive_index >= len(task.context.unpacked_objects):
                raise SerializableError()

            task.attachments.archive_index = archive_index

        return ()

    def gather(self, task: Task):

        if task.verb is Mode.UNPACK:

            archive_index = task.attachments.archive_index
            task.result = task.context.unpacked_objects[archive_index]


"""

class decorator:
attaches pack() method to class

User invokes pack() method on instance

pack() method retrieves delegate from its class (or looks it up)
and invokes the handle() method with the PACK verb

The delegate implements the verb action for the operand:
It creates an operator and runs a depth first search
to carry out the action.

Operators create other operators for sub-tasks. 
How should operator creation be encapsulated?


A delegate is the port of call for handling all verb actions 
on behalf of instances of a certain class. (Maybe the only
responsibility of a delegate should be to provide an operator for
an operand and a verb. The handle() method is really just
syntactic sugar for setting up a task and a context and invoke
handle_task())


An operator is a re-usable component in the context of
implementing verb actions as depth-first traversals of tasks.

The concrete problem of an operator splitting up a task
into subtasks should be made by the same mechanism that 
controls the splitting up itself. This allows to enforce
constraints on the set of possible sub-operands.

When there are no constraints or prior knowledge on the nature 
of an operand it is not yet clear how to derive a suitable operator.


So we have two types of lookup:

Given a type, we want to obtain a delegate for handling verb actions.
Given a type, we want to obtain an operator for handling verb actions.

The same should be possible for a type_identifier instead of a type.

So, given a type or type_identifier, we obtain a delegate. The delegate
creates an operator for the given operand and verb.

def operator_for(operand, verb):

    operand_type = type(operand)
    delegate = registry.lookup_value_for_type(operand_type, None)

    if delegate is not None:
        return delegate.operator_for(operand, verb)  # noqa
    
    raise NotSerializable()

"""
