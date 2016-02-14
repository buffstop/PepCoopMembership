# -*- coding: utf-8 -*-
"""
Property namings are used in order to configure the names of parameters of
route URLs.
"""


class IPagingPropertyNaming(object):
    """
    Provides names for the paging properties page number and page size.
    """

    @property
    def page_number_name(self):
        """
        The page number property name.
        """
        raise NotImplementedError()

    @property
    def page_size_name(self):
        """
        The page size property name.
        """
        raise NotImplementedError()


class ISortingPropertyNaming(object):
    """
    Provides names for the sorting properties sort property and sort direction.
    """

    @property
    def sort_property_name(self):
        """
        The sort property property name.
        """
        raise NotImplementedError()

    @property
    def sort_direction_name(self):
        """
        The sort direction property name.
        """
        raise NotImplementedError()


class IPropertyNaming(IPagingPropertyNaming, ISortingPropertyNaming):
    # pylint: disable=abstract-method
    """
    Provides names for the paging and sorting properties.
    """
    pass


class PropertyNaming(IPropertyNaming):
    """
    Provides names for the paging and sorting properties.
    """

    def __init__(
            self,
            page_number_name,
            page_size_name,
            sort_property_name,
            sort_direction_name,
            name_format='{property_name}'):
        # pylint: disable=too-many-arguments
        """
        Initializes the property naming.

        All names can be formatted using the name_format argument.

        Args:
            page_number_name: The page number property name.
            page_size_name: The page size property name.
            sort_property_name: The sort property property name.
            sort_direction_name: The sort direction property name.
            name_format: Optional. Can be used to format all property names
                using the string.format formatting pattern. The the format
                string must contain '{property_name}'. E.g. all property names
                can be prefixed using 'prefix.{property_name}'.
        """
        self._name_format = name_format
        self._page_number_name = self._format(page_number_name)
        self._page_size_name = self._format(page_size_name)
        self._sort_property_name = self._format(sort_property_name)
        self._sort_direction_name = self._format(sort_direction_name)

    def _format(self, value):
        """
        Formats the value.

        Args:
            value: The value to be formatted.

        Returns:
            The formatted value as a string.
        """
        return self._name_format.format(property_name=value)

    @property
    def page_number_name(self):
        """
        The page number property name.
        """
        return self._page_number_name

    @property
    def page_size_name(self):
        """
        The page size property name.
        """
        return self._page_size_name

    @property
    def sort_property_name(self):
        """
        The sort property property name.
        """
        return self._sort_property_name

    @property
    def sort_direction_name(self):
        """
        The sort direction property name.
        """
        return self._sort_direction_name
