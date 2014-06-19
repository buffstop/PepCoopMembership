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
from datetime import (
    datetime,
    date
)
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
        # XXX login must be unique!
        existing = C3sStaff.get_by_login(appstruct['login'])
        if existing is not None:
            #print "that staffer exists!"
            if u'_UNCHANGED_' in appstruct['password']:
                pass
            else:
                existing.password = appstruct['password']
                existing.last_password_change = datetime.now()
            encrypted = encrypt_with_gnupg('''hi,
the password of %s was changed by %s.

best,
your membership tool''' % (existing.login,
                           request.authenticated_userid))
            message = Message(
                subject='[C3S Yes] staff password changed.',
                sender='noreply@c3s.cc',
                recipients=[
                    request.registry.settings['c3smembership.mailaddr']],
                body=encrypted
            )

        else:  # create new entry
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
        return HTTPFound(request.route_url('dashboard_only'))
    return {
        'delete_form': delete_range_form.render()
    }


@view_config(permission='manage',
             route_name='mail_mail_confirmation')
def mail_mail_conf(request):
    '''
    send email to member to confirm her email address by clicking a link
    '''
    afmid = request.matchdict['memberid']
    afm = C3sMember.get_by_id(afmid)
    if isinstance(afm, NoneType):
        request.session.flash(
            'id not found. no mail sent.',
            'messages')
        return HTTPFound(request.route_url('dashboard',
                                           number=request.cookies['on_page'],
                                           order=request.cookies['order'],
                                           orderby=request.cookies['orderby']))

    import random
    import string
    _looong_token = u''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in range(13))
    _url = (request.registry.settings['c3smembership.url'] +
            '/vae/' + afm.email_confirm_code +
            '/' + _looong_token + '/' + afm.email)

    _body = u'''[english version below]

Liebe_r C3S-Unterstützer_in,

Uns wurde am {1} diese Mail-Adresse genannt, um mit Dir in Kontakt treten
zu können.

Um sicherzustellen, dass sich nicht versehentlich ein Tippfehler o.ä.
eingeschlichen hat, bitten wir Dich um eine Bestätigung der Adresse. Dafür
brauchst Du nur den folgenden Link aufzurufen:

  {0}

Solltest Du diese Adresse nicht bei uns angegeben haben, antworte bitte kurz
auf diese E-Mail.


Viele Grüße :: Das C3S-Team

++++++++++++++++++++++++++++++++++++++++++++++++++

Dear C3S-Supporter,

We were given this Email address to contact you on {2}. To make sure this
address really works, we are asking you to confirm your address.
Please click on the following link:

    {0}

If you did not give this email address to C3S, please reply briefly to this
email.

Best :: The C3S Team
'''.format(
    _url,
    afm.date_of_submission.strftime("%d.%m.%Y"),
    afm.date_of_submission.strftime("%d %b %Y"),
)

    log.info("mailing mail confirmation to AFM # %s" % afm.id)

    message = Message(
        subject=(u'[C3S] Please confirm your Email address! '
                 u'/ Bitte E-Mail-Adresse bestätigen!'),
        sender='yes@c3s.cc',
        recipients=[afm.email],
        body=_body
    )
    #print(message.subject)
    #print(message.body)
    mailer = get_mailer(request)
    mailer.send(message)
    afm.email_confirm_token = _looong_token
    afm.email_confirm_mail_date = datetime.now()
    return HTTPFound(request.route_url('dashboard',
                                       number=request.cookies['on_page'],
                                       order=request.cookies['order'],
                                       orderby=request.cookies['orderby']) +
                     '#' + str(afm.id))


@view_config(renderer='templates/verify-mail.pt',
             route_name='verify_afm_email')
def verify_mailaddress_conf(request):
    '''
    let member confirm her email address by clicking a link
    '''
    user_email = request.matchdict['email']
    refcode = request.matchdict['refcode']
    token = request.matchdict['token']
    # try to get entry from DB
    afm = C3sMember.get_by_code(refcode)
    if isinstance(afm, NoneType):  # no entry?
        #print "entry not found"
        return {
            'confirmed': False,
            'firstname': 'foo',
            'lastname': 'bar',
            'result_msg': 'bad URL / bad codes. please contact office@c3s.cc!',
        }
    # check token
    if len(afm.email_confirm_token) == 0:  # token was invalidated already
        #print "the token is empty"
        return {
            'confirmed': False,
            'firstname': afm.firstname,
            'lastname': afm.lastname,
            'result_msg': 'your token is invalid. please contact office@c3s.cc!',
        }

    try:
        assert(afm.email_confirm_token in token)
        assert(token in afm.email_confirm_token)
        assert(afm.email in user_email)
        assert(user_email in afm.email)
    except:
        return {
            'confirmed': False,
            'firstname': 'foo',
            'lastname': 'bar',
            'result_msg': 'bad token/email. please contact office@c3s.cc!',
        }

    afm.email_is_confirmed = True
    afm.email_confirm_token = u''
    DBSession.flush()
    # notify staff
    message = Message(
        subject='[C3S Yes!] afm email confirmed',
        sender='noreply@c3s.cc',
        recipients=[request.registry.settings['c3smembership.mailaddr'], ],
        body=u'see {}/detail/{}'.format(
            request.registry.settings['c3smembership.url'],
            afm.id)
    )
    mailer = get_mailer(request)
    mailer.send(message)
    return {
        'confirmed': True,
        'firstname': afm.firstname,
        'lastname': afm.lastname,
        'result_msg': u'',
    }
