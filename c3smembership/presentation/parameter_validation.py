# -*- coding: utf-8 -*-


class ParameterValidationException(Exception):

    def __init__(self, message, redirect_url):
        super(ParameterValidationException, self).__init__(message)
        self.__redirect_url = redirect_url

    @property
    def redirect_url(self):
        return self.__redirect_url
