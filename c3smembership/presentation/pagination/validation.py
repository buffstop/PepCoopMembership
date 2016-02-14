# -*- coding: utf-8 -*-
"""
Validation utilities for reading pagination settings from sources.
"""

import re


class IValidator(object):
    # pylint: disable=too-few-public-methods
    """
    Interface for a validator callable.
    """

    def __call__(self, value):
        """
        Determines whether the value is valid.

        Args:
            value: The value to be validated.

        Returns:
            True, if the value is valid, otherwise False.
        """
        raise NotImplementedError()


class DummyValidator(IValidator):
    # pylint: disable=too-few-public-methods
    """
    Dummy validator always returning True.
    """

    def __call__(self, value):
        # pylint: disable=unused-argument
        """
        Always returns True for all values.
        """
        return True


class IntegerValidator(IValidator):
    # pylint: disable=too-few-public-methods
    """
    Validates that values are integers.
    """

    def __call__(self, value):
        """
        Determines wether the value is an integer.

        Args:
            value: The value to be validated.

        Returns:
            True, if value is an integer, otherwise False.
        """
        if value is None:
            return False
        try:
            int(value)
        except ValueError:
            return False
        return True


class MinLengthValidator(object):
    # pylint: disable=too-few-public-methods
    """
    Validates that the value has a minimum length.
    """

    def __init__(self, min_length):
        """
        Initialised the MinLengthValidator.

        Args:
            min_length: The minimum length to be validated.
        """
        self.__min_length = min_length

    def __call__(self, value):
        """
        Validates that value has the minimum length.

        Args:
            value: The value to be validated.

        Returns:
            True, if the length of value is at least min_length.
        """
        if value is None:
            return False
        return len(value) >= self.__min_length


class RegexValidator(object):
    # pylint: disable=too-few-public-methods
    """
    Validates that a value matched a specified regular expression.
    """

    def __init__(self, pattern, flags=0):
        """
        Initialised the RegexValidator.

        Args:
            pattern: The regular expression pattern which the value must match
                to be validated.
            flags: Regular expression flags. See re.DEBUG, re.IGNORECASE,
                re.LOCALE, re.MULTILINE, re.DOTALL, re.UNICODE, re.VERBOSE.
        """
        self.__pattern = pattern
        self.__flags = flags

    def __call__(self, value):
        """
        Validates that value matches the regular expression.

        Args:
            value: The value to be validated.

        Returns:
            True, if value matches the regular expression, otherwise False.
        """
        if value is None:
            return False
        result = re.match(self.__pattern, value, self.__flags)
        return result is not None
