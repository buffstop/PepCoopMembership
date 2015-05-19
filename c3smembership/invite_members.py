# -*- coding: utf-8 -*-
from c3smembership.models import (
    C3sMember,
)
from datetime import datetime
import deform
from pkg_resources import resource_filename
from pyramid.i18n import (
    get_localizer,
)
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.view import view_config
from pyramid.threadlocal import get_current_request
from pyramid.httpexceptions import HTTPFound
from translationstring import TranslationStringFactory
from types import NoneType

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


@view_config(permission='manage',
             route_name='invite_member')
def invite_member_BCGV(request):
    '''
    send email to member with link to ticketing
    '''
    mid = request.matchdict['m_id']
    _m = C3sMember.get_by_id(mid)
    if isinstance(_m, NoneType):
        request.session.flash(
            'id not found. no mail sent.',
            'messages')
        return HTTPFound(request.route_url('membership_listing_backend',
                                           number=request.cookies['on_page'],
                                           order=request.cookies['order'],
                                           orderby=request.cookies['orderby']))

    _url = (request.registry.settings['ticketing.url'] +
            '/lu/' + _m.email_confirm_code +
            '/' + _m.email)

    _body = u'''[english version below]

Hallo {1} {2},

am 11.05.2015 haben wir Dich zu BarCamp und Generalversammlung der C3S SCE
eingeladen, welche am 12. und 13.06.2015 in Potsdam stattfinden.

Wir benötigen im Vorfeld eine Rückmeldung, ob Du an BarCamp und/oder
Generalversammlung teilnehmen möchtest, oder ob Du Dich vertreten lassen
möchtest.

Dies ist Dein individueller Link zur Anmeldung:

  {0}

Bitte teile uns dort rechtzeitig mit, ob Du teilnnimmst. Wir müssen
umgehend wissen, ob die Location ausreichend groß ist. Wenn irgend
möglich, antworte uns daher bitte bis zum 05.06.2015.

Auf der verlinkten Seite kannst Du separat die Teilnahme für die
Generalversammlung und das Barcamp bestätigen und ggfs. Essen vorbestellen.

Das wars! Versorge uns mit Themenvorschlägen, plane Deine Fahrt - dann
sehen wir uns in Potsdam! Bei Fragen kannst Du Dich wie immer an info@c3s.cc
wenden.

Wir freuen uns auf Dich & Deine Ideen!


Das Team der C3S

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Hello {1} {2},

on 11th of March 2015 you received an email inviting you to the BarCamp
and general assembly of C3S SCE mbh on the 12th and 13th July of 2015
in Potsdam.

If possible, please let us know via this form, whether you
will attend or not:

This is your personal registration link:

  {0}

Please let us know in time whether you will participate. We must know as
soon as possible whether the location will be large enough. If possible,
please respond by July 5th, 2015, at the latest.

On the linked page you can confirm your participation in the general
assembly and the barcamp separately. You can also book food for the
day of the BarCamp.

That's all! Let us know your proposals for topics, plan your trip -- and
we shall meet in Potdam!

We are looking forward to seeing you and learning to know your ideas!


Your C3S Team

'''.format(
        _url,  # {0}
        _m.firstname,  # {1}
        _m.lastname,  # {2}
    )

    log.info("mailing event invitation to to member id %s" % _m.id)

    message = Message(
        subject=(u'[C3S] Invitation to Barcamp and Assembly '
                 u'/ Einladung zu Barcamp und Generalversammlung'),
        sender='yes@office.c3s.cc',
        recipients=[_m.email],
        body=_body,
        extra_headers={
            'Reply-To': 'yes@c3s.cc',
            }
    )

    if 'true' in request.registry.settings['testing.mail_to_console']:
        # ^^ yes, a little ugly, but works; it's a string
        # print "printing mail"
        # print(message.subject)
        # print(message.body)
        print(message.body.encode('utf-8'))
    else:
        # print "sending mail"
        mailer = get_mailer(request)
        mailer.send(message)

    # _m._token = _looong_token
    _m.email_invite_flag_bcgv15 = True
    _m.email_invite_date_bcgv15 = datetime.now()
    return HTTPFound(request.route_url('membership_listing_backend',
                                       number=request.cookies['on_page'],
                                       order=request.cookies['order'],
                                       orderby=request.cookies['orderby']) +
                     '#member_' + str(_m.id))
