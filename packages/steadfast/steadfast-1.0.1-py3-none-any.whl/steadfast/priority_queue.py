# -*- coding: utf-8 -*-

import heapq


class PriorityQueue(object):

    """
        Wrapper for heapq. Lower priorities get returned before higher priorities.

    """

    class _State(object):

        def __init__(self, key):
            self.key = key
            self.ignore = False

    class _TieBreaker(object):

        def __init__(self):
            self._count = 0

        def __call__(self, key):
            self._count += 1
            return self._count

    def __init__(self, tie_breaker=None):

        self._heap = []
        self._states_by_key = {}
        self._tie_breaker = tie_breaker

        if self._tie_breaker is None:
            # tmp = self._TieBreaker()
            # self._tie_breaker = lambda key: tmp(key)
            self._tie_breaker = self._TieBreaker()

    def __len__(self):
        return len(self._states_by_key)

    def push(self, key, priority):

        state = self._states_by_key.get(key, None)

        if state is not None:
            state.ignore = True

        state = self._State(key)
        self._states_by_key[key] = state

        heapq.heappush(self._heap, (priority, self._tie_breaker(key), state))

    def pop(self):

        while self._heap:

            priority, _, state = heapq.heappop(self._heap)

            if not state.ignore:

                self._states_by_key.pop(state.key, None)

                if not self._states_by_key:
                    self._heap = []

                return state.key

        return None

