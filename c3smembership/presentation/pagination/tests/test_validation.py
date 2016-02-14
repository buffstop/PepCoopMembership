# -*- coding: utf-8 -*-
"""
"""

import unittest
from c3smembership.presentation.pagination.validation import (
    DummyValidator,
    IntegerValidator,
    IValidator,
    MinLengthValidator,
    RegexValidator,
)


class TestIValidator(unittest.TestCase):

    def test_call(self):
        validator = IValidator()
        with self.assertRaises(NotImplementedError):
            validator('some value')


class TestDummyValidator(unittest.TestCase):

    def test_call(self):
        validator = DummyValidator()
        self.assertTrue(validator(None))
        self.assertTrue(validator(1))
        self.assertTrue(validator('test'))


class TestIntegerValidator(unittest.TestCase):

    def test_call(self):
        validator = IntegerValidator()
        self.assertFalse(validator(None))
        self.assertTrue(validator(3))
        self.assertTrue(validator('3'))
        self.assertFalse(validator('a'))


class RegexValidatorTest(unittest.TestCase):

    def test_call(self):
        validator = RegexValidator('test')
        self.assertFalse(validator(None))
        self.assertTrue(validator('test'))


class MinLengthValidatorTest(unittest.TestCase):

    def test_call(self):
        validator = MinLengthValidator(3)
        self.assertFalse(validator(None))
        self.assertFalse(validator(''), 3)
        self.assertFalse(validator('a'), 3)
        self.assertFalse(validator('aa'), 3)
        self.assertTrue(validator('aaa'), 3)
        self.assertTrue(validator('aaaa'), 3)
        self.assertFalse(validator([]), 3)
        self.assertFalse(validator([0]), 3)
        self.assertFalse(validator([0, 1]), 3)
        self.assertTrue(validator([0, 1, 2]), 3)
        self.assertTrue(validator([0, 1, 2, 3]), 3)

        validator = MinLengthValidator(0)
        self.assertTrue(validator(''), 3)
        self.assertTrue(validator([]), 3)

        validator = MinLengthValidator(-1)
        self.assertTrue(validator(''), 3)
        self.assertTrue(validator([]), 3)
