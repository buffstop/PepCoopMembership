# -*- coding: utf-8 -*-
"""
Provides functionality for reading information in a flexible way.
"""

from .exceptions import (
    PageNotFoundException
)
from .pagination import (
    Pagination,
    Paging,
    PagingRequest,
    Sorting,
)
from .validation import (
    IntegerValidator,
    MinLengthValidator,
    RegexValidator,
)


class IReader(object):
    # pylint: disable=too-few-public-methods
    """
    Interface specifying a reader callable.

    Classes implementing this interface must overwrite the __call__ method and
    conform to its specification.

    Reader callables can also be explicitly declared as function.
    """

    def __call__(self):
        """
        Returns the read content.
        """
        raise NotImplementedError()


class StrategyReader(object):
    # pylint: disable=too-few-public-methods
    """
    The strategy reader contains a list of readers and a valitator. It tries
    on reader after another until one returns content which is valid according
    to the validator.
    """

    def __init__(self, readers, validator):
        """
        Initialises the ``StrategyReader``.

        Args:
            readers: A iterator providing readers.
            validator: A validator which is used to validate the content of the
                readers.
        """
        self.__readers = readers
        self.__validator = validator

    def __call__(self):
        """
        Return the content of the first reader having valid content.
        """
        for reader in self.__readers:
            read_object = reader()
            if self.__validator(read_object):
                return read_object
        return None


class DefaultReader(IReader):
    # pylint: disable=too-few-public-methods
    """
    Reads a default value.
    """

    def __init__(self, default_value):
        """
        Initialises the ``DefaultReader``.

        Args:
            default_value: The default value to be returned by the __call__
                method.
        """
        self.__default_value = default_value

    def __call__(self):
        """
        Returns the default value specified in the constructor.
        """
        return self.__default_value


class RequestParamReader(IReader):
    # pylint: disable=too-few-public-methods
    """
    Reads a parameter value from a request.
    """

    def __init__(self, request, param_key):
        """
        Initialises the ``RequestParamReader``.

        Args:
            request: The request from which the parameter value is read.
            param_key: The name of the parameter from which the value is read.
        """
        self.__request = request
        self.__param_key = param_key

    def __call__(self):
        """
        Returns the parameter value from the request.
        """
        if self.__param_key in self.__request.params:
            return self.__request.params[self.__param_key]
        else:
            return None


class RequestPostReader(IReader):
    # pylint: disable=too-few-public-methods
    """
    Reads a POST parameter value from a request.
    """

    def __init__(self, request, post_key):
        """
        Initialises the ``RequestPostReader``.

        Args:
            request: The request from which the parameter value is read.
            post_key: The name of the POST parameter from which the value is
                read.
        """
        self.__request = request
        self.__post_key = post_key

    def __call__(self):
        """
        Returns the POST parameter value from the request.
        """
        if self.__post_key in self.__request.POST:
            return self.__request.POST[self.__post_key]
        else:
            return None


class RequestMatchdictReader(IReader):
    # pylint: disable=too-few-public-methods
    """
    Reads an URL component value from a request's matchdict.
    """

    def __init__(self, request, matchdict_key):
        """
        Initialises the ``RequestMatchdictReader``.

        Args:
            request: The request from which the URL component value is read.
            matchdict_key: The name of the URL component which is read from the
                request.
        """
        self.__request = request
        self.__matchdict_key = matchdict_key

    def __call__(self):
        """
        Returns the URL component from the request.
        """
        if self.__matchdict_key in self.__request.matchdict:
            return self.__request.matchdict[self.__matchdict_key]
        else:
            return None


class RequestCookieReader(IReader):
    # pylint: disable=too-few-public-methods
    """
    Reads a cookie value from a request.
    """

    def __init__(self, request, cookie_name):
        """
        Initialises the ``RequestCookieReader``.

        Args:
            request: The request from with the cookie value is read.
            cookie_name: The name of the cookie from which the value is read.
        """
        self.__request = request
        self.__cookie_name = cookie_name

    def __call__(self):
        """
        Returns the value of the cookie from the request.
        """
        if self.__cookie_name in self.__request.cookies:
            return self.__request.cookies[self.__cookie_name]
        else:
            return None


class IPaginationReader(object):
    # pylint: disable=too-few-public-methods
    """
    Interface specifying a pagination reader callable.

    Classes implementing this interface must overwrite the __call__ method and
    conform to its specification.

    Reader callables can also be explicitly declared as function.
    """

    def __call__(self, request, content_size):
        """
        Reads a pagination from a request.

        Args:
            request: The Pyramid request from which the pagination request is
                read.
            content_size: The size of the pagination content which in
                combination with the pagination request give the pagination.

        Returns:
            The pagination read from the request.

        Throws:
            PageNotFoundException: In case the a valid pagination cannot be
                read.
        """
        raise NotImplementedError()


class RequestPaginationReader(IPaginationReader):
    # pylint: disable=too-few-public-methods
    """
    The default pagination reader callable.

    The pagination information is determined in the following order:

    # POST parameters: If values are set via HTML forms then this information is
      preferred.
    # URL parameters: If not POST information is set for pagination then the
      URL parameters are checked for available information.
    # Cookies: As a third step cookies are checked for available pagination
      information.
    # Default values: If no information is available then default values are
      used.

    Naming property settings can be passed to the constructor using the
    ``IPropertyNaming`` interface.
    """

    def __init__(self, post_property_naming, param_property_naming,
                 cookie_property_naming):
        """
        Initialises the ``RequestPaginationReader``.

        Args:
            post_property_naming: The ``IPropertyNaming`` for POST parameters.
            param_property_naming: The ``IPropertyNaming`` for parameters.
            cookie_property_naming: The ``IPropertyNaming`` for cookies.
        """
        self._post_property_naming = post_property_naming
        self._param_property_naming = param_property_naming
        self._cookie_property_naming = cookie_property_naming
        self._settings = None

    def __call__(self, request, content_size):
        """
        Reads the pagination from the request.

        Args:
            request: The Pyramid request from which the pagination request is
                read.
            content_size: The size of the pagination content which in
                combination with the pagination request give the pagination.

        Returns:
            The pagination read from the request.

        Throws:
            PageNotFoundException: In case the a valid pagination cannot be
                read.
        """
        self._settings = self._get_route_settings(request)
        sorting = self._create_sorting(request)
        paging_request = self._create_page_request(request)
        try:
            return Pagination(
                Paging(content_size, paging_request),
                sorting)
        except (ValueError, TypeError):
            raise PageNotFoundException('Page not found.')

    @classmethod
    def _get_route_settings(cls, request):
        """
        Gets the route settings from the pagination registry.
        """
        return request.registry.pagination[request.matched_route.name]

    def _create_sort_direction_reader(self, request):
        """
        Creates the reader for the sort direction.
        """
        return StrategyReader(
            [
                RequestPostReader(
                    request,
                    self._post_property_naming.sort_direction_name
                ),
                RequestParamReader(
                    request,
                    self._param_property_naming.sort_direction_name
                ),
                RequestCookieReader(
                    request,
                    self._cookie_property_naming.sort_direction_name
                ),
                DefaultReader(self._settings['sort_direction_default'])
            ],
            RegexValidator('^asc|desc$'))

    def _create_sort_property_reader(self, request):
        """
        Creates the reader for the sort property.
        """
        return StrategyReader(
            [
                RequestPostReader(
                    request,
                    self._post_property_naming.sort_property_name
                ),
                RequestParamReader(
                    request,
                    self._param_property_naming.sort_property_name
                ),
                RequestCookieReader(
                    request,
                    self._cookie_property_naming.sort_property_name
                ),
                DefaultReader(self._settings['sort_property_default'])
            ],
            MinLengthValidator(1))

    def _create_page_size_reader(self, request):
        """
        Creates the reader for the page size.
        """
        return StrategyReader(
            [
                RequestPostReader(
                    request,
                    self._post_property_naming.page_size_name
                ),
                RequestParamReader(
                    request,
                    self._param_property_naming.page_size_name
                ),
                RequestCookieReader(
                    request,
                    self._cookie_property_naming.page_size_name
                ),
                DefaultReader(self._settings['page_size_default'])
            ],
            IntegerValidator())

    def _create_page_number_reader(self, request):
        """
        Creates the reader for the page number.
        """
        return StrategyReader(
            [
                RequestPostReader(
                    request,
                    self._post_property_naming.page_number_name
                ),
                RequestParamReader(
                    request,
                    self._param_property_naming.page_number_name
                ),
                RequestCookieReader(
                    request,
                    self._cookie_property_naming.page_number_name
                ),
                DefaultReader(self._settings['page_number_default'])
            ],
            IntegerValidator())

    def _create_sorting(self, request):
        """
        Create the sorting from the sort property and sort direction readers.
        """
        sort_direction_reader = self._create_sort_direction_reader(request)
        sort_property_reader = self._create_sort_property_reader(request)
        return Sorting(
            sort_property_reader(),
            sort_direction_reader())

    def _create_page_request(self, request):
        """
        Create the page request from the page number and page size readers.
        """
        page_size_reader = self._create_page_size_reader(request)
        page_number_reader = self._create_page_number_reader(request)
        return PagingRequest(
            int(page_number_reader()),
            int(page_size_reader()))
