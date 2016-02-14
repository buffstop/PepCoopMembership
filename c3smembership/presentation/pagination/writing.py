# -*- coding: utf-8 -*-
"""
Utilities for storing pagination settings.
"""


class ISortingWriter(object):
    # pylint: disable=too-few-public-methods
    """
    Writes sorting attributes.
    """

    def __call__(self, sorting):
        """
        Writes sorting information.

        Args:
            sorting: The sorting to be written.
        """
        raise NotImplementedError()


class CookieSortingWriter(ISortingWriter):
    # pylint: disable=too-few-public-methods
    """
    Writes sorting settings to a request cookie.
    """

    def __init__(self, request, cookie_property_naming):
        """
        Initializes the CookieSortingWriter.

        Args:
            request: The request which contains the cookie to which the sorting
                is written.
            cookie_property_naming: The property naming for cookies.
        """
        self.__request = request
        self.__cookie_property_naming = cookie_property_naming

    def __call__(self, sorting):
        """
        Writes the sorting to the request cookie.

        Args:
            sorting: The sorting to be written to the request cookie.
        """
        self.__request.response.set_cookie(
            self.__cookie_property_naming.sort_direction_name,
            value=str(sorting.sort_direction))
        self.__request.response.set_cookie(
            self.__cookie_property_naming.sort_property_name,
            value=str(sorting.sort_property))


class IPagingRequestWriter(object):
    # pylint: disable=too-few-public-methods
    """
    Writes paging request attributes.
    """

    def __call__(self, paging_request):
        """
        Writes the paging request attributes.

        Args:
            paging_request: The paging request to be written.
        """
        raise NotImplementedError()


class CookiePagingRequestWriter(IPagingRequestWriter):
    # pylint: disable=too-few-public-methods
    """
    Writes paging request to a request cookie.
    """

    def __init__(self, request, cookie_property_naming):
        """
        Initialised the CookiePagingRequestWriter.

        Args:
            request: The request which contains the cookie to which the paging
                request is written.
            cookie_property_naming: The property naming for cookies.
        """
        self.__request = request
        self.__cookie_property_naming = cookie_property_naming

    def __call__(self, paging_request):
        """
        Writes the paging request to the request cookie.

        Args:
            paging_request: The paging request to be written to the request
                cookie.
        """
        self.__request.response.set_cookie(
            self.__cookie_property_naming.page_number_name,
            value=str(paging_request.page_number))
        self.__request.response.set_cookie(
            self.__cookie_property_naming.page_size_name,
            value=str(paging_request.page_size))


class IPaginationRequestWriter(object):
    # pylint: disable=too-few-public-methods
    """
    Writes pagination request information.
    """

    def __call__(self, request, pagination_request):
        """
        Writes the pagination request to the Pyramid request.

        Args:
            request: The Pyramid request the pagination request is written to.
            pagination_request: The pagination request to be written.
        """
        raise NotImplementedError()


class DefaultPaginationRequestWriter(object):
    # pylint: disable=too-few-public-methods
    """
    Writes pagination request information.
    """

    def __init__(self, cookie_property_naming):
        """
        Initializes the DefaultPaginationRequestWriter.

        Args:
            cookie_property_naming: The property naming for the cookie.
        """
        self._cookie_property_naming = cookie_property_naming

    def __call__(self, request, pagination_request):
        """
        Writes the pagination request to the Pyramid request.

        Args:
            request: The Pyramid request the pagination request is written to.
            pagination_request: The pagination request to be written.
        """
        paging_request_writer = CookiePagingRequestWriter(
            request,
            self._cookie_property_naming)
        sorting_writer = CookieSortingWriter(
            request,
            self._cookie_property_naming)

        paging_request_writer(pagination_request.paging_request)
        sorting_writer(pagination_request.sorting)
