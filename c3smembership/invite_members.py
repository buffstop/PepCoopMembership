# -*- coding: utf-8 -*-
"""
This module has functionality to invite members to C3S events
like the General Assembly and BarCamp.

- Email templates (en/de)
- Check and send email (view)
- Batch invite n members (view)

The first use was for the C3S HQ inauguration party in 02.2014.
It was then reused for

- BarCamp and General Assembly 2014
- BarCamp and General Assembly 2015

How it works
------------

We send an email to the members from our membership database -- this app.
The templates for those emails
(english/german depending on members locale) can be prepared here.

For convenience, staff can invite n members at the same time.

Combination with c3sPartyTicketing
----------------------------------

Invitation emails are usually prepped with links
to the C3S ticketing system (*c3sPartyTicketing*).
That other webapp can be configured to fetch information
about the relevant C3S member from this app via API call,
see the relevant module.
"""
from c3smembership.presentation.views.dashboard import get_dashboard_redirect
from c3smembership.models import (
    C3sMember,
)
from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.view import view_config
from types import NoneType

from c3smembership.membership_certificate import make_random_token
from c3smembership.models import C3sMember
from c3smembership.invite_members_texts import make_bcga16_invitation_email


DEBUG = False
LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    log = logging.getLogger(__name__)

invite_mail_template = u''' '''


@view_config(permission='manage',
             route_name='invite_member')
def invite_member_BCGV(request):
    '''
    Send email to member with link to ticketing.

    === =====================================
    URL http://app:port/invite_member/{m_id}
    === =====================================
    '''
    mid = request.matchdict['m_id']
    _m = C3sMember.get_by_id(mid)
    if isinstance(_m, NoneType):
        request.session.flash(
            'id not found. no mail sent.',
            'messages')
        return get_dashboard_redirect(request)

    # prepare a random token iff none is set
    if _m.email_invite_token_bcgv16 is None:
        _m.email_invite_token_bcgv16 = make_random_token()
    _url = (
        request.registry.settings['ticketing.url'] +
        '/lu/' + _m.email_invite_token_bcgv16 +
        '/' + _m.email)

    email_subject, email_body = make_bcga16_invitation_email(_m, _url)

    log.info("mailing event invitation to to member id %s" % _m.id)

    message = Message(
        subject=email_subject,
        sender='yes@c3s.cc',
        recipients=[_m.email],
        body=email_body,
        extra_headers={
            'Reply-To': 'office@c3s.cc',
            }
    )

    print_mail = True if 'true' in request.registry.settings[
        'testing.mail_to_console'] else False

    if print_mail:  # pragma: no cover
        print(message.body.encode('utf-8'))
    else:
        # print "sending mail"
        mailer = get_mailer(request)
        mailer.send(message)

    # _m._token = _looong_token
    _m.email_invite_flag_bcgv16 = True
    _m.email_invite_date_bcgv16 = datetime.now()
    return get_dashboard_redirect(request, _m.id)


@view_config(
    route_name="invite_batch",
    permission='manage')
def batch_invite(request):
    """
    Batch invite n members at the same time.

    The number (n) is configurable, defaults to 5.
    The number can either be supplied in the URL
    or by posting a form with 'number' and 'submit to this view.

    === =====================================
    URL http://app:port/invite_batch/{number}
    === =====================================
    """
    try:  # how many to process?
        n = int(request.matchdict['number'])
    except:
        n = 5
    if 'submit' in request.POST:
        # print("request.POST: {}".format(request.POST))
        try:
            n = int(request.POST['number'])
        except:
            n = 5

    _invitees = C3sMember.get_invitees(n)
    print("got {} invitees".format(len(_invitees)))

    if len(_invitees) == 0:
        request.session.flash('no invitees left. all done!',
                              'message_to_staff')
        return HTTPFound(request.route_url('toolbox'))

    _num_sent = 0
    _ids_sent = []

    for _m in _invitees:
        # prepare a random token iff none is set
        if _m.email_invite_token_bcgv16 is None:
            _m.email_invite_token_bcgv16 = make_random_token()
        _url = (
            request.registry.settings['ticketing.url'] +
            '/lu/' + _m.email_invite_token_bcgv16 +
            '/' + _m.email)

        log.info("mailing event invitation to to member id %s" % _m.id)
        print("mailing event invitation to member id %s" % _m.id)

        email_subject, email_body = make_bcga16_invitation_email(_m, _url)

        message = Message(
            subject=email_subject,
            sender='yes@c3s.cc',
            recipients=[_m.email],
            body=email_body,
            extra_headers={
                'Reply-To': 'office@c3s.cc',
            }
        )

        if 'true' in request.registry.settings[
                'testing.mail_to_console']:  # pragma: no cover
            # ^^ yes, a little ugly, but works; it's a string
            # print "printing mail"
            # print(message.body.encode('utf-8'))
            pass
        else:
            # print "sending mail"
            mailer = get_mailer(request)
            mailer.send(message)

        # _m._token = _looong_token
        _m.email_invite_flag_bcgv16 = True
        _m.email_invite_date_bcgv16 = datetime.now()
        if _m.membership_accepted and _m.email_invite_flag_bcgv16:
            # print("YES!!! updated")
            pass
        _num_sent += 1
        _ids_sent.append(_m.id)

    request.session.flash(
        "sent out {} mails (to members with ids {}".format(
            _num_sent, _ids_sent),
        'message_to_staff')

    return HTTPFound(request.route_url('toolbox'))
