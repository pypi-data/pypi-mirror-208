# -*- coding: utf-8 -*-

import inspect
from collections import namedtuple
from types import SimpleNamespace

__all__ = ['Argument', 'NoArgumentValue', 'ArgumentList', 'inspect_arguments', 'get_calling_function']


Argument = namedtuple('Argument', 'name, default, keyword_only')


class ExpectedArgumentValue(Exception):
    pass


class NoArgumentValue:
    pass


class VariableArguments:
    pass


class VariableKeywords:
    pass


class ArgumentList:

    class Check:

        def __init__(self):
            self.passed = False
            self.undefined_arguments = []
            self.unknown_keywords = []

        def update_status(self):
            self.passed = not self.undefined_arguments and not self.unknown_keywords

    @property
    def allows_variable_arguments(self):
        return not not self.asterisk_name

    @property
    def allows_variable_keywords(self):
        return not not self.double_asterisk_name

    @property
    def arguments(self):
        return self.arguments_[:]

    @arguments.setter
    def arguments(self, value):
        self.arguments_ = list(value)
        self.clear_caches()

    @property
    def asterisk_name(self):
        return self.asterisk_name_

    @asterisk_name.setter
    def asterisk_name(self, value):
        self.asterisk_name_ = value
        self.clear_caches()

    @property
    def double_asterisk_name(self):
        return self.double_asterisk_name_

    @double_asterisk_name.setter
    def double_asterisk_name(self, value):
        self.double_asterisk_name_ = value
        self.clear_caches()

    @property
    def name_index(self):

        if self.name_index_ is None:
            self.name_index_ = dict()

            for arg in self.arguments:
                self.name_index_[arg.name] = arg

            if self.allows_variable_arguments:
                self.name_index_[self.asterisk_name] = VariableArguments

            if self.allows_variable_arguments:
                self.name_index_[self.double_asterisk_name] = VariableKeywords

        return self.name_index_

    def __init__(self):
        self.arguments_ = []
        self.asterisk_name_ = ''
        self.double_asterisk_name_ = ''
        self.name_index_ = None

    def clear_caches(self):
        self.name_index_ = None

    def build_value_dict(self, ignore=None):

        if ignore is None:
            ignore = ()

        result = dict()

        for arg in self.arguments:

            if arg.name in ignore:
                continue

            result[arg.name] = arg.default
            #setattr(result, arg.name, arg.default)

        if self.allows_variable_arguments and self.asterisk_name not in ignore:
            result[self.asterisk_name] = ()
            #setattr(result, self.asterisk_name, ())

        return result

    def build_value_scope(self, ignore=None):
        result = SimpleNamespace()
        result.__dict__.update(self.build_value_dict(ignore))
        return result

    def check_value_dict(self, argument_values, ignore=None, exit_early=True):

        if ignore is None:
            ignore = ()

        result = self.Check()

        name_index = self.name_index

        for arg, value in argument_values.items():

            if arg not in name_index or arg in ignore:

                if not (self.allows_variable_keywords or arg in ignore):
                    result.unknown_keywords.append(arg)

                    if exit_early:
                        return result

            if value is NoArgumentValue:
                result.undefined_arguments.append(arg)

                if exit_early:
                    return result

        for arg in self.arguments:

            if arg.name in ignore:
                continue

            if arg.name not in argument_values:
                result.undefined_arguments.append(arg)

                if exit_early:
                    return result

        if self.allows_variable_arguments and self.asterisk_name not in ignore:

            if self.asterisk_name not in argument_values:
                result.undefined_arguments.append(self.asterisk_name)

                if exit_early:
                    return result

        result.update_status()
        return result

    def check_value_scope(self, argument_values, ignore=None, exit_early=True):
        return self.check_value_dict(argument_values.__dict__, ignore, exit_early)

    def args_and_kwargs_from_value_dict(self, value_dict, ignore=None):

        if ignore is None:
            ignore = ()

        args = []
        kwargs = {}

        for arg in self.arguments:

            if arg.name in ignore:
                continue

            value = value_dict.get(arg.name, arg.default)

            if value is NoArgumentValue:
                raise ExpectedArgumentValue()

            if not arg.keyword_only:
                args.append(value)
            else:
                kwargs[arg.name] = value

        if self.allows_variable_arguments:
            args.extend(value_dict[self.asterisk_name])

        return args, kwargs

    def args_and_kwargs_from_value_scope(self, value_scope, ignore=None):
        return self.args_and_kwargs_from_value_scope(value_scope.__dict__, ignore)


def inspect_arguments(method):

    # 'args' is a list of the parameter names.
    # 'varargs' and 'varkw' are the names of the * and ** parameters or None.
    # 'defaults' is an n-tuple of the default values of the last n parameters.
    # 'kwonlyargs' is a list of keyword-only parameter names.
    # 'kwonlydefaults' is a dictionary mapping names from kwonlyargs to defaults.
    # 'annotations' is a dictionary mapping parameter names to annotations.

    method = inspect.getfullargspec(method)
    arguments = []

    defaults = method.defaults if method.defaults is not None else ()
    # noinspection SpellCheckingInspection
    kwonlydefaults = method.kwonlydefaults if method.kwonlydefaults is not None else {}
    n_positional = len(method.args) - len(defaults)

    for argument in method.args[:n_positional]:
        arguments.append(Argument(name=argument, default=NoArgumentValue, keyword_only=False))

    for argument, default_value in zip(method.args[n_positional:], defaults):
        arguments.append(Argument(name=argument, default=default_value, keyword_only=False))

    for argument in method.kwonlyargs:
        default_value = kwonlydefaults.get(argument, NoArgumentValue)
        arguments.append(Argument(name=argument, default=default_value, keyword_only=True))

    result = ArgumentList()
    result.arguments = arguments
    result.asterisk_name = method.varargs if method.varargs is not None else ''
    result.double_asterisk_name = method.varkw if method.varkw is not None else ''

    return result


def get_calling_function():
    frame = inspect.currentframe()
    frame = frame.f_back
    frame = frame.f_back

    co_name = frame.f_code.co_name
    self = frame.f_locals.get("self", None)

    if "self" in frame.f_code.co_varnames:
        cls = self.__class__
        f = getattr(cls, co_name)
    else:
        f = frame.f_globals[co_name]

    return f