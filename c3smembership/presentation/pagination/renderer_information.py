# -*- coding: utf-8 -*-
"""
Provides a class to hand over pagination information to renderers.
"""


class RendererInformation(object):
    """
    Provides pagination information for renderers.

    The purpose of this class is to provide all relevant pagination information
    to renderers via one single object.
    """

    def __init__(self, url_builder, paging, sorting):
        """
        Initialises the RendererInformation object.

        Args:
            url_builder: a url_building.UrlBuilder objects.
            paging: a pagination.Paging object.
            sorting: a pagination.Sorting object.
        """
        self._url_builder = url_builder
        self._paging = paging
        self._sorting = sorting

    @property
    def url(self):
        """
        Gets the URL builder to generate URLs for links and forms.
        """
        return self._url_builder

    @property
    def paging(self):
        """
        Gets paging information like page number and size.
        """
        return self._paging

    @property
    def sorting(self):
        """
        Gest sorting information like sort property and sort direction.
        """
        return self._sorting
