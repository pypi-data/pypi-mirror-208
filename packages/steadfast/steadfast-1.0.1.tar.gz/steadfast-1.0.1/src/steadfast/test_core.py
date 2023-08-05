#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import random
import sys

from .core import *

class Klaus:
    pass


class CoreTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CoreTest, self).__init__(*args, **kwargs)

        seed = None

        if seed is None:
            seed = random.randrange(sys.maxsize)

        self.seed_ = seed
        self.random_ = random.Random(self.seed_)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_klaus(self):

        delegate = Delegate()
        result = delegate.handle(Klaus(), None)

        self.assertTrue(True)
