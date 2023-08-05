# -*- coding: utf-8 -*-

import sys
from .priority_queue import PriorityQueue


# noinspection SpellCheckingInspection
__all__ = ['toposort']


# noinspection PyUnusedLocal
# noinspection SpellCheckingInspection
def recover_cycle(node_in_cycle, nodes, node_adjacencies):

    stack = [[node_in_cycle, 0]]
    marked_nodes = set()
    marked_nodes.add(node_in_cycle)

    while stack:

        entry = stack[-1]
        node = entry[0]
        index = entry[1]

        if index >= len(node_adjacencies(node)):
            marked_nodes.remove(node)
            stack.pop()
            continue

        entry[1] = index + 1

        next_node = node_adjacencies(node)[index]

        if next_node == node_in_cycle:
            return [item[0] for item in stack]

        if next_node in marked_nodes:
            continue

        stack.append([next_node, 0])
        marked_nodes.add(next_node)

    return [node_in_cycle]


# noinspection SpellCheckingInspection
def toposort(nodes, node_adjacencies, node_get_priority, node_set_priority, tie_breaker=None):

    """
    :param nodes:
    :param node_adjacencies: node_adjacencies(node) -> Iterable
    :param node_get_priority: node_get_priority(node) -> int
    :param node_set_priority: node_set_priority(node) -> int
    :param tie_breaker:
    :return: A tuple composed of a boolean and a list of nodes;
             If the boolean is True, the list of nodes represents the topological order,
             if the boolean is False, the list of nodes represents a cycle.
    """

    def node_number(node_arg):
        return id(node_arg)

    if tie_breaker is None:
        tie_breaker = node_number

    ordered_nodes = []
    q = PriorityQueue(tie_breaker=tie_breaker)

    for node in nodes:
        q.push(node, node_get_priority(node))

    last_priority = -(sys.maxsize - 2)

    while q:

        node = q.pop()
        priority = node_get_priority(node)

        # print(f"toposort: priority={priority:d}")

        if priority < last_priority:
            # cycle detected
            cycle = recover_cycle(node, nodes, node_adjacencies)
            return False, cycle

        last_priority = priority

        ordered_nodes.append(node)

        for dependent in node_adjacencies(node):
            priority = node_get_priority(dependent)
            priority -= 1
            node_set_priority(dependent, priority)
            q.push(dependent, priority)

    return True, ordered_nodes
