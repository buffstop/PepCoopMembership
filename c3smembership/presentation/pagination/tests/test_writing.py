# -*- coding: utf-8 -*-
"""
"""

from unittest import TestCase
from pyramid.testing import DummyRequest
from c3smembership.presentation.pagination.pagination import (
    PagingRequest,
    Sorting,
    PaginationRequest,
)
from c3smembership.presentation.pagination.writing import (
    CookiePagingRequestWriter,
    CookieSortingWriter,
    DefaultPaginationRequestWriter,
    IPaginationRequestWriter,
    IPagingRequestWriter,
    ISortingWriter,
)
from mocking import (
    ResponseMock,
    PropertyNamingMock,
)


class TestISortingWriter(TestCase):

    def test_call(self):
        writer = ISortingWriter()
        with self.assertRaises(NotImplementedError):
            writer('sorting')


class CookieSortingWriterTest(TestCase):

    def test_write(self):
        request = DummyRequest()
        response_mock = ResponseMock()
        request.response = response_mock
        sorting = Sorting('id', 'desc')
        sorting_writer = CookieSortingWriter(
            request,
            PropertyNamingMock(
                'page_number',
                'page_size',
                'sort_property',
                'sort_direction'
            )
        )
        sorting_writer(sorting)
        self.assertEqual(response_mock.get_cookie('sort_property'), 'id')
        self.assertEqual(response_mock.get_cookie('sort_direction'), 'desc')
        self.assertEqual(response_mock.call_count(), 2)

        request = DummyRequest()
        response_mock = ResponseMock()
        request.response = response_mock
        sorting = Sorting('id', 'desc')
        sorting_writer = CookieSortingWriter(
            request,
            PropertyNamingMock(
                'cookie_prefix.page_number',
                'cookie_prefix.page_size',
                'cookie_prefix.sort_property',
                'cookie_prefix.sort_direction'
            )
        )
        sorting_writer(sorting)
        self.assertEqual(response_mock.get_cookie('cookie_prefix.sort_property'), 'id')
        self.assertEqual(response_mock.get_cookie('cookie_prefix.sort_direction'), 'desc')
        self.assertEqual(response_mock.call_count(), 2)


class IPagingRequestWriterTest(TestCase):

    def test_call(self):
        writer = IPagingRequestWriter()
        with self.assertRaises(NotImplementedError):
            writer('paging request')


class CookiePagingRequestWriterTest(TestCase):

    def test_write(self):
        request = DummyRequest()
        response_mock = ResponseMock()
        request.response = response_mock
        pagination_request = PagingRequest(3, 12)
        pagination_request_writer = CookiePagingRequestWriter(
            request,
            PropertyNamingMock(
                'page_number',
                'page_size',
                'sort_property',
                'sort_direction'
            )
        )
        pagination_request_writer(pagination_request)
        self.assertEqual(response_mock.get_cookie('page_number'), '3')
        self.assertEqual(response_mock.get_cookie('page_size'), '12')
        self.assertEqual(response_mock.call_count(), 2)


class IPaginationRequestWriterTest(TestCase):

    def test_call(self):
        writer = IPaginationRequestWriter()
        with self.assertRaises(NotImplementedError):
            writer('request', 'pagination request')


class DefaultPaginationRequestWriterTest(TestCase):

    def test_call(self):
        writer = DefaultPaginationRequestWriter(
            PropertyNamingMock(
                'cookie_prefix.page_number',
                'cookie_prefix.page_size',
                'cookie_prefix.sort_property',
                'cookie_prefix.sort_direction'
            )
        )
        request = DummyRequest()
        request.response = ResponseMock()
        pagination_request = PaginationRequest(
            PagingRequest(3, 24),
            Sorting('some_sort_property', 'desc'))
        writer(request, pagination_request)

        self.assertEqual(
            request.response.get_cookie('cookie_prefix.page_number'),
            '3')
        self.assertEqual(
            request.response.get_cookie('cookie_prefix.page_size'),
            '24')
        self.assertEqual(
            request.response.get_cookie('cookie_prefix.sort_property'),
            'some_sort_property')
        self.assertEqual(
            request.response.get_cookie('cookie_prefix.sort_direction'),
            'desc')
