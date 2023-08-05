# -*- coding: utf-8 -*-

import typing as tp
import types

from .inspect import get_calling_function


__all__ = ["Task", "Operator", "Delegate", "Context", "CompositeOperator", "TaskListOperator",
           "NoResult", "ResultContainer", "SubscriptResult", "AttributeResult",
           "SerializableError", "UnknownVerb", "handle_task", "log_operator"]

"""

Structurally guided serialization proceeds by depth-first traversal of operators:



    Each operator modifies an operand

    designated state by incorporating information from an operand.

    When we visit a task for the first time we check whether the task can be 
    split up into sub-tasks, and if so, we add those tasks to the traversal



"""


class SerializableError(Exception):
    pass


class UnknownVerb(SerializableError):
    pass


class Context:

    def __init__(self, polymorphic_operator=None):

        if polymorphic_operator is None:
            polymorphic_operator = Operator()

        self.polymorphic_operator = polymorphic_operator


class NoResult:
    pass


class ResultContainer:

    def assign(self, value):
        pass

    def __call__(self):
        return NoResult


class SubscriptResult(ResultContainer):

    def __init__(self, container, subscript):
        self.container = container
        self.subscript = subscript

    def __call__(self):
        return self.container[self.subscript]

    def assign(self, value):
        self.container[self.subscript] = value


class AttributeResult(ResultContainer):

    def __init__(self, container, attribute):
        self.container = container
        self.attribute = attribute

    def __call__(self):
        return getattr(self.container, self.attribute)

    def assign(self, value):
        setattr(self.container, self.attribute, value)


class Task:

    context = None
    verb = None
    operator = None
    operand = None

    @property
    def result(self):
        return self.result_

    @result.setter
    def result(self, value):
        self.result_ = value

        if self.result_container is not None:
            self.result_container.assign(self.result_)

    result_container = None
    attachments = None

    def __init__(self, context, verb, operator, operand, result=NoResult, result_container=None):

        if result_container is None:
            result_container = AttributeResult(self, "result_")

        self.context = context
        self.verb = verb
        self.operator = operator
        self.operand = operand
        self.result_container = result_container
        self.result_ = None
        self.result = result
        self.attachments = types.SimpleNamespace()


class Operator:

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def spread(self, task: Task) -> tp.Iterable[Task]:
        return ()

    def gather(self, task: Task):
        pass

    def copy(self):
        return self.__class__()


LOG_OPERATOR_ACTIVE = False


def log_operator(cls):

    if not LOG_OPERATOR_ACTIVE:
        return cls

    svd_spread = getattr(cls, "spread")
    svd_gather = getattr(cls, "gather")

    def spread(self, task):

        f = get_calling_function()

        if not hasattr(f, 'is_patched'):
            print(f"{self.__class__.__name__}.spread(): {type(task.operand).__name__} <{id(task.operand):x}>, attachments='{task.attachments.__dict__}'")

        result = svd_spread(self, task)
        return result

    def gather(self, task):
        result = svd_gather(self, task)

        f = get_calling_function()

        if not hasattr(f, 'is_patched'):
            print(f"{self.__class__.__name__}.gather(): {type(task.operand).__name__} <{id(task.operand):x}>, attachments='{task.attachments.__dict__}'")

        return result

    setattr(spread, "is_patched", True)
    setattr(gather, "is_patched", True)

    setattr(cls, "spread", spread)
    setattr(cls, "gather", gather)

    return cls


@log_operator
class CompositeOperator(Operator):

    def __init__(self, parent_operator, child_operators):
        super(CompositeOperator, self).__init__()
        self.parent_operator = parent_operator
        self.child_operators = list(child_operators)

    def spread(self, task: Task) -> tp.Iterable[Task]:

        tasks = list(self.parent_operator.spread(task))

        for operator in self.child_operators:
            child_tasks = operator.spread(task)
            tasks.extend(child_tasks)

        return tasks

    def gather(self, task: Task):

        for operator in self.child_operators:
            operator.gather(task)

        self.parent_operator.gather(task)

    def copy(self):
        return CompositeOperator(self.parent_operator, self.child_operators)


@log_operator
class TaskListOperator(Operator):

    def __init__(self):
        super(TaskListOperator, self).__init__()

    def spread(self, task: Task) -> tp.Iterable[Task]:
        return task.operand


class Delegate:

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def operator_for(self, operand: tp.Any, verb: tp.Any):
        return Operator()

    def handle(self, operand, verb, context=None) -> tp.Any:

        if context is None:
            context = Context()

        operator = self.operator_for(operand, verb)
        task = Task(context, verb, operator, operand)
        return handle_task(task)


def handle_task(task):

    class FirstVisit:
        pass

    stack = [(task, FirstVisit)]

    while stack:

        task, subtask_iterator = stack[-1]

        if subtask_iterator is FirstVisit:

            # print(f"spread(): {type(task.operand).__name__} <{id(task.operand):x}>")

            subtasks = task.operator.spread(task)
            subtask_iterator = iter(subtasks)
            stack[-1] = task, subtask_iterator

        if subtask_iterator is not None:
            try:
                subtask = next(subtask_iterator)
                stack.append((subtask, FirstVisit))
                continue

            except StopIteration:
                pass

        # print(f"gather(): {type(task.operand).__name__} <{id(task.operand):x}>")
        task.operator.gather(task)
        stack.pop()

    return task.result
