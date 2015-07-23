# -*- coding: utf-8 -*-
"""
This module holds some search functionality:

- Search for People (by lastname, with auto complete)
- Search for Reference Codes (with auto complete)

Buttons with links to the search views are placed in the toolbox.
"""
import colander
import deform

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from c3smembership.models import C3sMember


@view_config(route_name='search_people',
             renderer='templates/search_people.pt',
             permission='manage')
def search_people(request):
    '''
    Search for people.

    We use a form with autocomplete to let staff find entries faster.
    '''
    # check for input from "find people" form
    if 'code_to_show' in request.POST:
        try:
            _code = request.POST['code_to_show']
            # print u"_code = {}".format(_code)
            _code_ = _code.split(' ')[0]
            # print u"_code_ = {}".format(_code_)
            _entry = C3sMember.get_by_code(_code_)

            return HTTPFound(
                location=request.route_url(
                    'detail',
                    memberid=_entry.id)
            )
        except:
            pass

    class AutocompleteForm(colander.MappingSchema):
        code_to_show = colander.SchemaNode(
            colander.String(),
            title='Personen finden (Nachname: Groß-/Kleinschr. beachten!)',
            widget=deform.widget.AutocompleteInputWidget(
                min_length=1,
                css_class="form-inline",
                values=request.route_path(
                    'autocomplete_people_search',
                    traverse=('autocomplete_people_search')
                )
            )
        )

    schema = AutocompleteForm()
    form = deform.Form(
        schema,
        css_class="form-inline",
        buttons=('go!',),
    )
    autoformhtml = form.render()

    return {
        'autoform': autoformhtml,
    }


@view_config(route_name='search_codes',
             renderer='templates/search_codes.pt',
             permission='manage')
def search_codes(request):
    '''
    Search for Reference Codes

    We use a form with autocomplete to let staff find entries faster.
    '''
    # check for input from "find people" form
    if 'code_to_show' in request.POST:
        try:
            _code = request.POST['code_to_show']
            # print u"_code = {}".format(_code)
            _code_ = _code.split(' ')[0]
            # print u"_code_ = {}".format(_code_)
            _entry = C3sMember.get_by_code(_code_)
            # print _entry

            return HTTPFound(
                location=request.route_url(
                    'detail',
                    memberid=_entry.id)
            )
        except:
            pass

    '''
    we use another form with autocomplete to let staff find entries faster
    '''
    class AutocompleteRefCodeForm(colander.MappingSchema):
        code_to_show = colander.SchemaNode(
            colander.String(),
            title='Code finden (quicksearch; Groß-/Kleinschreibung beachten!)',
            widget=deform.widget.AutocompleteInputWidget(
                min_length=1,
                css_class="form-inline",
                values=request.route_path(
                    'autocomplete_input_values',
                    traverse=('autocomplete_input_values')
                )
            )
        )

    schema = AutocompleteRefCodeForm()
    form = deform.Form(
        schema,
        css_class="form-inline",
        buttons=('go!',),
    )
    refcodeformhtml = form.render()

    return {
        'refcodeform': refcodeformhtml,
    }
    '''
    '''
