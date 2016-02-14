# -*- coding: utf-8 -*-
"""
"""

from unittest import TestCase
from c3smembership.presentation.pagination.exceptions import (
    PageNotFoundException,
)
from c3smembership.presentation.pagination.pagination import (
    Pagination,
    PaginationRequest,
    Paging,
    PagingIterator,
    PagingRequest,
    Sorting,
)


class PagingRequestTest(TestCase):

    def test_constructor(self):
        # page size must not be 0
        with self.assertRaises(ValueError):
            PagingRequest(1, 0)
        # page number must be > 0
        with self.assertRaises(ValueError):
            PagingRequest(0, 1)
        # page size must be of type int
        with self.assertRaises(TypeError):
            PagingRequest(1, '1')
        # page number must be of type int
        with self.assertRaises(TypeError):
            PagingRequest('1', 1)
        pagination = PagingRequest(1, 1)
        self.assertTrue(pagination is not None)
        pagination = PagingRequest(10, 10)
        self.assertTrue(pagination is not None)

    def test_page_number(self):
        pagination = PagingRequest(2, 5)
        self.assertEqual(pagination.page_number, 2)

    def test_page_size(self):
        pagination = PagingRequest(2, 5)
        self.assertEqual(pagination.page_size, 5)

    def test_content_offset(self):
        pagination = PagingRequest(2, 1)
        self.assertEqual(pagination.content_offset, 1)
        pagination = PagingRequest(1, 5)
        self.assertEqual(pagination.content_offset, 0)
        pagination = PagingRequest(2, 5)
        self.assertEqual(pagination.content_offset, 5)
        pagination = PagingRequest(1, 30)
        self.assertEqual(pagination.content_offset, 0)

    def test_is_valid_content_size_page(self):
        pagination = PagingRequest(1, 1)
        self.assertTrue(pagination.is_valid_content_size_page(0))
        pagination = PagingRequest(2, 1)
        self.assertFalse(pagination.is_valid_content_size_page(0))
        pagination = PagingRequest(5, 1)
        self.assertTrue(pagination.is_valid_content_size_page(5))
        pagination = PagingRequest(6, 1)
        self.assertFalse(pagination.is_valid_content_size_page(5))
        pagination = PagingRequest(5, 10)
        self.assertTrue(pagination.is_valid_content_size_page(70))
        pagination = PagingRequest(8, 10)
        self.assertFalse(pagination.is_valid_content_size_page(70))
        pagination = PagingRequest(8, 10)
        self.assertTrue(pagination.is_valid_content_size_page(71))


class PagingTest(TestCase):

    def test_constructor(self):
        # page size must be larger than 0
        with self.assertRaises(ValueError):
            Paging(-1, PagingRequest(1, 1))
        # page size must be of type int
        with self.assertRaises(TypeError):
            Paging('1', PagingRequest(1, 1))
        # page number must be valid
        with self.assertRaises(PageNotFoundException):
            Paging(2, PagingRequest(3, 1))
        paging = Paging(0, PagingRequest(1, 1))
        paging = Paging(10, PagingRequest(1, 1))
        self.assertTrue(paging is not None)

    def test_content_size(self):
        paging = Paging(10, PagingRequest(2, 5))
        self.assertEqual(paging.content_size, 10)

    def test_page_count(self):
        paging = Paging(15, PagingRequest(1, 5))
        self.assertTrue(paging.page_count, 5)

    def test_next_page(self):
        paging = Paging(15, PagingRequest(2, 5))
        paging = paging.next_page
        self.assertEqual(paging.content_size, 15)
        self.assertEqual(paging.page_number, 3)
        self.assertEqual(paging.page_size, 5)
        paging = Paging(3, PagingRequest(3, 1))

        with self.assertRaises(PageNotFoundException) as raise_context:
            next_page = paging.next_page
            del(next_page)
        self.assertEqual(
            str(raise_context.exception),
            'A next page does not exist.')

    def test_previous_page(self):
        paging = Paging(15, PagingRequest(2, 5))
        paging = paging.previous_page
        self.assertEqual(paging.content_size, 15)
        self.assertEqual(paging.page_number, 1)
        self.assertEqual(paging.page_size, 5)
        paging = Paging(3, PagingRequest(1, 1))

        with self.assertRaises(PageNotFoundException) as raise_context:
            previous_page = paging.previous_page
            del(previous_page)
        self.assertEqual(
            str(raise_context.exception),
            'A previous page does not exist.')

    def test_page(self):
        paging = Paging(3, PagingRequest(1, 1))
        paging = paging.page(2)
        self.assertEqual(paging.content_size, 3)
        self.assertEqual(paging.page_number, 2)
        self.assertEqual(paging.page_size, 1)

        with self.assertRaises(PageNotFoundException) as raise_context:
            paging.page(4)
        self.assertEqual(
            str(raise_context.exception),
            'Page 4 does not exist.')

        with self.assertRaises(PageNotFoundException) as raise_context:
            paging.page(0)
        self.assertEqual(
            str(raise_context.exception),
            'Page 0 does not exist.')

        with self.assertRaises(PageNotFoundException) as raise_context:
            paging.page(-1)
        self.assertEqual(
            str(raise_context.exception),
            'Page -1 does not exist.')

    def test_first_page(self):
        paging = Paging(3, PagingRequest(2, 1))
        paging = paging.first_page
        self.assertEqual(paging.content_size, 3)
        self.assertEqual(paging.page_number, 1)
        self.assertEqual(paging.page_size, 1)

    def test_last_page(self):
        paging = Paging(3, PagingRequest(2, 1))
        paging = paging.last_page
        self.assertEqual(paging.content_size, 3)
        self.assertEqual(paging.page_number, 3)
        self.assertEqual(paging.page_size, 1)

    def test_is_first_page(self):
        paging = Paging(3, PagingRequest(2, 1))
        self.assertFalse(paging.is_first_page)
        paging = Paging(3, PagingRequest(1, 1))
        self.assertTrue(paging.is_first_page)
        paging = Paging(0, PagingRequest(1, 1))
        self.assertTrue(paging.is_first_page)

    def test_is_last_page(self):
        paging = Paging(3, PagingRequest(2, 1))
        self.assertFalse(paging.is_last_page)
        paging = Paging(3, PagingRequest(3, 1))
        self.assertTrue(paging.is_last_page)
        paging = Paging(0, PagingRequest(1, 1))
        self.assertTrue(paging.is_last_page)

    def test_has_page(self):
        paging = Paging(15, PagingRequest(1, 3))
        self.assertTrue(paging.has_page(1))
        self.assertTrue(paging.has_page(5))
        self.assertFalse(paging.has_page(6))
        paging = Paging(16, PagingRequest(1, 5))
        self.assertTrue(paging.has_page(4))
        self.assertFalse(paging.has_page(5))
        paging = Paging(0, PagingRequest(1, 5))
        self.assertTrue(paging.has_page(1))

    def test_has_next_page(self):
        paging = Paging(16, PagingRequest(1, 3))
        self.assertTrue(paging.has_next_page)
        paging = Paging(16, PagingRequest(5, 3))
        self.assertTrue(paging.has_next_page)
        paging = Paging(16, PagingRequest(6, 3))
        self.assertFalse(paging.has_next_page)

    def test_has_previous_page(self):
        paging = Paging(16, PagingRequest(1, 3))
        self.assertFalse(paging.has_previous_page)
        paging = Paging(16, PagingRequest(2, 3))
        self.assertTrue(paging.has_previous_page)

    def test_iterator(self):
        # pylint: disable=unused-variable
        paging = Paging(16, PagingRequest(1, 3))
        i = 0
        for page in paging:
            i += 1
        self.assertEqual(i, 6)

        paging = Paging(1, PagingRequest(1, 1))
        i = 0
        for page in paging:
            i += 1
        self.assertEqual(i, 1)

        paging = Paging(19, PagingRequest(2, 5))
        i = 1
        for page in paging:
            i += 1
        self.assertEqual(i, 4)

        # expect one (empty) page for no content
        paging = Paging(0, PagingRequest(1, 1))
        i = 0
        for page in paging:
            i += 1
        self.assertEqual(i, 1)


class SortingTest(TestCase):

    def test_constructor(self):
        sorting = Sorting('id', 'asc')
        self.assertTrue(sorting is not None)

    def test_sort_property(self):
        sorting = Sorting('id', 'asc')
        self.assertEqual(sorting.sort_property, 'id')

    def test_sort_direction(self):
        sorting = Sorting('id', 'asc')
        self.assertEqual(sorting.sort_direction, 'asc')


class PaginationRequestTest(TestCase):

    def test_paging_request(self):
        paging_request = PagingRequest(3, 10)
        pagination_request = PaginationRequest(
            paging_request,
            None)
        self.assertEqual(pagination_request.paging_request, paging_request)

    def test_sorting(self):
        sorting = Sorting('id', 'desc')
        view_pagination = PaginationRequest(
            None,
            sorting)
        self.assertEqual(view_pagination.sorting, sorting)


class PaginationTest(TestCase):

    def test_paging(self):
        paging_request = PagingRequest(3, 10)
        paging = Paging(50, paging_request)
        view_pagination = Pagination(
            paging,
            None)
        self.assertEqual(view_pagination.paging, paging)

    def test_sorting(self):
        sorting = Sorting('id', 'desc')
        view_pagination = Pagination(
            None,
            sorting)
        self.assertEqual(view_pagination.sorting, sorting)


class TestPagingIterator(TestCase):

    @classmethod
    def _create_paging(cls, page_number, page_size, content_size):
        paging_request = PagingRequest(page_number, page_size)
        paging = Paging(content_size, paging_request)
        return paging

    def test_next(self):
        # pylint: disable=unused-variable
        paging = self._create_paging(3, 10, 50)
        i = 2
        for page in paging:
            i += 1
        self.assertEqual(i, 5)

    def test_iterator(self):
        # pylint: disable=unused-variable
        paging = self._create_paging(3, 10, 50)
        iterator = PagingIterator(paging)
        i = 2
        for page in iterator:
            i += 1
        self.assertEqual(i, 5)
