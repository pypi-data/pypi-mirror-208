# -*- coding: utf-8 -*-
import types
import typing as tp
import inspect

from .inspect import inspect_arguments, NoArgumentValue, ArgumentList, Argument
from .core import *
from .identifiers import dot_identifier_for_type
from .common import *
from .operators import Field, PolymorphicOperator, AtomicOperator, DictOperator, DictModifierOperator, \
                        SingletonOperator, ReferenceOperator, setup_builtin_delegates
from .types import TypeRegistry, isnamedtuple
from .toposort import toposort

__all__ = ['ObjectArchive', 'ArchiveContext', 'TypeDelegate', 'DELEGATE_REGISTRY',
           'SaveInitArguments', 'SaveAssignments', 'Singleton']


DELEGATE_REGISTRY = TypeRegistry()


@log_operator
class ArchiveOperator(TypeAttachableMixin, DictOperator):

    def __init__(self, type_identifier="archive"):

        TypeAttachableMixin.__init__(self)
        DictOperator.__init__(self, type_identifier)

    def begin_packing(self, operand, context, state, type_identifier):

        result = {self.TYPE_KEYWORD: type_identifier,
                  "version": "1.0.0"}

        fields = [Field(operand.records, AtomicOperator(), SubscriptResult(result, "records"))]

        state.result = result
        return fields

    # noinspection PyMethodMayBeStatic
    def begin_unpacking(self, operand, context, state):

        state.type_identifier, state.result, state.reserved = self.unpack_raw_dict(operand)
        return ()

    # noinspection PyMethodMayBeStatic
    def end_unpacking(self, operand, context, state):

        result = ObjectArchive()

        if "records" not in state.result:
            raise ExpectedKeyInDict()

        result.records = state.result["records"]

        return result

    def copy(self):
        result = ArchiveOperator()
        result.type = self.type
        result.type_identifier = self.type_identifier
        return result

    def gather(self, task: Task):

        super(ArchiveOperator, self).gather(task)


class ArchiveUnwrapper(Operator):

    def __init__(self):
        super(ArchiveUnwrapper, self).__init__()

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def spread(self, task: Task) -> tp.Iterable[Task]:
        return task.context.polymorphic_operator.spread(task)

    def gather(self, task: Task):

        task.context.polymorphic_operator.gather(task)

        if task.verb is Mode.UNPACK:
            task.context.unpack_index -= 1


class ObjectArchive(Delegate, object):

    def __init__(self):
        self.records = list()

    def allocate(self):
        archive_index = len(self.records)
        self.records.append(None)

        return SubscriptResult(self.records, archive_index)

    def pack(self):

        context = ArchiveContext()
        task = Task(context, Mode.PACK, ArchiveOperator(), self)
        handle_task(task)
        context.order_archive_nodes()
        return context.archive.records[0]

    def unpack(self):

        context = ArchiveContext(archive=self)
        context.unpacked_objects = [None] * len(self.records)
        unwrapper = ArchiveUnwrapper()
        tasks = []

        for index, operand in enumerate(reversed(self.records)):

            index = len(self.records) - 1 - index

            operator = unwrapper
            result_container = SubscriptResult(context.unpacked_objects, index)

            task = Task(context, Mode.UNPACK, operator, operand, result_container=result_container)
            tasks.append(task)

        task = Task(context, Mode.UNPACK, TaskListOperator(), tasks)
        handle_task(task)

        context.apply_assignments()

        result = context.unpacked_objects[0]
        return result

    @staticmethod
    def unpack_from(archived):

        context = ArchiveContext()
        task = Task(context, Mode.UNPACK, ArchiveOperator(), archived)
        result = handle_task(task)

        return result


class TypeDelegate(TypeAttachableMixin, Delegate):

    # noinspection PyShadowingBuiltins
    def __init__(self, type, operator, type_identifier=None):

        super(TypeDelegate, self).__init__()

        if type_identifier is None:
            type_identifier = dot_identifier_for_type(type)

        self.type = type
        self.type_identifier = type_identifier
        self.operator = operator

    def operator_for(self, operand: tp.Any, verb: tp.Any):
        return self.operator

    def handle(self, operand, verb, context=None) -> tp.Any:

        if verb not in Mode:
            raise UnknownVerb(verb)

        result = NoResult

        if verb is Mode.PACK:

            if context is None:
                context = ArchiveContext()

            # ignore result, which is just a reference to the operand
            super(TypeDelegate, self).handle(operand, verb, context)
            context.order_archive_nodes()
            result = context.archive.pack()

        elif verb is Mode.UNPACK:
            archive = ObjectArchive.unpack_from(operand)
            result = archive.unpack()

        return result


setup_builtin_delegates(DELEGATE_REGISTRY, TypeDelegate)
DEFAULT_OPERATOR = PolymorphicOperator(DELEGATE_REGISTRY, "builtins.dict")


class ArchiveNode(ResultContainer):

    def __init__(self):
        self.content = NoResult
        self.operand = None  # The operand that gave rise to this node. We save the operand so that it does not
                             # get deallocated during packing, which can lead to key collisions

        self.reference_nodes = []  # Holds all nodes referenced by this node
        self.reference_containers = []  # Holds all containers with a reference to this node

        self.required_nodes = []  # Holds all nodes required by this node
        self.remaining = None  # Will hold a count of the remaining required nodes


    def assign(self, content):
        self.content = content

    def __call__(self):
        return self.content

    def get_reference_nodes(self):
        return self.reference_nodes

    def get_remaining(self):

        if self.remaining is None:
            self.remaining = len(self.required_nodes)

        return self.remaining

    def set_remaining(self, value):
        self.remaining = value


class ArchiveContext(Context):

    def __init__(self, archive=None):
        super(ArchiveContext, self).__init__(DEFAULT_OPERATOR)

        if archive is None:
            archive = ObjectArchive()

        self.archive = archive

        self.archive_nodes = []
        self.archive_indices = dict()

        self.reference_operator = ReferenceOperator()

        self.unpacked_objects = None
        self.unpack_index = len(self.archive.records)

        self.assignments = dict()

    # noinspection PyMethodMayBeStatic
    def key_for_operand(self, operand):
        return id(operand)

    def archive_container_for(self, operand, allocate=True):

        key = self.key_for_operand(operand)
        key_container = self.archive_indices.get(key, None)

        if key_container is not None:
            return True, key_container

        if allocate:

            archive_node = ArchiveNode()
            archive_node.operand = operand
            self.archive_nodes.append(archive_node)
            key_container = archive_node
            self.archive_indices[key] = key_container

        return False, key_container

    # noinspection PyMethodMayBeStatic
    def archive_record_reference_container(self, referenced_node, reference_container):
        referenced_node.reference_containers.append(reference_container)

    # noinspection PyMethodMayBeStatic
    def archive_record_reference_node(self, node, reference_node):

        if node is None or reference_node is None:
            return

        node.reference_nodes.append(reference_node)

    # noinspection PyMethodMayBeStatic
    def archive_record_required_node(self, node, required_node):

        if node is None or required_node is None:
            return

        node.required_nodes.append(required_node)

    def archive_record_assignments(self, archive_index, assignments):
        self.assignments[archive_index] = assignments

    def apply_assignments(self):

        assignment_indices = sorted(self.assignments.keys(), reverse=True)

        for archive_index in assignment_indices:
            target = self.unpacked_objects[archive_index]
            index_assignments = self.assignments[archive_index]

            for attribute, value in index_assignments.items():
                task = Task(self, Mode.UNPACK, self.reference_operator, value)
                value_result = handle_task(task)
                setattr(target, attribute, value_result)

            pass

        pass

    def order_archive_nodes(self):

        is_ordered, nodes = toposort(self.archive_nodes,
                              ArchiveNode.get_reference_nodes,
                              ArchiveNode.get_remaining,
                              ArchiveNode.set_remaining,
                              tie_breaker=None)

        if not is_ordered:
            raise SerializableError()

        for node in reversed(nodes):

            index = len(self.archive.records)

            if len(node.reference_containers) != 1 or index == 0:

                reference = self.reference_operator.encode(index)

                for container in node.reference_containers:
                    container.assign(reference)

                self.archive.records.append(node.content)

            else:
                node.reference_containers[0].assign(node.content)


@log_operator
class SaveInitArguments(TypeAttachableMixin, DelegateAttachableMixin, DictOperator):

    class MethodNotDefined(SerializableError):

        def __init__(self, class_identifier, method_name):
            self.class_identifier = class_identifier
            self.method_name = method_name

    class CannotSynthesizeMethod(SerializableError):

        def __init__(self, class_identifier, method_name):
            self.class_identifier = class_identifier
            self.method_name = method_name

    class SaveInitArgumentsResultInvalid(SerializableError):

        def __init__(self, class_identifier, method_name, undefined_arguments, unknown_keywords):
            self.class_identifier = class_identifier
            self.method_name = method_name
            self.undefined_arguments = undefined_arguments
            self.unknown_keywords = unknown_keywords

    def __init__(self, method_name="save_init_arguments"):

        TypeAttachableMixin.__init__(self)
        DelegateAttachableMixin.__init__(self)
        DictOperator.__init__(self, require_type_identifier=True)

        self.method_name = method_name
        self.method = None
        self.init_argument_list = None

    def type_changed(self):

        if isnamedtuple(self.type):

            self.init_argument_list = ArgumentList()
            self.init_argument_list.arguments = [Argument(name="self", default=NoArgumentValue, keyword_only=False)] + \
                [Argument(name=field, default=NoArgumentValue, keyword_only=True) for field in self.type._fields]

            def save_init_arguments(instance, arguments):

                for argument in self.init_argument_list.arguments[1:]:

                    value = getattr(instance, argument.name)
                    setattr(arguments, argument.name, value)

            self.method = save_init_arguments
            return

        self.method = self.type.__dict__.get(self.method_name, None)
        self.init_argument_list = inspect_arguments(self.type.__init__)

        if self.method is None:

            for init_argument in self.init_argument_list.arguments[1:]:
                if init_argument.default is NoArgumentValue and init_argument.name not in self.type.__dict__:
                    raise self.CannotSynthesizeMethod(dot_identifier_for_type(self.type), self.method_name)

            if self.init_argument_list.allows_variable_arguments:
                init_asterisk_name = self.init_argument_list.asterisk_name
                if init_asterisk_name not in self.type.__dict__:
                    raise self.CannotSynthesizeMethod(dot_identifier_for_type(self.type), self.method_name)

            def save_init_arguments(instance, arguments):

                for argument in self.init_argument_list.arguments[1:]:

                    if hasattr(instance, argument.name):
                        value = getattr(instance, argument.name)
                    else:
                        value = argument.default

                    setattr(arguments, argument.name, value)

                if self.init_argument_list.allows_variable_arguments:
                    asterisk_name = self.init_argument_list.asterisk_name
                    setattr(arguments, asterisk_name, getattr(instance, asterisk_name))

            self.method = save_init_arguments

        if not inspect.isfunction(self.method):
            raise self.MethodNotDefined(dot_identifier_for_type(self.type), self.method_name)

    def delegate_changed(self):
        self.type_identifier = self.delegate.type_identifier

    def save_instance_init_arguments(self, instance):

        ignore = (self.init_argument_list.arguments[0].name,)
        arguments = self.init_argument_list.build_value_scope(ignore=ignore)
        self.method(instance, arguments)
        check = self.init_argument_list.check_value_scope(arguments, ignore=ignore)

        if not check.passed:
            raise self.SaveInitArgumentsResultInvalid(self.method_name, dot_identifier_for_type(self.type),
                                                      check.undefined_arguments, check.unknown_keywords)

        return arguments

    def begin_packing(self, operand, context, state, type_identifier):

        if not isinstance(operand, self.type):
            raise NotSerializable()

        arguments = self.save_instance_init_arguments(operand)

        result = super(SaveInitArguments, self).begin_packing(arguments.__dict__, context, state, type_identifier)
        return result

    # noinspection PyMethodMayBeStatic
    def end_packing(self, operand, context, state):
        return state.result

    # noinspection PyMethodMayBeStatic
    def end_unpacking(self, operand, context, state):
        # delegate = self.registry.lookup_value_for_alias(type_identifier)

        ignore = (self.init_argument_list.arguments[0].name,)
        args, kwargs = self.init_argument_list.args_and_kwargs_from_value_dict(state.result, ignore=ignore)
        instance = self.type(*args, **kwargs)
        return instance

    def copy(self):
        result = SaveInitArguments(self.method_name)
        result.type = self.type
        return result


@log_operator
class SaveAssignments(TypeAttachableMixin, DictModifierOperator):

    def __init__(self, method_name="save_assignments", type_identifier="assign"):

        TypeAttachableMixin.__init__(self)
        DictModifierOperator.__init__(self, type_identifier, require_type_identifier=True)

        self.method_name = method_name
        self.method = None

    def type_changed(self):

        self.method = self.type.__dict__.get(self.method_name, None)

        if self.method is None or not inspect.isfunction(self.method):
            raise self.MethodNotDefined(self.method_name, dot_identifier_for_type(self.type))

    def save_instance_assignments(self, instance):

        assignments = types.SimpleNamespace()
        self.method(instance, assignments)
        return assignments

    def begin_packing(self, operand, context, state, type_identifier):

        if not isinstance(operand, self.type):
            raise NotSerializable()

        assignments = self.save_instance_assignments(operand)
        tmp_state = types.SimpleNamespace()

        result = super(SaveAssignments, self).begin_packing(assignments.__dict__, context, tmp_state, type_identifier)

        state.result[self.ASSIGN_KEYWORD] = tmp_state.result
        return result

    # noinspection PyMethodMayBeStatic
    def begin_unpacking(self, operand, context, state):
        # state.type_identifier, state.result, state.reserved = self.unpack_raw_dict(operand)

        if self.ASSIGN_KEYWORD not in state.reserved:
            raise ExpectedKeyInDict()

        assignments = state.reserved[self.ASSIGN_KEYWORD]
        tmp_state = types.SimpleNamespace()

        super(SaveAssignments, self).begin_unpacking(assignments, context, tmp_state)

        if tmp_state.type_identifier != self.type_identifier:
            raise UnknownType()

        context.archive_record_assignments(context.unpack_index - 1, tmp_state.result)

        return ()

    # noinspection PyMethodMayBeStatic
    def end_unpacking(self, operand, context, state):
        return NoResult

    def copy(self):
        result = SaveAssignments(self.method_name, type_identifier=self.type_identifier)
        result.type = self.type
        return result

    def gather(self, task: Task):
        super(SaveAssignments, self).gather(task)


@log_operator
class Singleton(TypeAttachableMixin, SingletonOperator):

    def __init__(self, method_name="get_singleton", type_identifier="assign"):

        TypeAttachableMixin.__init__(self)
        SingletonOperator.__init__(self, type_identifier, singleton_provider=self.get_singleton)

        self.method_name = method_name
        self.method = None

    def type_changed(self):

        self.method = self.type.__dict__.get(self.method_name, None)

        if self.method is None or not inspect.isfunction(self.method):
            raise self.MethodNotDefined(self.method_name, dot_identifier_for_type(self.type))

    def get_singleton(self):
        return self.method()

    def copy(self):
        result = Singleton(self.method_name, type_identifier=self.type_identifier)
        result.type = self.type
        return result

