# -*- coding: utf-8 -*-
"""
"""

from unittest import TestCase
from c3smembership.presentation.pagination.pagination import (
    Pagination,
    Paging,
    PagingRequest,
    Sorting,
    PaginationRequest,
)
from c3smembership.presentation.pagination.url_building import (
    IUrlCreator,
    IUrlCreatorFactory,
    RequestUrlCreator,
    RequestUrlCreatorFactory,
    UrlBuilder,
)
from mocking import (
    PropertyNamingMock,
    UrlCreatorMock,
)
from pyramid import testing
from pyramid.testing import DummyRequest



class IUrlCreatorTest(TestCase):

    def test_create_url(self):
        pagination_url_creator = IUrlCreator()
        with self.assertRaises(NotImplementedError):
            pagination_url_creator(None, None)


class RequestUrlCreatorTest(TestCase):

    def test_create_url(self):
        config = testing.setUp()
        config.add_route('route_name', 'route_name')
        request = DummyRequest()
        property_naming = PropertyNamingMock(
            'page-number',
            'page-size',
            'sort-property',
            'sort-direction')
        pagination_url_creator = RequestUrlCreator(
            request,
            'route_name',
            property_naming,
        )
        url = pagination_url_creator(
            PaginationRequest(
                PagingRequest(3, 10),
                Sorting('id', 'desc')))
        self.assertTrue(url.find('http://example.com/route_name') == 0)
        self.assertTrue(url.find('page-number=3') > 0)
        self.assertTrue(url.find('page-size=10') > 0)
        self.assertTrue(url.find('sort-property=id') > 0)
        self.assertTrue(url.find('sort-direction=desc') > 0)

        config.add_route('match_route', 'match_route/{page_number}')
        request = DummyRequest()
        request.matchdict['page_number'] = 'some_page'
        request.params['test'] = 'some_value'
        pagination_url_creator = RequestUrlCreator(
            request,
            'match_route',
            property_naming,
        )
        url = pagination_url_creator(
            PaginationRequest(
                PagingRequest(3, 10),
                Sorting('id', 'desc')))
        self.assertTrue(url.find('match_route/some_page') > 0)
        self.assertTrue(url.find('test=some_value') > 0)


class IUrlCreatorFactoryTest(TestCase):

    def test_call(self):
        creator_factory = IUrlCreatorFactory()
        with self.assertRaises(NotImplementedError):
            creator_factory(None, None)


class RequestUrlCreatorFactoryTest(TestCase):

    def test_call(self):
        request_dummy = DummyRequest()
        property_naming = PropertyNamingMock(
            'page-number',
            'page-size',
            'sort-property',
            'sort-direction')
        creator_factory = RequestUrlCreatorFactory(property_naming)
        url_creator = creator_factory(
            request_dummy,
            'route_name')
        self.assertTrue(isinstance(url_creator, IUrlCreator))


class UrlBuilderTest(TestCase):

    def test_pagination(self):
        pagination = Pagination('paging', 'sorting')
        provider = UrlBuilder(None, pagination)
        self.assertEqual(pagination, provider.pagination)

    def test_sort_direction(self):
        sorting = Sorting('id', 'desc')
        provider = UrlBuilder(None, Pagination(None, sorting))
        sort_direction_provider = provider.sort_direction('asc')
        self.assertEqual(
            sort_direction_provider.pagination.sorting.sort_property,
            'id')
        self.assertEqual(
            sort_direction_provider.pagination.sorting.sort_direction,
            'asc')

        sort_property_provider = provider.sort_property('name')
        self.assertEqual(
            sort_property_provider.pagination.sorting.sort_direction,
            'desc')
        self.assertEqual(
            sort_property_provider.pagination.sorting.sort_property,
            'name')

    def assert_equal_paging(self, provider, content_size, page_number,
                            page_size):
        self.assertEqual(
            provider.pagination.paging.page_number,
            page_number)
        self.assertEqual(
            provider.pagination.paging.page_size,
            page_size)
        self.assertEqual(
            provider.pagination.paging.content_size,
            content_size)

    def assert_equal_sorting(self, provider, sort_property, sort_direction):
        self.assertEqual(
            provider.pagination.sorting.sort_property,
            sort_property)
        self.assertEqual(
            provider.pagination.sorting.sort_direction,
            sort_direction)

    @classmethod
    def get_response_provider(cls, content_size, page_number, page_size):
        return UrlBuilder(
            UrlCreatorMock('http://example.com/test/url'),
            Pagination(
                Paging(
                    content_size,
                    PagingRequest(page_number, page_size)),
                Sorting('id', 'desc')))

    def test_first_page(self):
        provider = self.get_response_provider(123, 3, 21)
        first_page_provider = provider.first_page
        self.assert_equal_paging(first_page_provider, 123, 1, 21)
        self.assert_sorting_equals(first_page_provider, provider)
        self.assertEqual(
            first_page_provider.url,
            'http://example.com/test/url')

    def test_last_page(self):
        provider = self.get_response_provider(123, 3, 21)
        last_page_provider = provider.last_page
        self.assert_equal_paging(last_page_provider, 123, 6, 21)
        self.assert_sorting_equals(last_page_provider, provider)
        self.assertEqual(
            last_page_provider.url,
            'http://example.com/test/url')

    def assert_sorting_equals(self, provider1, provider2):
        self.assertEqual(
            provider1.pagination.sorting.sort_property,
            provider2.pagination.sorting.sort_property)
        self.assertEqual(
            provider1.pagination.sorting.sort_direction,
            provider2.pagination.sorting.sort_direction)

    def test_previous_page(self):
        provider = self.get_response_provider(123, 3, 21)
        previous_page_provider = provider.previous_page
        self.assert_equal_paging(previous_page_provider, 123, 2, 21)
        self.assert_sorting_equals(previous_page_provider, provider)
        self.assertEqual(
            previous_page_provider.url,
            'http://example.com/test/url')

    def test_next_page(self):
        provider = self.get_response_provider(123, 3, 21)
        next_page_provider = provider.next_page
        self.assert_equal_paging(next_page_provider, 123, 4, 21)
        self.assert_sorting_equals(next_page_provider, provider)
        self.assertEqual(
            next_page_provider.url,
            'http://example.com/test/url')

    def test_invert_sort_direction(self):
        provider = self.get_response_provider(123, 3, 21)
        inverted = provider.invert_sort_direction
        self.assert_equal_paging(inverted, 123, 3, 21)
        self.assert_equal_sorting(inverted, 'id', 'asc')
        self.assertEqual(inverted.url, 'http://example.com/test/url')

        twice_inverted = inverted.invert_sort_direction
        self.assert_equal_paging(twice_inverted, 123, 3, 21)
        self.assert_equal_sorting(twice_inverted, 'id', 'desc')
        self.assertEqual(twice_inverted.url, 'http://example.com/test/url')

    def test_sort_property_alternating_direction(self):
        provider = self.get_response_provider(123, 3, 21)

        provider = provider.sort_direction('asc')

        # different sort property must be ascending
        alternating = provider.sort_property_alternating_direction('sortprop')
        self.assert_equal_paging(alternating, 123, 3, 21)
        self.assert_equal_sorting(alternating, 'sortprop', 'asc')
        self.assertEqual(alternating.url, 'http://example.com/test/url')

        # same sort property must be other sort direction: asc -> desc
        alternating = provider.sort_property_alternating_direction('id')
        self.assert_equal_paging(alternating, 123, 3, 21)
        self.assert_equal_sorting(alternating, 'id', 'desc')
        self.assertEqual(alternating.url, 'http://example.com/test/url')

        provider = provider.sort_direction('desc')

        # different sort property must be ascending
        alternating = provider.sort_property_alternating_direction('sortprop')
        self.assert_equal_paging(alternating, 123, 3, 21)
        self.assert_equal_sorting(alternating, 'sortprop', 'asc')
        self.assertEqual(alternating.url, 'http://example.com/test/url')

        # same sort property must be other sort direction: desc -> asc
        alternating = provider.sort_property_alternating_direction('id')
        self.assert_equal_paging(alternating, 123, 3, 21)
        self.assert_equal_sorting(alternating, 'id', 'asc')
        self.assertEqual(alternating.url, 'http://example.com/test/url')

    def test_str(self):
        provider = self.get_response_provider(123, 3, 21)
        self.assertEqual(str(provider), 'http://example.com/test/url')
