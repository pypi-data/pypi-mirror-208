# -*- coding: utf-8 -*-

import enum
import weakref

from .core import SerializableError


__all__ = ['Mode', 'CLASS_VERBS', 'NotSerializable', 'DerivedClassNotSerializable', 'ExpectedVerbToBeMethod',
           'TypeAttachableMixin', 'DelegateAttachableMixin',
           'ExpectedDictOperand', 'ExpectedListOperand', 'ExpectedKeyInDict', 'ExpectedStringValueForDictKey',
           'ExpectedIntValueForDictKey', 'UnknownType']


class Mode(enum.Enum):

    PACK = 1
    UNPACK = 2


class NotSerializable(SerializableError):
    pass


class DerivedClassNotSerializable(NotSerializable):
    pass


class ExpectedVerbToBeMethod(NotSerializable):
    pass


class ExpectedDictOperand(SerializableError):
    pass


class ExpectedListOperand(SerializableError):
    pass


class ExpectedKeyInDict(SerializableError):
    pass


class ExpectedStringValueForDictKey(SerializableError):
    pass


class ExpectedIntValueForDictKey(SerializableError):
    pass


class UnknownType(SerializableError):
    pass


CLASS_VERBS = [Mode.UNPACK]


class TypeAttachableMixin:

    @property
    def type(self):
        return self.type_() if self.type_ else None

    @type.setter
    def type(self, value):
        self.type_ = weakref.ref(value)
        self.type_changed()

    def __init__(self):
        super().__init__()
        self.type_ = None

    def type_changed(self):
        pass


class DelegateAttachableMixin:

    @property
    def delegate(self):
        return self.delegate_() if self.delegate_ else None

    @delegate.setter
    def delegate(self, value):
        self.delegate_ = weakref.ref(value)
        self.delegate_changed()

    def __init__(self):
        super().__init__()
        self.delegate_ = None

    def delegate_changed(self):
        pass