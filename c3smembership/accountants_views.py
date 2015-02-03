# -*- coding: utf-8 -*-
import tempfile
import unicodecsv

from c3smembership.models import (
    C3sMember,
    C3sStaff,
    DBSession,
)
from c3smembership.utils import generate_pdf
from c3smembership.mail_utils import (
    make_signature_confirmation_emailbody,
    make_payment_confirmation_emailbody,
)
from c3smembership.mail_reminders_util import (
    make_signature_reminder_emailbody,
    make_payment_reminder_emailbody,
)
from pkg_resources import resource_filename
from types import NoneType
import colander
import deform
from deform import ValidationFailure

from pyramid.i18n import (
    get_localizer,
)
from pyramid.view import view_config
from pyramid.threadlocal import get_current_request
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
)
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.url import route_url
from translationstring import TranslationStringFactory
from datetime import datetime
from sqlalchemy.exc import (
    IntegrityError,
    ResourceClosedError,
)
import math

deform_templates = resource_filename('deform', 'templates')
c3smembership_templates = resource_filename('c3smembership', 'templates')

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


@view_config(renderer='templates/login.pt',
             route_name='login')
def accountants_login(request):
    """
    This view lets accountants log in.
    if a person is already logged in, she is forwarded to the dashboard
    """
    logged_in = authenticated_userid(request)
    #print("authenticated_userid: " + str(logged_in))

    log.info("login by %s" % logged_in)

    if logged_in is not None:  # if user is already authenticated
        return HTTPFound(  # redirect her to the dashboard
            request.route_url('dashboard_only'))

    class AccountantLogin(colander.MappingSchema):
        """
        colander schema for login form
        """
        login = colander.SchemaNode(
            colander.String(),
            title=_(u"login"),
            oid="login",
        )
        password = colander.SchemaNode(
            colander.String(),
            validator=colander.Length(min=5, max=100),
            widget=deform.widget.PasswordWidget(size=20),
            title=_(u"password"),
            oid="password",
        )

    schema = AccountantLogin()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit')),
            deform.Button('reset', _(u'Reset'))
        ],
        #use_ajax=True,
        #renderer=zpt_renderer
    )

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        #print("the form was submitted")
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure, e:
            print(e)

            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{'form': e.render()}

        # get user and check pw...
        login = appstruct['login']
        password = appstruct['password']

        try:
            checked = C3sStaff.check_password(login, password)
        except AttributeError:  # pragma: no cover
            checked = False
        if checked:
            log.info("password check for %s: good!" % login)
            headers = remember(request, login)
            log.info("logging in %s" % login)
            return HTTPFound(  # redirect to accountants dashboard
                location=route_url(  # after successful login
                    'dashboard_only',
                    request=request),
                headers=headers)
        else:
            log.info("password check: failed for %s." % login)
    else:
        request.session.pop('message_above_form')  # remove message fr. session

    html = form.render()
    return {'form': html, }


@view_config(renderer='templates/dashboard.pt',
             permission='manage',
             route_name='dashboard')
def accountants_desk(request):
    """
    This view lets accountants view applications and set their status:
    has their signature arrived? how about the payment?
    """
    #_number_of_datasets = C3sMember.get_num_nonmember_listing()
    _number_of_datasets = C3sMember.nonmember_listing_count()
    #print "number of datasets: {}".format(_number_of_datasets)
    #C3sMember.get_num_non_accepted()
    try:  # check if page number, orderby and order were supplied with the URL
        _page_to_show = int(request.matchdict['number'])
        _order_by = request.matchdict['orderby']
        _order = request.matchdict['order']
    except:
        #print("Using default values")
        _page_to_show = 0
        _order_by = 'id'
        _order = 'asc'

    # '''
    # there used to be a form on this page allowing input of
    # one 'code_to_show' in case you wanted to see it
    # and be redirected there
    # '''
    # # check for input from "find dataset by confirm code" form
    # if 'code_to_show' in request.POST:
    #     try:
    #         _code = request.POST['code_to_show']
    #         log.info(
    #             "%s searched for code %s" % (
    #                 authenticated_userid(request), _code))
    #         _entry = C3sMember.get_by_code(_code)

    #         return HTTPFound(
    #             location=request.route_url(
    #                 'detail',
    #                 memberid=_entry.id)
    #         )
    #     except:
    #         pass

    """
    num_display determines how many items are to be shown on one page
    """
    if 'num_to_show' in request.POST:
        try:
            _num = int(request.POST['num_to_show'])
            if isinstance(_num, type(1)):
                num_display = _num
        except:
            # choose default
            num_display = 20
    elif 'num_display' in request.cookies:
        #print("found it in cookie")
        num_display = int(request.cookies['num_display'])
    else:
        #print("setting default")
        num_display = request.registry.settings[
            'c3smembership.dashboard_number']

    """
    base_offset helps us to minimize impact on the database
    when querying for results.
    we can choose just those results we need for the page to show
    """
    base_offset = int(_page_to_show) * int(num_display)

    '''
    load the list from the database
    '''
    # get data sets from DB
    _members = C3sMember.nonmember_listing(
        _order_by, how_many=num_display, offset=base_offset, order=_order)
    #print "DEBUG: number of items in _members: {}".format(len(_members))

    # calculate next-previous-navi
    next_page = (int(_page_to_show) + 1)
    if (int(_page_to_show) > 0):
        previous_page = int(_page_to_show) - 1
    else:
        previous_page = int(_page_to_show)
    _last_page = int(math.ceil(_number_of_datasets / int(num_display)))
    if next_page > _last_page:
        next_page = _last_page
    # store info about current page in cookie
    request.response.set_cookie('on_page', value=str(_page_to_show))
    request.response.set_cookie('num_display', value=str(num_display))
    request.response.set_cookie('order', value=str(_order))
    request.response.set_cookie('orderby', value=str(_order_by))

    _message = None
    if 'message' in request.GET:
        _message = request.GET['message']

    return {'_number_of_datasets': _number_of_datasets,
            'members': _members,
            'num_display': num_display,
            'next': next_page,
            'previous': previous_page,
            'current': _page_to_show,
            'orderby': _order_by,
            'order': _order,
            'message': _message,
            'last_page': _last_page,
            'is_last_page': _page_to_show == _last_page,
            'is_first_page': _page_to_show == 0,
            }


@view_config(permission='manage',
             route_name='switch_sig')
def switch_sig(request):
    """
    This view lets accountants switch member signature info
    has their signature arrived?
    """
    memberid = request.matchdict['memberid']
    #log.info("the id: %s" % memberid)

    # store the dashboard page the admin came from
    dashboard_page = request.cookies['on_page']
    order = request.cookies['order']
    order_by = request.cookies['orderby']

    _member = C3sMember.get_by_id(memberid)
    if _member.signature_received is True:
        _member.signature_received = False
        _member.signature_received_date = datetime(1970, 1, 1)
    elif _member.signature_received is False:
        _member.signature_received = True
        _member.signature_received_date = datetime.now()

    log.info(
        "signature status of member.id %s changed by %s to %s" % (
            _member.id,
            request.user.login,
            _member.signature_received
        )
    )

    return HTTPFound(
        request.route_url(
            'dashboard',
            number=dashboard_page, order=order, orderby=order_by)
        + '#member_' + str(_member.id)
    )


@view_config(permission='manage',
             route_name='delete_entry')
def delete_entry(request):
    """
    This view lets accountants delete entries (doublettes)
    """

    deletion_confirmed = False
    if 'deletion_confirmed' in request.params:
        deletion_confirmed = (request.params['deletion_confirmed'] == '1')

    if deletion_confirmed:
        memberid = request.matchdict['memberid']
        _member = C3sMember.get_by_id(memberid)

        C3sMember.delete_by_id(_member.id)
        log.info(
            "member.id %s was deleted by %s" % (
                _member.id,
                request.user.login,
            )
        )
        _message = "member.id %s was deleted" % _member.id

        request.session.flash(_message, 'messages')
        return HTTPFound(
            request.route_url(
                'dashboard_only',
                _query={'message': 'Member with id {0} was deleted.'.format(
                        memberid)}
            ) + '#member_' + str(_member.id)
        )
    else:
        return HTTPFound(
            request.route_url(
                'dashboard_only',
                _query={'message': 'Deleting the member was not confirmed' + \
                    ' and therefore nothing was deleted.'}
            )
        )



@view_config(permission='manage',
             route_name='switch_pay')
def switch_pay(request):
    """
    This view lets accountants switch member signature info
    has their signature arrived?
    """
    memberid = request.matchdict['memberid']
    dashboard_page = request.cookies['on_page']
    order = request.cookies['order']
    order_by = request.cookies['orderby']
    _member = C3sMember.get_by_id(memberid)

    if _member.payment_received is True:  # change to NOT SET
        _member.payment_received = False
        _member.payment_received_date = datetime(1970, 1, 1)
    elif _member.payment_received is False:  # set to NOW
        _member.payment_received = True
        _member.payment_received_date = datetime.now()

    log.info(
        "payment info of member.id %s changed by %s to %s" % (
            _member.id,
            request.user.login,
            _member.payment_received
        )
    )
    return HTTPFound(
        request.route_url(
            'dashboard',
            number=dashboard_page, order=order, orderby=order_by
        ) + '#member_' + str(_member.id)
    )


@view_config(renderer='json',
             permission='manage',
             route_name='member_info')
def member_info(request):
    memberid = request.matchdict['memberid']
    member = C3sMember.get_by_id(memberid)
    if member is None:
        return {}
    else:
        return {
            'id': member.id,
            'firstname': member.firstname,
            'lastname': member.lastname
        }
    return None


@view_config(renderer='templates/detail.pt',
             permission='manage',
             route_name='detail')
def member_detail(request):
    """
    This view lets accountants view member details
    has their signature arrived? how about the payment?
    """
    logged_in = authenticated_userid(request)
    #log.info("detail view.................................................")
    #print("---- authenticated_userid: " + str(logged_in))

    # this following stanza is overridden by the views permission settings
    #if logged_in is None:  # not authenticated???
    #    return HTTPFound(  # go back to login!!!
    #        location=route_url(
    #            'login',
    #            request=request),
    #    )

    memberid = request.matchdict['memberid']
    log.info("member details of id %s checked by %s" % (
        memberid, logged_in))

    _member = C3sMember.get_by_id(memberid)

    #print(_member)
    if _member is None:  # that memberid did not produce good results
        return HTTPFound(  # back to base
            request.route_url('dashboard_only'))

    class ChangeDetails(colander.MappingSchema):
        """
        colander schema (form) to change details of member
        """
        signature_received = colander.SchemaNode(
            colander.Bool(),
            title=_(u"Have we received a good signature?")
        )
        payment_received = colander.SchemaNode(
            colander.Bool(),
            title=_(u"Have we received payment for the shares?")
        )

    schema = ChangeDetails()
    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit')),
            deform.Button('reset', _(u'Reset'))
        ],
        use_ajax=True,
        renderer=zpt_renderer
    )

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure, e:  # pragma: no cover
            log.info(e)
            #print("the appstruct from the form: %s \n") % appstruct
            #for thing in appstruct:
            #    print("the thing: %s") % thing
            #    print("type: %s") % type(thing)
            print(e)
            #message.append(
            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{'form': e.render()}

        # change info about member in database

        test1 = (  # changed value through form (different from db)?
            appstruct['signature_received'] == _member.signature_received)
        if not test1:
            log.info(
                "info about signature of %s changed by %s to %s" % (
                    _member.id,
                    request.user.login,
                    appstruct['signature_received']))
            _member.signature_received = appstruct['signature_received']
        test2 = (  # changed value through form (different from db)?
            appstruct['payment_received'] == _member.payment_received)
        if not test2:
            log.info(
                "info about payment of %s changed by %s to %s" % (
                    _member.id,
                    request.user.login,
                    appstruct['payment_received']))
            _member.payment_received = appstruct['payment_received']
        # store appstruct in session
        request.session['appstruct'] = appstruct

        # show the updated details
        HTTPFound(route_url('detail', request, memberid=memberid))

    # else: form was not submitted: just show member info and form
    else:
        appstruct = {  # populate form with values from DB
            'signature_received': _member.signature_received,
            'payment_received': _member.payment_received}
        form.set_appstruct(appstruct)
        #print("the appstruct: %s") % appstruct
    html = form.render()

    return {'member': _member,
            'form': html}


@view_config(permission='view',
             route_name='logout')
def logout_view(request):
    """
    can be used to log a user/staffer off. "forget"
    """
    request.session.invalidate()
    request.session.flash(u'Logged out successfully.')
    headers = forget(request)
    return HTTPFound(location=route_url('login', request),
                     headers=headers)


@view_config(permission='manage',
             route_name='regenerate_pdf')
def regenerate_pdf(request):
    """
    staffers can regenerate a users pdf
    """
    _code = request.matchdict['code']
    _member = C3sMember.get_by_code(_code)

    if _member is None:  # that memberid did not produce good results
        return HTTPFound(  # back to base
            request.route_url('dashboard_only'))
    _appstruct = {
        'firstname': _member.firstname,
        'lastname': _member.lastname,
        'address1': _member.address1,
        'address2': _member.address2,
        'postcode': _member.postcode,
        'city': _member.city,
        'email': _member.email,
        'email_confirm_code': _member.email_confirm_code,
        'country': _member.country,
        '_LOCALE_': _member.locale,
        'membership_type': _member.membership_type,
        'num_shares': _member.num_shares,
        'date_of_birth': _member.date_of_birth,
        'date_of_submission': _member.date_of_submission,
    }
    log.info(
        "%s regenerated the PDF for code %s" % (
            authenticated_userid(request), _code))
    return generate_pdf(_appstruct)


@view_config(permission='manage',
             route_name='mail_sig_confirmation')
def mail_signature_confirmation(request):
    """
    send a mail to membership applicant
    informing her about reception of signature
    """
    _id = request.matchdict['memberid']
    _member = C3sMember.get_by_id(_id)
    if _member.locale == 'de':
        _subject = u'[C3S AFM] Wir haben Deine Unterschrift erhalten. Dankeschön!'
    else:
        _subject = u'[C3S AFM] We have received your signature. Thanks!'

    message = Message(
        subject=_subject,
        sender='yes@c3s.cc',
        recipients=[_member.email],
        body=make_signature_confirmation_emailbody(_member)
    )
    #print(message.body)
    mailer = get_mailer(request)
    mailer.send(message)
    _member.signature_confirmed = True
    _member.signature_confirmed_date = datetime.now()
    return HTTPFound(request.route_url('dashboard',
                                       number=request.cookies['on_page'],
                                       order=request.cookies['order'],
                                       orderby=request.cookies['orderby'])
                     )


@view_config(permission='manage',
             route_name='mail_pay_confirmation')
def mail_payment_confirmation(request):
    """
    send a mail to membership applicant
    informing her about reception of payment
    """
    _id = request.matchdict['memberid']
    _member = C3sMember.get_by_id(_id)

    if _member.locale == 'de':
        _subject = u'[C3S AFM] Wir haben Deine Zahlung erhalten. Dankeschön!'
    else:
        _subject = u'[C3S AFM] We have received your payment. Thanks!'

    message = Message(
        subject=_subject,
        sender='yes@c3s.cc',
        recipients=[_member.email],
        body=make_payment_confirmation_emailbody(_member)
    )
    #print(message.body)
    mailer = get_mailer(request)
    mailer.send(message)
    _member.payment_confirmed = True
    _member.payment_confirmed_date = datetime.now()
    return HTTPFound(request.route_url('dashboard',
                                       number=request.cookies['on_page'],
                                       order=request.cookies['order'],
                                       orderby=request.cookies['orderby'],
                                       )
                     )


@view_config(permission='manage',
             route_name='mail_sig_reminder')
def mail_signature_reminder(request):
    """
    send a mail to membership applicant
    reminding her about lack of signature
    """
    _id = request.matchdict['memberid']
    _member = C3sMember.get_by_id(_id)
    if isinstance(_member, NoneType):
        request.session.flash(
            'that member was not found! (id: {})'.format(_id),
            'messages'
        )
        return HTTPFound(
            request.route_url(
                'dashboard',
                number=request.cookies['on_page'],
                order=request.cookies['order'],
                orderby=request.cookies['orderby']))

    # first reminder? second?
    #if ((_member.sent_signature_reminder is None
    #) or (    ):
    #_first =
    message = Message(
        subject=u"C3S: don't forget to send your form / Bitte Beitrittsformular einsenden",
        sender='office@c3s.cc',
        #bcc=[request.registry.settings['reminder_blindcopy']],
        recipients=[_member.email],
        body=make_signature_reminder_emailbody(_member)
    )
    mailer = get_mailer(request)
    mailer.send(message)
    #print u"the mail: {}".format(message.body)
    #import pdb
    #pdb.set_trace()
    try:  # if value is int
        _member.sent_signature_reminder += 1
    except:  # pragma: no cover
        # if value was None (after migration of DB schema)
        _member.sent_signature_reminder = 1
    _member.sent_signature_reminder_date = datetime.now()
    return HTTPFound(request.route_url(
        'dashboard',
        number=request.cookies['on_page'],
        order=request.cookies['order'],
        orderby=request.cookies['orderby']) + '#member_' + str(_member.id)
    )


@view_config(permission='manage',
             route_name='mail_pay_reminder')
def mail_payment_reminder(request):
    """
    send a mail to membership applicant
    reminding her about lack of signature
    """
    _id = request.matchdict['memberid']
    _member = C3sMember.get_by_id(_id)

    message = Message(
        subject=u"C3S: don't forget to pay your shares / Bitte Anteile bezahlen",
        sender='office@c3s.cc',
        #bcc=[request.registry.settings['reminder_blindcopy']],
        recipients=[_member.email],
        body=make_payment_reminder_emailbody(_member)
    )
    mailer = get_mailer(request)
    mailer.send(message)
    try:  # if value is int
        _member.sent_payment_reminder += 1
    except:  # pragma: no cover
        # if value was None (after migration of DB schema)
        _member.sent_payment_reminder = 1
    _member.sent_payment_reminder_date = datetime.now()
    return HTTPFound(request.route_url(
        'dashboard',
        number=request.cookies['on_page'],
        order=request.cookies['order'],
        orderby=request.cookies['orderby']) + '#member_' + str(_member.id)
    )



# @view_config(permission='manage',
#              route_name='mail_pay_confirmation')
# def mail_passwd_reset(request):
#     """
#     send a mail to member to reset her password
#     """
#     _id = request.matchdict['memberid']
#     _member = C3sMember.get_by_id(_id)

#     message = Message(
#         subject=_('[C3S AFM] Please reset your password!'),
#         sender='yes@c3s.cc',
#         recipients=[_member.email],
#         body=make_password_reset_emailbody(_member)
#     )
#     #print(message.body)
#     mailer = get_mailer(request)
#     mailer.send(message)
#     _member.password XXX = True
#     _member. XXX = datetime.now()
#     return HTTPFound(request.route_url('dashboard',
#                                        number=request.cookies['on_page'],
#                                        order=request.cookies['order'],
#                                        orderby=request.cookies['orderby'],
#                                        )
#                      )

@view_config(permission='manage', route_name='dashboard_only')
def dashboard_only(request):
    if 'on_page' in request.cookies:
        try:
            _number = int(request.cookies['on_page'])
        except ValueError:
            _number = 0
    else:
        _number = 0
    if 'orderby' in request.cookies:
        _order_by = request.cookies['orderby']
    else:
        _order_by = 'id'
    if 'order' in request.cookies:
        _order = request.cookies['order']
    else:
        _order = 'asc'
    return HTTPFound(
        request.route_url(
            'dashboard',
            number=_number, orderby=_order_by,
            order=_order, _query=request.GET))
