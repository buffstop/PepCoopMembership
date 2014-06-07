# -*- coding: utf-8 -*-
from c3smembership.models import (
    C3sMember,
    C3sStaff,
    DBSession,
    Group,
    #Shares,
    #Membership,
    #MembershipNumber,
)
from c3smembership.gnupg_encrypt import encrypt_with_gnupg
import colander
from colander import Range
#import datetime
from datetime import date
import deform
from deform import ValidationFailure
import math
from pkg_resources import resource_filename
from pyramid.i18n import (
    get_localizer,
)
#from pyramid.request import Request
#from pyramid.response import Response
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.view import view_config
from pyramid.threadlocal import get_current_request
from pyramid.httpexceptions import HTTPFound
#from pyramid.security import (
#    authenticated_userid,
    #forget,
    #remember,
#)
#from pyramid.url import route_url

#from pyramid_mailer import get_mailer
#from pyramid_mailer.message import Message
from sqlalchemy.exc import (
    IntegrityError,
    #ResourceClosedError,
)
import tempfile
from translationstring import TranslationStringFactory
from types import NoneType
#import unicodecsv

deform_templates = resource_filename('deform', 'templates')
c3smembership_templates = resource_filename(
    'c3smembership', 'templates')

my_search_path = (deform_templates, c3smembership_templates)

_ = TranslationStringFactory('c3smembership')


def translator(term):
    return get_localizer(get_current_request()).translate(term)

my_template_dir = resource_filename('c3smembership', 'templates/')
deform_template_dir = resource_filename('deform', 'templates/')

zpt_renderer = deform.ZPTRendererFactory(
    [
        my_template_dir,
        deform_template_dir,
    ],
    translator=translator,
)
# the zpt_renderer above is referred to within the demo.ini file by dotted name

DEBUG = False
LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    log = logging.getLogger(__name__)


@view_config(renderer='templates/stats.pt',
             permission='manage',
             route_name='stats')
def stats_view(request):
    """
    This view lets accountants view statistics:
    how many membership applications, real members, shares, etc.
    """
    return {
        # form submissions
        '_number_of_datasets': C3sMember.get_number(),
        'afm_shares_unpaid': C3sMember.afm_num_shares_unpaid(),
        'afm_shares_paid': C3sMember.afm_num_shares_paid(),
        # shares
        #'num_shares': Shares.get_total_shares(),
        # memberships
        #'num_memberships': Membership.get_number(),
        #'num_ms_nat': Membership.get_number(),  # XXX check!
        #'num_ms_jur': '0',  # XXX Membership.num_ms_jur(),
        #'num_ms_norm': Membership.num_ms_norm(),
        #'num_ms_inves': Membership.num_ms_invest(),
        # staff figures
        'num_staff': len(C3sStaff.get_all())
    }


@view_config(renderer='templates/toolbox.pt',
             permission='manage',
             route_name='toolbox')
def toolbox(request):
    """
    This view shows some options
    """
    return {'foo': 'bar'}


@view_config(renderer='templates/staff.pt',
             permission='manage',
             route_name='staff')
def staff_view(request):
    """
    This view lets admins edit staff/cashier personnel:
    who may act as cashier etc.?
    """
    _staffers = C3sStaff.get_all()

    class Staffer(colander.MappingSchema):
        login = colander.SchemaNode(
            colander.String(),
            title='login',
        )
        password = colander.SchemaNode(
            colander.String(),
            title='passwort',
        )

    schema = Staffer()

    stafferform = deform.Form(
        schema,
        buttons=[
            deform.Button('new_staffer', 'save')
        ]
    )

    if 'action' in request.POST:
        #print(request.POST['id'])
        try:
            _staffer = C3sStaff.get_by_id(int(request.POST['id']))
        except:
        #    print("exception!")
            return HTTPFound(location=request.route_url('staff'))
        #print(request.POST['action'])
        if request.POST['action'] == u'delete':
            #print("will delete staff id %s" % _staffer.id)
            C3sStaff.delete_by_id(_staffer.id)
            #print("deleted staff id %s" % _staffer.id)
            # send mail
            encrypted = encrypt_with_gnupg('''hi,
%s was deleted from the backend by %s.

best,
your membership tool''' % (_staffer.login,
                           request.authenticated_userid))
            message = Message(
                subject='[C3S Yes] staff was deleted.',
                sender='noreply@c3s.cc',
                recipients=[
                    request.registry.settings['c3smembership.mailaddr']],
                body=encrypted
            )
            mailer = get_mailer(request)
            mailer.send(message)
            return HTTPFound(location=request.route_url('staff'))
        elif request.POST['action'] == 'edit':
            appstruct = {
                'login': _staffer.login,
                'password': '_UNCHANGED_',
            }
            stafferform.set_appstruct(appstruct)

    if 'new_staffer' in request.POST:
        #print "new staffer!"
        controls = request.POST.items()
        try:
            appstruct = stafferform.validate(controls)
            #print('validated!')
        except ValidationFailure, e:
            return {
                'stafferform': e.render()
            }
        #try:
        # create an appstruct for persistence
        # XXX login must be unique!
        # XXX no password change if _UNCHANGED_
        staffer = C3sStaff(
            login=appstruct['login'],
            password=appstruct['password'],
            email=u'',
        )
        staffer.groups = [Group.get_staffers_group()]
        #print "about to add user"
        DBSession.add(staffer)
        DBSession.flush()
        print "added staffer"
        # send mail
        encrypted = encrypt_with_gnupg('''hi,
%s was added to the backend by %s.

best,
your membership tool''' % (staffer.login,
                           request.authenticated_userid))
        message = Message(
            subject='[C3S Yes] staff was added.',
            sender='noreply@c3s.cc',
            recipients=[
                request.registry.settings['c3smembership.mailaddr']],
            body=encrypted
        )
        mailer = get_mailer(request)
        mailer.send(message)

        return HTTPFound(
            request.route_url('staff')
        )

    return {
        'staffers': _staffers,
        'stafferform': stafferform.render(),
    }


@view_config(renderer='templates/delete_afms.pt',
             permission='manage',
             route_name='delete_afms')
def delete_afms(request):
    '''
    delete a bunch of AfMs in one go
    '''
    class DeleteAfMRange(colander.MappingSchema):
        first = colander.SchemaNode(
            colander.Integer(),
            title='first ID to delete'
        )
        last = colander.SchemaNode(
            colander.Integer(),
            title='last ID to delete'
        )
    schema = DeleteAfMRange()
    delete_range_form = deform.Form(
        schema,
        buttons=[deform.Button('delete_them', 'DELETE')]
    )
    if 'first' in request.POST:
        print "form was submitted!"
        print "first ID to delete: %s" % request.POST['first']
        controls = request.POST.items()
        try:
            appstruct = delete_range_form.validate(controls)
            #print('validated!')
            #print appstruct
            _first = appstruct['first']
            _last = appstruct['last']
            assert(_first < _last)
        except ValidationFailure, e:
            return {
                'resetform': e.render()
            }
        # delete entries here :-)
        for i in range(_first, _last+1):
            #print i
            try:
                #_del = C3sMember.delete_by_id(i)
                C3sMember.delete_by_id(i)
                #print 'deleted %s' % _del
            except:
                print 'id %s didnt exist'
    return {
        'delete_form': delete_range_form.render()
    }
