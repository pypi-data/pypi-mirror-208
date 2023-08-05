# -*- coding: utf-8 -*-

import inspect
import os
import sys

__all__ = ["identifier_from_name", "identifiers_from_qualified_name", "identifier_from_qualified_name",
           "dot_identifier_for_type"]


def identifier_from_name(name):

    indices = [index for index, c in enumerate(name) if c.isupper()]

    if not indices or indices[0] != 0:
        indices.insert(0, 0)

    if not indices or indices[-1] != len(name):
        indices.append(len(name))

    result = ''
    last_index = 0

    for index in indices:
        part = name[last_index:index]

        if part:

            part = part.lower()

            if result:
                result += '_'

            result += part

        last_index = index

    return result


def identifiers_from_qualified_name(qualified_name):

    components = qualified_name.split('.')

    for index, component in enumerate(components):
        components[index] = identifier_from_name(component)

    return components


def identifier_from_qualified_name(qualified_name, separator="."):

    components = identifiers_from_qualified_name(qualified_name)
    return separator.join(components)


MAIN_MODULE_NAME = None


def dot_identifier_for_type(type):

    global MAIN_MODULE_NAME

    module_name = type.__module__

    if module_name == "__main__":

        while MAIN_MODULE_NAME is None:

            module_path = inspect.getmodule(type).__file__
            name = inspect.getmodulename(module_path)

            if name is None:
                MAIN_MODULE_NAME = "__main__"
                break

            path = [name]

            package_path = os.path.dirname(module_path)

            while package_path:

                if not os.path.isdir(package_path):
                    break

                if not os.path.isfile(os.path.join(package_path, "__init__.py")):
                    break

                package_name = os.path.basename(package_path)
                path.insert(0, package_name)

                parent_package_path = os.path.dirname(package_path)

                if parent_package_path == package_path:
                    break

                package_path = parent_package_path

            MAIN_MODULE_NAME = ".".join(path)
            break

        module_name = MAIN_MODULE_NAME

    return identifier_from_qualified_name(module_name + "." + type.__qualname__)