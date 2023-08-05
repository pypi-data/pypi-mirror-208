#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import random
import sys
import weakref

from collections import namedtuple

from .__init__ import *


@decl_serializable(
    SaveInitArguments())
class Image(object):

    @property
    def width(self):
        return self.width_

    @property
    def height(self):
        return self.height_

    @property
    def title(self):
        return self.title_

    def __init__(self, width=640, height=480, aspect_ratio=(1,1), title="Untitled"):
        self.width_ = width
        self.height_ = height
        self.aspect_ratio_ = aspect_ratio
        self.title_ = title

    def save_init_arguments(self, arguments):

        arguments.width = self.width
        arguments.height = self.height
        arguments.aspect_ratio = self.aspect_ratio_
        arguments.title = self.title


@decl_serializable(
    SaveInitArguments())
class DerivedImage(Image):

    @property
    def extra(self):
        return self.extra_

    def __init__(self, width=0, height=0, aspect_ratio=(1,1), title='', extra="none"):
        super(DerivedImage, self).__init__(width, height, aspect_ratio, title)
        self.extra_ = extra

    def save_init_arguments(self, arguments):
        super(DerivedImage, self).save_init_arguments(arguments)

        arguments.extra = self.extra


@decl_serializable(
    SaveInitArguments())
class MaskedImage(Image):

    @property
    def mask(self):
        return self.mask_

    def __init__(self, width=0, height=0, aspect_ratio=(1,1), title='', mask=None):
        super().__init__(width, height, aspect_ratio, title)

        self.mask_ = mask

    def save_init_arguments(self, arguments):
        super(MaskedImage, self).save_init_arguments(arguments)

        arguments.mask = self.mask


def qualified_namedtuple(*args, qualname=None, **kwargs):
    Result = namedtuple(*args, **kwargs)

    if qualname:
        Result.__qualname__ = qualname + "." + Result.__qualname__

    return Result


@decl_serializable(
    SaveInitArguments())
class A(object):

    Operand = qualified_namedtuple('Operand', 'x, y', qualname=__qualname__)
    Operand = decl_serializable(Operand)

    @property
    def elements(self):
        return iter(self.elements_)

    @property
    def operand(self):
        return self.operand_

    def __init__(self, operand, *elements):
        self.operand_ = operand
        self.elements_ = list(elements)


@decl_serializable(
    SaveInitArguments())
class B(object):

    def __init__(self, domain=None):
        self.domain = domain

    def save_init_arguments(self, arguments):
        arguments.domain = self.domain


@decl_serializable(
    SaveInitArguments(),
    SaveAssignments()
)
class C(object):

    @property
    def a(self):
        return self.a_() if self.a_ is not None else None

    @a.setter
    def a(self, value):
        self.a_ = weakref.ref(value) if value is not None else None

    def __init__(self):
        self.a_ = None

    def save_init_arguments(self, arguments):
        pass

    def save_assignments(self, assignments):
        assignments.a = self.a


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

    def test_example(self):

        c = C()
        b1 = B(c)
        b2 = B(c)
        op = A.Operand(3, 5)
        a = A(op, b1, b2)
        c.a = a

        archived = a.pack()
        # a2 = A.unpack(archived)

        mask = DerivedImage(width=333, height=777, aspect_ratio=(16, 9), title="Mask", extra="77")
        masked_image = MaskedImage(width=222, height=555, aspect_ratio=(3, 4), title="Hello", mask=mask)

        archived = masked_image.pack()
        masked_image_2 = MaskedImage.unpack(archived)

        self.assertTrue(True)
