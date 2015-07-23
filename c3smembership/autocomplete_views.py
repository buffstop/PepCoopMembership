"""
This module holds two view functions used by the Search pages
featuring autocomplete (see toolbox):

- Search for People
- Search for Codes

When these forms are used to find an application either by code or by lastname,
the given prefix (the alphanumeric characters) is sent to the relevant view,
which then returnd JSON to power the autocomplete functionality.
"""

from pyramid.view import view_config
from c3smembership.models import C3sMember


# aotucomplete reference code search
@view_config(renderer='json',
             permission='manage',
             route_name='autocomplete_input_values')
def autocomplete_input_values(request):
    '''
    AJAX view/helper function
    returns the matching set of values for autocomplete/quicksearch

    this function and view expects a parameter 'term' (?term=foo) containing a
    string to find matching entries (e.g. starting with 'foo') in the database
    '''
    text = request.params.get('term', '')
    return C3sMember.get_matching_codes(text)


# autocomplete people search
@view_config(renderer='json',
             permission='manage',
             route_name='autocomplete_people_search')
def autocomplete_people_search(request):
    '''
    AJAX view/helper function
    returns the matching set of values for autocomplete/quicksearch

    this function and view expects a parameter 'term' (?term=foo) containing a
    string to find matching entries (e.g. starting with 'foo') in the database
    '''
    text = request.params.get('term', '')
    #print u"DEBUG: autocomp. people search for: {}".format(text)
    return C3sMember.get_matching_people(text)
