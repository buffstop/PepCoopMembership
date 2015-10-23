"""
This module holds the error view.

It can be used from any other view, e.g. by way of redirection in case of
some error. Info stored in session can be displayed here (see template).
"""

from pyramid.view import view_config


@view_config(
    renderer='templates/error_page.pt',
    route_name='error_page',
)
def error_view(request):
    """
    display error stored in session.
    """
    return {'foo': 'bar'}  # return dumb dictionary; info is in session.
