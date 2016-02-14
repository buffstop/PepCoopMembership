# -*- coding: utf-8 -*-
"""
"""

from unittest import TestCase
from pyramid import testing
from c3smembership.presentation.pagination.reading import (
    RequestPaginationReader,
    DefaultReader,
    IPaginationReader,
    IReader,
    RequestCookieReader,
    RequestMatchdictReader,
    RequestParamReader,
    RequestPostReader,
    StrategyReader,
)
from c3smembership.presentation.pagination.exceptions import (
    PageNotFoundException
)
from mocking import (
    MockReader,
    RouteMock,
    PropertyNamingMock,
    ValidatorMock,
)


class IReaderTest(TestCase):

    def test_call(self):
        reader = IReader()
        with self.assertRaises(NotImplementedError):
            reader()


class RequestCookieReaderTest(TestCase):

    def test_read(self):
        request = testing.DummyRequest()
        reader = RequestCookieReader(request, 'some_cookie')
        self.assertTrue(reader() is None)

        # use cookie
        request = testing.DummyRequest()
        request.cookies['some_cookie'] = 123
        reader = RequestCookieReader(request, 'some_cookie')
        self.assertEqual(reader(), 123)


class RequestPostReaderTest(TestCase):

    def test_read(self):
        request = testing.DummyRequest()
        reader = RequestPostReader(request, 'post_key')
        self.assertTrue(reader() is None)

        # POST
        request = testing.DummyRequest()
        request.POST['post_key'] = '123'
        reader = RequestPostReader(request, 'post_key')
        self.assertEqual(reader(), '123')


class RequestMatchdictReaderTest(TestCase):

    def test_read(self):
        request = testing.DummyRequest()
        reader = RequestMatchdictReader(request, 'matchdict_key')
        self.assertTrue(reader() is None)

        # match
        request = testing.DummyRequest()
        request.matchdict['matchdict_key'] = '123'
        reader = RequestMatchdictReader(request, 'matchdict_key')
        self.assertEqual(reader(), '123')


class DefaultReaderTest(TestCase):

    def test_read(self):
        reader = DefaultReader('id')
        self.assertEqual(reader(), 'id')


class StrategyReaderTest(TestCase):

    def test_read(self):
        reader = StrategyReader(
            [],
            ValidatorMock(0))
        self.assertTrue(reader() is None)

        reader = StrategyReader(
            [MockReader(None)],
            ValidatorMock(1))
        self.assertTrue(reader() is None)

        reader = StrategyReader(
            [
                MockReader(None),
                MockReader(None),
                MockReader('test')
            ],
            ValidatorMock(3))
        self.assertEqual(reader(), 'test')


class RequestParamReaderTest(TestCase):

    def test_read(self):
        request = testing.DummyRequest()
        request.params['test'] = 'some_value'
        reader = RequestParamReader(request, 'test')
        self.assertEqual(reader(), 'some_value')
        reader = RequestParamReader(request, 'test2')
        self.assertTrue(reader() is None)


class IPaginationReaderTest(TestCase):

    def test_call(self):
        reader = IPaginationReader()
        with self.assertRaises(NotImplementedError):
            reader('request', 'content_size')


class RequestPaginationReaderTest(TestCase):

    def setUp(self):
        self.reader = RequestPaginationReader(
            PropertyNamingMock(
                'post_page_number',
                'post_page_size',
                'post_sort_property',
                'post_sort_direction'
            ),
            PropertyNamingMock(
                'param_page_number',
                'param_page_size',
                'param_sort_property',
                'param_sort_direction'
            ),
            PropertyNamingMock(
                'cookie_page_number',
                'cookie_page_size',
                'cookie_sort_property',
                'cookie_sort_direction'
            )
        )

    @classmethod
    def make_request(cls, post=None):
        request = testing.DummyRequest(post=post)
        request.matched_route = RouteMock('dummy_route')
        request.registry.pagination = {
            'dummy_route': {
                'sort_property_default': 'some_property',
                'page_size_default': 123,
                'sort_direction_default': 'asc',
                'page_number_default': 1,
            }
        }
        return request

    @classmethod
    def set_dict(cls, dictionary, prefix, page_number, page_size, sort_property,
                 sort_direction):
        # pylint: disable=too-many-arguments
        dictionary['{0}page_number'.format(prefix)] = page_number
        dictionary['{0}page_size'.format(prefix)] = page_size
        dictionary['{0}sort_property'.format(prefix)] = sort_property
        dictionary['{0}sort_direction'.format(prefix)] = sort_direction

    def test_call_defaults(self):
        request = self.make_request()
        content_size = 50
        pagination = self.reader(request, content_size)
        self.assertEqual(pagination.paging.page_number, 1)
        self.assertEqual(pagination.paging.page_size, 123)
        self.assertEqual(pagination.sorting.sort_property, 'some_property')
        self.assertEqual(pagination.sorting.sort_direction, 'asc')

    def test_call_post(self):
        content_size = 50
        request = self.make_request({
            'post_page_size': 7,
            'post_page_number': 8,
            'post_sort_property': 'post_property',
            'post_sort_direction': 'desc',
        })
        self.set_dict(request.params, 'param_', 2, 21, 'some_other_property',
                      'asc')
        pagination = self.reader(request, content_size)
        self.assertEqual(pagination.paging.page_number, 8)
        self.assertEqual(pagination.paging.page_size, 7)
        self.assertEqual(pagination.sorting.sort_property, 'post_property')
        self.assertEqual(pagination.sorting.sort_direction, 'desc')

    def test_call_params(self):
        content_size = 50
        request = self.make_request()
        self.set_dict(request.cookies, 'cookie_', 3, 22, 'some_cookie_property',
                      'asc')
        self.set_dict(request.params, 'param_', 2, 21, 'some_other_property',
                      'desc')
        pagination = self.reader(request, content_size)
        self.assertEqual(pagination.paging.page_number, 2)
        self.assertEqual(pagination.paging.page_size, 21)
        self.assertEqual(
            pagination.sorting.sort_property,
            'some_other_property')
        self.assertEqual(pagination.sorting.sort_direction, 'desc')

    def test_call_cookies(self):
        content_size = 50
        request = self.make_request()
        self.set_dict(request.cookies, 'cookie_', 3, 22, 'some_cookie_property',
                      'desc')
        pagination = self.reader(request, content_size)
        self.assertEqual(pagination.paging.page_number, 3)
        self.assertEqual(pagination.paging.page_size, 22)
        self.assertEqual(
            pagination.sorting.sort_property,
            'some_cookie_property')
        self.assertEqual(pagination.sorting.sort_direction, 'desc')

    def test_call_exceptions(self):
        request = self.make_request()
        with self.assertRaises(PageNotFoundException):
            self.reader(request, 'asdf')
