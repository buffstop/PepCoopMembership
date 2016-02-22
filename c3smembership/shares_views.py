"""
This module holds functionality to administer a members shares.
"""
import colander
import deform
from deform import ValidationFailure
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from types import NoneType
from c3smembership.models import Shares

from c3smembership.presentation.i18n import _

LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    log = logging.getLogger(__name__)


@view_config(renderer='templates/shares_detail.pt',
             permission='manage',
             route_name='shares_detail')
def shares_detail(request):
    '''
    Show details about a package of shares.
    '''
    _s = Shares.get_by_id(request.matchdict['id'])
    if isinstance(_s, NoneType):
        # entry was not found in database
        request.session.flash(
            "This shares id was not found in the database!",
            'message_to_staff'
        )
        return HTTPFound(
            request.route_url('toolbox'))

    # get shares owner if possible
    try:
        _m_id = _s.members[0].id
        _m_first = _s.members[0].firstname
        _m_last = _s.members[0].lastname
        # print('got it!')
    except:
        # print('failed!')
        _m_id = 0
        _m_first = 'Not'
        _m_last = 'Found'

    return {
        's': _s,  # the share
        'm_id': _m_id,  # the owner
        'm_first': _m_first,  # the owner
        'm_last': _m_last,  # the owner
    }


@view_config(renderer='templates/shares_edit.pt',
             permission='manage',
             route_name='shares_edit')
def shares_edit(request):
    '''
    Edit details of a package of shares.
    '''
    # print(request.matchdict['id'])
    from c3smembership.models import Shares
    # load info from DB -- if possible
    _s = Shares.get_by_id(request.matchdict['id'])

    if isinstance(_s, NoneType):
        # entry was not found in database
        return HTTPFound(request.route_url(
            'membership_listing_backend', number=0, orderby='id', order='asc'))
    else:
        appstruct = {}
        appstruct = {
            'number': _s.number,
            'date_of_acquisition': _s.date_of_acquisition,
        }

    # construct a form
    class Shares(colander.Schema):
        number = colander.SchemaNode(
            colander.Integer(),
            title=_('Number of Shares'),
        )
        date_of_acquisition = colander.SchemaNode(
            colander.Date(),
            title=_('Date of Acquisition')
        )
    schema = Shares()
    form = deform.Form(
        schema,
        buttons=[deform.Button('submit', _(u'Submit'))],
    )
    # form generation complete

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
            # print("the appstruct from the form: %s \n") % appstruct
            # for thing in appstruct:
            #     print("the thing: %s") % thing
            #     print("type: %s") % type(thing)

        except ValidationFailure, e:  # pragma: no cover
            print(e)
            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{'form': e.render()}

        # if no error occurred, persist the changed values info in database

        test1 = (  # changed value through form (different from db)?
            appstruct['number'] == _s.number)
        if not test1:
            log.info(
                "info about number of shares of %s changed by %s to %s" % (
                    _s.id,
                    request.user.login,
                    appstruct['number']))
            _s.number = appstruct['number']
        test2 = (  # changed value through form (different from db)?
            appstruct['date_of_acquisition'] == _s.date_of_acquisition)
        if not test2:
            log.info(
                "info about date_of_acquisition of %s changed by %s to %s" % (
                    _s.id,
                    request.user.login,
                    appstruct['date_of_acquisition']))
            _s.date_of_acquisition = appstruct['date_of_acquisition']
        # store appstruct in session
        # request.session['appstruct'] = appstruct

    else:  # no form submission
        # prepopulate form
        form.set_appstruct(appstruct)

    html = form.render()

    return {
        's': _s,
        'form': html
    }


@view_config(permission='manage',
             route_name='shares_delete')
def shares_delete(request):
    '''
    Staff may delete a package of shares.
    '''
    _id = request.matchdict['id']
    from c3smembership.models import Shares
    # load info from DB -- if possible
    _s = Shares.get_by_id(_id)

    if isinstance(_s, NoneType):
        # entry was not found in database
        request.session.flash(
            "This shares package {} was not found in the DB.".format(_id),
            'message_to_staff'
        )
        return HTTPFound(request.route_url('toolbox'))

    # print("any members? {}".format(_s.members))
    if (len(_s.members) > 0):
        # shares package is still owned
        request.session.flash(
            "DID NOT DELETE! "
            "This shares package {} still has a member owning it.".format(_id),
            'message_to_staff'
        )
        return HTTPFound(request.route_url('toolbox'))
    else:
        Shares.delete_by_id(_id)
        request.session.flash(
            "the shares package {} was deleted.".format(_id),
            'message_to_staff'
        )
        return HTTPFound(request.route_url('toolbox'))
