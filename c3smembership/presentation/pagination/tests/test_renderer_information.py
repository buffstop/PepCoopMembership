# -*- coding: utf-8 -*-
"""
"""


from unittest import TestCase
from c3smembership.presentation.pagination.renderer_information import (
    RendererInformation
)


class RendererInformationTest(TestCase):

    def test_all(self):
        renderer_information = RendererInformation(
            'url_builder',
            'paging',
            'sorting')

        self.assertEqual(renderer_information.url, 'url_builder')
        self.assertEqual(renderer_information.paging, 'paging')
        self.assertEqual(renderer_information.sorting, 'sorting')
