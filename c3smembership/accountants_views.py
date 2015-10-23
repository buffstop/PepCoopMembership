# -*- coding: utf-8 -*-
"""
This module holds views for accountants to do accounting stuff.

- Log In or Log Out
- Administer Applications for Membership on the Dashboard
- Check reception of signature, send reception confirmation or reminder mails
- Check reception of payment, send reception confirmation or reminder mails
- Check application details
- Deletion of applications
- ReGenerate a PDF for an application
"""
# import tempfile
# import unicodecsv

from c3smembership.models import (
    C3sMember,
    C3sStaff,
    Dues15Invoice,
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

from git_tools import GitTools

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
from datetime import (
    datetime,
    date,
)
import math

DEFORM_TEMPLATES = resource_filename('deform', 'templates')
C3SMEMBERSHIP_TEMPLATES = resource_filename('c3smembership', 'templates')

MY_SEARCH_PATH = (DEFORM_TEMPLATES, C3SMEMBERSHIP_TEMPLATES)

_ = TranslationStringFactory('c3smembership')


def translator(term):
    return get_localizer(get_current_request()).translate(term)

MY_TEMPLATE_DIR = resource_filename('c3smembership', 'templates/')
DEFORM_TEMPLATE_DIR = resource_filename('deform', 'templates/')

# the ZPT_RENDERER is referred to within the demo.ini file by dotted name
ZPT_RENDERER = deform.ZPTRendererFactory(
    [
        MY_TEMPLATE_DIR,
        DEFORM_TEMPLATE_DIR,
    ],
    translator=translator,
)

DEBUG = False
LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    LOG = logging.getLogger(__name__)


@view_config(renderer='templates/login.pt',
             route_name='login')
def accountants_login(request):
    """
    This view lets accountants log in (using a login form).

    If a person is already logged in, she is forwarded to the dashboard.
    """
    logged_in = authenticated_userid(request)

    LOG.info("login by %s", logged_in)

    if logged_in is not None:
        return HTTPFound(request.route_url('dashboard_only'))

    class AccountantLogin(colander.MappingSchema):
        """
        colander schema for login form
        """
        login = colander.SchemaNode(
            colander.String(),
            title=_(u"login"),
            oid="login")
        password = colander.SchemaNode(
            colander.String(),
            validator=colander.Length(min=5, max=100),
            widget=deform.widget.PasswordWidget(size=20),
            title=_(u"password"),
            oid="password")

    schema = AccountantLogin()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit')),
            deform.Button('reset', _(u'Reset'))
        ],
    )

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure, e_validation_failure:
            print(e_validation_failure)

            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{'form': e_validation_failure.render()}

        # get user and check pw...
        login = appstruct['login']
        password = appstruct['password']

        try:
            checked = C3sStaff.check_password(login, password)
        except AttributeError:  # pragma: no cover
            checked = False
        if checked:
            LOG.info("password check for %s: good!", login)
            headers = remember(request, login)
            LOG.info("logging in %s", login)
            return HTTPFound(
                location=route_url(
                    'dashboard_only',
                    request=request),
                headers=headers)
        else:
            LOG.info("password check: failed for %s.", login)
    else:
        request.session.pop('message_above_form')

    html = form.render()
    return {'form': html, }


@view_config(renderer='templates/dashboard.pt',
             permission='manage',
             route_name='dashboard')
def accountants_desk(request):
    """
    The Dashboard.

    This view lets accountants view
    the **list of applications for membership**.

    Some details can be seen (name, email, link to more details)
    as well as their membership application *progress*:

    - has their signature arrived?
    - how about the payment?
    - have reminders been sent? receptions confirmed?

    There are also links to *edit* or *delete* one of the datasets.

    Once all requirements are fulfilled,
    an application can be turned into a membership from here:
    a button shows up.
    """
    _number_of_datasets = C3sMember.nonmember_listing_count()
    try:
        _page_to_show = int(request.matchdict['number'])
        _order_by = request.matchdict['orderby']
        _order = request.matchdict['order']
    except (KeyError, ValueError):
        _page_to_show = 0
        _order_by = 'id'
        _order = 'asc'

    if 'num_to_show' in request.POST:
        try:
            _num = int(request.POST['num_to_show'])
            if isinstance(_num, type(1)):
                num_display = _num
        except (KeyError, ValueError):
            num_display = 20
    elif 'num_display' in request.cookies:
        num_display = int(request.cookies['num_display'])
    else:
        num_display = request.registry.settings[
            'c3smembership.dashboard_number']

    # base_offset helps us to minimize impact on the database
    # when querying for results.
    # we can choose just those results we need for the page to show
    base_offset = int(_page_to_show) * int(num_display)

    # load the list from the database
    _members = C3sMember.nonmember_listing(
        _order_by, how_many=num_display, offset=base_offset, order=_order)

    # calculate next-previous-navi
    next_page = int(_page_to_show) + 1
    if int(_page_to_show) > 0:
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

    # build version information for footer
    import c3smembership
    version_number = c3smembership.__version__
    version_location_url = None
    version_location_name = None
    if request.registry.settings['c3smembership.runmode'] == 'dev':
        # retrieving git information is expensive and therefore only
        # displayed in development mode
        git_tag = GitTools.get_tag()
        branch_name = GitTools.get_branch()
        if git_tag is None:
            git_tag = '???'
        version_number = '{0} (Tag {1}, Branch {2})'.format(
            version_number, git_tag, branch_name)
        version_location_name = GitTools.get_commit_hash()
        version_location_url = GitTools.get_github_commit_url()

    return {
        '_number_of_datasets': _number_of_datasets,
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
        'version_number': version_number,
        'version_location_name': version_location_name,
        'version_location_url': version_location_url,
    }


@view_config(permission='manage',
             route_name='switch_sig')
def switch_sig(request):
    """
    This view lets accountants switch an applications signature status
    once their signature has arrived.
    """
    memberid = request.matchdict['memberid']

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

    LOG.info(
        "signature status of member.id %s changed by %s to %s",
        _member.id,
        request.user.login,
        _member.signature_received
    )

    if 'dashboard' in request.referrer:
        return HTTPFound(
            request.route_url(
                'dashboard',
                number=dashboard_page, order=order, orderby=order_by)
            + '#member_' + str(_member.id)
        )
    else:
        return HTTPFound(
            request.route_url(
                'detail',
                memberid=_member.id)
            + '#membership_info'
        )


@view_config(permission='manage',
             route_name='delete_entry')
def delete_entry(request):
    """
    This view lets accountants delete datasets (e.g. doublettes).
    """

    deletion_confirmed = (request.params.get('deletion_confirmed', '0') == '1')
    redirection_view = request.params.get('redirect', 'dashboard_only')
    LOG.info('redirect to: ' + str(redirection_view))

    if deletion_confirmed:
        memberid = request.matchdict['memberid']
        _member = C3sMember.get_by_id(memberid)
        member_lastname = _member.lastname
        member_firstname = _member.firstname

        C3sMember.delete_by_id(_member.id)
        LOG.info(
            "member.id %s was deleted by %s" % (
                _member.id,
                request.user.login,
            )
        )
        _message = "member.id %s was deleted" % _member.id
        request.session.flash(_message, 'messages')

        _msgstr = u'Member with id {0} \"{1}, {2}\" was deleted.'
        return HTTPFound(
            request.route_url(
                redirection_view,
                _query={'message': _msgstr.format(
                        memberid,
                        member_lastname,
                        member_firstname)}
            ) + '#member_' + str(memberid)
        )
    else:
        return HTTPFound(
            request.route_url(
                redirection_view,
                _query={'message': (
                    'Deleting the member was not confirmed'
                    ' and therefore nothing has been deleted.')}
            )
        )


@view_config(permission='manage',
             route_name='switch_pay')
def switch_pay(request):
    """
    This view lets accountants switch a member applications payment status
    once their payment has arrived.
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

    LOG.info(
        "payment info of member.id %s changed by %s to %s",
        _member.id,
        request.user.login,
        _member.payment_received
    )
    if 'dashboard' in request.referrer:
        return HTTPFound(
            request.route_url(
                'dashboard',
                number=dashboard_page, order=order, orderby=order_by)
            + '#member_' + str(_member.id)
        )
    else:
        return HTTPFound(
            request.route_url(
                'detail',
                memberid=_member.id)
            + '#membership_info'
        )


@view_config(renderer='json',
             permission='manage',
             route_name='get_member')
def get_member(request):
    """
    This function serves an AJAX-call from the dashboard.

    There will be one call per application for membership listed!
    """
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
    This view lets accountants view member details:

    - has their signature arrived?
    - how about the payment?

    Mostly all the info about an application or membership
    in the database can be seen here.
    """
    from decimal import Decimal as D
    # import decimal
    logged_in = authenticated_userid(request)
    memberid = request.matchdict['memberid']
    LOG.info("member details of id %s checked by %s", memberid, logged_in)

    _member = C3sMember.get_by_id(memberid)

    if _member is None:  # that memberid did not produce good results
        request.session.flash(
            "A Member with id "
            "{} could not be found in the DB. run for the backups!".format(
                memberid),
            'message_to_staff'
        )
        return HTTPFound(  # back to base
            request.route_url('toolbox'))

    # class ChangeDetails(colander.MappingSchema):
    #     """
    #     colander schema (form) to change details of member
    #     """
    #     signature_received = colander.SchemaNode(
    #         colander.Bool(),
    #         title=_(u"Have we received a good signature?")
    #     )
    #     payment_received = colander.SchemaNode(
    #         colander.Bool(),
    #         title=_(u"Have we received payment for the shares?")
    #     )

    # schema = ChangeDetails()
    # form = deform.Form(
    #     schema,
    #     buttons=[
    #         deform.Button('submit', _(u'Submit')),
    #         deform.Button('reset', _(u'Reset'))
    #     ],
    #     use_ajax=True,
    #     renderer=zpt_renderer
    # )

    # # if the form has been used and SUBMITTED, check contents
    # if 'submit' in request.POST:
    #     controls = request.POST.items()
    #     try:
    #         appstruct = form.validate(controls)
    #     except ValidationFailure, e:  # pragma: no cover
    #         log.info(e)
    #         print(e)
    #         request.session.flash(
    #             _(u"Please note: There were errors, "
    #               "please check the form below."),
    #             'message_above_form',
    #             allow_duplicate=False)
    #         return{'form': e.render()}

    #     # change info about member in database
    #     test1 = (  # changed value through form (different from db)?
    #         appstruct['signature_received'] == _member.signature_received)
    #     if not test1:
    #         log.info(
    #             "info about signature of %s changed by %s to %s" % (
    #                 _member.id,
    #                 request.user.login,
    #                 appstruct['signature_received']))
    #         _member.signature_received = appstruct['signature_received']
    #     test2 = (  # changed value through form (different from db)?
    #         appstruct['payment_received'] == _member.payment_received)
    #     if not test2:
    #         log.info(
    #             "info about payment of %s changed by %s to %s" % (
    #                 _member.id,
    #                 request.user.login,
    #                 appstruct['payment_received']))
    #         _member.payment_received = appstruct['payment_received']
    #     # store appstruct in session
    #     request.session['appstruct'] = appstruct

    #     # show the updated details
    #     HTTPFound(route_url('detail', request, memberid=memberid))

    # # else: form was not submitted: just show member info and form
    # else:
    #     appstruct = {  # populate form with values from DB
    #         'signature_received': _member.signature_received,
    #         'payment_received': _member.payment_received}
    #     form.set_appstruct(appstruct)
    #     # print("the appstruct: %s") % appstruct
    # html = form.render()

    # make pretty link for certificate download
    if _member.is_legalentity:
        _cert_link = _member.lastname
    else:
        _cert_link = _member.firstname + _member.lastname

    _cert_link = _cert_link.replace(
        u'&', u'+').replace(
        u' ', u'_').replace(
        u'.', u'').replace(
        u'ä', u'ae').replace(
        u'ö', u'oe').replace(
        u'ü', u'ue').replace(
        u'.', u'')

    # get the members invoices from the DB
    _invoices = Dues15Invoice.get_by_membership_no(_member.membership_number)

    return {
        'today': date.today().strftime('%Y-%m-%d'),
        'D': D,
        'member': _member,
        'cert_link': _cert_link,
        'invoices': _invoices,
        # 'form': html
    }


@view_config(permission='view',
             route_name='logout')
def logout_view(request):
    """
    Is used to log a user/staffer off. "forget"
    """
    request.session.invalidate()
    request.session.flash(u'Logged out successfully.')
    headers = forget(request)
    return HTTPFound(
        location=route_url('login', request),
        headers=headers
    )


@view_config(permission='manage',
             route_name='regenerate_pdf')
def regenerate_pdf(request):
    """
    Staffers can regenerate an appkicants PDF and send it to her.
    """
    _code = request.matchdict['code']
    _member = C3sMember.get_by_code(_code)

    if _member is None:
        return HTTPFound(request.route_url('dashboard_only'))
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
    LOG.info(
        "%s regenerated the PDF for code %s",
        authenticated_userid(request),
        _code)
    return generate_pdf(_appstruct)


@view_config(permission='manage',
             route_name='mail_sig_confirmation')
def mail_signature_confirmation(request):
    """
    Send a mail to a membership applicant
    informing her about reception of signature.
    """
    _id = request.matchdict['memberid']
    _member = C3sMember.get_by_id(_id)
    if _member.locale == 'de':
        _subject = u'[C3S AFM] Wir haben Deine Unterschrift ' + \
            'erhalten. Dankeschön!'
    else:
        _subject = u'[C3S AFM] We have received your signature. Thanks!'

    message = Message(
        subject=_subject,
        sender='yes@c3s.cc',
        recipients=[_member.email],
        body=make_signature_confirmation_emailbody(_member)
    )
    mailer = get_mailer(request)
    mailer.send(message)
    _member.signature_confirmed = True
    _member.signature_confirmed_date = datetime.now()
    return HTTPFound(request.route_url(
        'dashboard',
        number=request.cookies['on_page'],
        order=request.cookies['order'],
        orderby=request.cookies['orderby']))


@view_config(permission='manage',
             route_name='mail_pay_confirmation')
def mail_payment_confirmation(request):
    """
    Send a mail to a membership applicant
    informing her about reception of payment.
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
    mailer = get_mailer(request)
    mailer.send(message)
    _member.payment_confirmed = True
    _member.payment_confirmed_date = datetime.now()
    return HTTPFound(request.route_url(
        'dashboard',
        number=request.cookies['on_page'],
        order=request.cookies['order'],
        orderby=request.cookies['orderby']))


@view_config(permission='manage',
             route_name='mail_sig_reminder')
def mail_signature_reminder(request):
    """
    Send a mail to a membership applicant
    reminding her about lack of signature.
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

    message = Message(
        subject=u"C3S: don't forget to send your form / Bitte " + \
            'Beitrittsformular einsenden',
        sender='office@c3s.cc',
        recipients=[_member.email],
        body=make_signature_reminder_emailbody(_member)
    )
    mailer = get_mailer(request)
    mailer.send(message)
    try:
        _member.sent_signature_reminder += 1
    except TypeError:
        # if value was None (after migration of DB schema)
        _member.sent_signature_reminder = 1
    _member.sent_signature_reminder_date = datetime.now()
    return HTTPFound(request.route_url(
        'dashboard',
        number=request.cookies['on_page'],
        order=request.cookies['order'],
        orderby=request.cookies['orderby']) + '#member_' + str(_member.id))


@view_config(permission='manage',
             route_name='mail_pay_reminder')
def mail_payment_reminder(request):
    """
    Send a mail to a membership applicant
    reminding her about lack of signature.
    """
    _id = request.matchdict['memberid']
    _member = C3sMember.get_by_id(_id)

    message = Message(
        subject=u"C3S: don't forget to pay your shares / Bitte Anteile " + \
            "bezahlen",
        sender='office@c3s.cc',
        recipients=[_member.email],
        body=make_payment_reminder_emailbody(_member)
    )
    mailer = get_mailer(request)
    mailer.send(message)
    try:  # if value is int
        _member.sent_payment_reminder += 1
    except TypeError:  # pragma: no cover
        # if value was None (after migration of DB schema)
        _member.sent_payment_reminder = 1
    _member.sent_payment_reminder_date = datetime.now()
    return HTTPFound(request.route_url(
        'dashboard',
        number=request.cookies['on_page'],
        order=request.cookies['order'],
        orderby=request.cookies['orderby']) + '#member_' + str(_member.id))


@view_config(permission='manage', route_name='dashboard_only')
def dashboard_only(request):
    """
    This is a mere redirect, so the url with /dashboard works w/o long tail.

    Convenience. Can also be used in code or templates:
    request.route_url('dashboard_only')
    """
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
            order=_order, _query=request.GET
        )
    )
