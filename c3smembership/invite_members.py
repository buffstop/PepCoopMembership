# -*- coding: utf-8 -*-
from c3smembership.models import (
    C3sMember,
    #DBSession,
)
from datetime import datetime
import deform
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
        return HTTPFound(request.route_url('dashboard',
                                           number=request.cookies['on_page'],
                                           order=request.cookies['order'],
                                           orderby=request.cookies['orderby']))

    #import random
    #import string
    #_looong_token = u''.join(
    #    random.choice(
    #        string.ascii_uppercase + string.digits) for x in range(13))
    _url = (request.registry.settings['ticketing.url'] +
            '/lu/' + _m.email_confirm_code +
            '/' + _m.email)

    _body = u'''[english version below]

Hallo {1} {2},

die

Cultural Commons Collecting Society SCE
mit beschränkter Haftung
- C3S SCE -
Heyestraße 194
40625 Düsseldorf

lädt Dich ein

* zur ersten jährlichen Generalversammlung nach § 13 der Satzung der C3S
  SCE [1],
* zum C3S-Barcamp 2014 und
* zur C3S-Party.

Bitte lies zunächst den gesamten Einladungstext. Er enthält wichtige
Hinweise.


Die Generalversammlung
======================

Die erste Generalversammlung der C3S SCE findet im Rahmen der c/o pop
convention in Köln statt:

am     23. August 2014
von    14:00 bis 18:00 Uhr (Verlängerung möglich)
im     Millowitsch-Theater, Aachener Straße 5, 50674 Köln

Die Anmeldung beginnt um 12:00 Uhr im Foyer des Millowitsch-Theaters.

Bitte komme zeitig, um Verzögerungen zu vermeiden, da wir Dir erst
Material aushändigen müssen. Die Teilnahme ist selbstverständlich
kostenlos. Bitte teile uns bis zum 11.08.2014 über dieses Formular mit,
ob Du teilnimmst oder nicht:

{0}


Warum ist Deine Teilnahme wichtig?
==================================

Die Generalversammlung ist das Organ, das die grundlegenden
Entscheidungen der C3S SCE trifft. Gemeinsam mit den anderen Mitgliedern
bist Du die Generalversammlung.

Eines unserer Hauptziele ist die Mitbestimmung durch alle nutzenden
Mitglieder, und die Mitwirkung aller Mitglieder. Du kannst Deine Meinung
sagen, Du kannst diskutieren, Du kannst aktiver Teil der C3S SCE werden,
und Du kannst abstimmen. Vor allem kannst Du Dich informieren, woran und
wie die C3S SCE arbeitet, und Du kannst andere Mitglieder kennenlernen.
Die C3S SCE ist Deine Community, Deine Genossenschaft. Nach der
Zulassung wird sie Deine Verwertungsgesellschaft sein.


Veranstaltungen: Ablauf und Rahmenprogramm
==========================================

21.08.2014: [c/o pop convention] "C3S SCE - Der Verwaltungsrat
            steht Rede und Antwort"
            Fritz Thyssen Stiftung / Robert Ellscheid Saal [2]
            Apostelnkloster 13-15, 50672 Köln
            Uhrzeit wird hier angekündigt:
            http://c-o-pop.de/convention/programm/
            Tickets zur c/o pop sind bei uns zum vergünstigten Preis
            von € 50 erhältlich (bitte Mail an office@c3s.cc senden).

22.08.2014: [C3S SCE] Barcamp 2014 [3]
            Alter Bahnhof Düsseldorf-Gerresheim [4]
            Heyestr. 194, 40625 Düsseldorf
            12:00 Uhr bis 20:00 Uhr
            Teilnahme € 9,00 // Teilnahme inkl. Essen € 19,00
            Voranmeldung erforderlich:
            {0}

23.08.2014: [C3S SCE] 1. Generalversammlung der C3S SCE
            Millowitsch-Theater [5]
            Aachener Straße 5, 50674 Köln
            14:00 Uhr bis 18:00 Uhr (Verlängerung möglich)
            Akkreditierung ab 12:00 Uhr
            Eintritt frei
            Voranmeldung erforderlich:
            {0}

23.08.2014: [C3S SCE] Party mit DJ - offen für alle
            CAMPI Volksbühne (neben Millowitsch-Theater)
            Aachener Straße 5, 50674 Köln
            ab 17:00 Uhr
            Eintritt frei


Agenda der Generalversammlung 2014 der C3S SCE
==============================================

Begrüßung der Anwesenden

# 1 Bestimmen der Versammlungsleitung und de(s/r) Protokollführer(s/in)

# 2 Genehmigung der Tagesordnung

# 3 Wiederkehrende Tagesordnungspunkte

## 3.1 Entgegennahme der Tätigkeitsberichte der geschäftsführenden
       Direktoren und des Verwaltungsrates mit anschließender Aussprache
## 3.2 Feststellung des Jahresabschlusses
## 3.3 Entscheidung über die Verwendung des Jahresüberschusses und die
       Verrechnung des Jahresfehlbetrages
## 3.4 Entgegennahme der Berichte über die genossenschaftliche Prüfung
       und des Gründungsberichts
## 3.5 Entlastung der geschäftsführenden Direktoren und des
       Verwaltungsrates

# 4 Anträge auf Satzungsänderung

# 5 Bericht vom C3S-Barcamp 2014

# 6 Antrag auf Beschluss zur Einrichtung eines Beirats

# 7 Einrichtung der Beratungskommissionen
## 7.1 Kommission Tarife
## 7.2 Kommission Verteilung
## 7.3 Kommission Wahrnehmungsverträge
## 7.4 Kommission Mitgliederausbau
## 7.5 Kommission Mitgliedsbeitragsordnung

# 8 Diskussionen

Beschlussanträge und Anträge zur Änderung der Tagesordnung kannst Du bis
zum 16. August (Ausschlussfrist 24 Uhr MEZ/CET) in Textform unter
agenda@c3s.cc einreichen.


Organisatorisches
=================

Teilnahmeberechtigt an der Generalversammlung sind nur Mitglieder der
C3S SCE und Bevollmächtigte nicht anwesender, aber stimmberechtigter
Mitglieder. Bevollmächtigte dürfen nach § 13 (6), Satz 3 der Satzung nur
Mitglieder der Genossenschaft, Ehegatten, Eltern, Kinder oder
Geschwister eines Mitglieds sein. Eingetragene Lebenspartner werden wie
Ehegatten behandelt. Du kannst online bei Absage Deiner Teilnahme
eine(n) Vertreter(in) benennen - mehr dazu unter:

{0}

Bitte denke daran, dass der/die Bevollmächtigte eine von Dir
unterzeichnete schriftliche Vollmacht mitbringen muss. Eine Person kann
maximal zwei Stimmberechtigte vertreten. Einen Vordruck für die
Vollmacht findest Du hier:

https://url.c3s.cc/vollmacht

Um die Generalversammlung vorzubereiten und Diskussionen vorzuverlagern,
werden wir am 22. August ein Barcamp [2] in Düsseldorf organisieren.
Eine Zusammenfassung der Ergebnisse des Barcamps wird Dir bei der
Anmeldung zur Generalversammlung ausgehändigt. Themen, die dort
besprochen werden sollen, kannst Du hier im Wiki einsehen und ergänzen:

https://url.c3s.cc/barcamp2014

(Zugang bitte erfragen: wiki@c3s.cc)

Vor der Generalversammlung erhältst Du den Geschäftsbericht sowie eine
detaillierte Agenda zum Download. Auf der Basis der Informationen im
Geschäftsbericht entscheidet die Generalversammlung über die Entlastung
des Verwaltungsrats und der Geschäftsführenden Direktoren.

Während der Generalversammlung wird ein Audio-Mitschnitt aufgezeichnet,
um ein fehlerfreies Protokoll zu gewährleisten. Der Mitschnitt wird
nicht veröffentlicht, aber intern als Anhang zum Protokoll archiviert.

Wer nicht möchte, dass sein Redebeitrag aufgezeichnet wird, kann dem vor
Beginn seines/ihres Beitrags widersprechen.


OpenPGP Key-Signing-Party
=========================

Wenn Du bereits Deine Emails mit OpenPGP verschlüsselst, kannst Du nach
Ende der Generalversammlung die Party zum gegenseitigen Key-Signing
nutzen. Alle Infos dazu findest Du in Kürze im Wiki:

https://url.c3s.cc/barcamp2014


Anreise und Unterbringung
=========================

Leider können wir als C3S SCE keine Anreisen oder Unterbringung selber
organisieren oder finanzieren. Wir können Dir aber helfen, indem Du eine
Mitfahrgelegenheit oder Couchsurfing anbieten oder danach fragen kannst:

Mitfahrgelegenheiten:   https://url.c3s.cc/fahren
Couchsurfing:           https://url.c3s.cc/schlafen


Wo gehts zur Anmeldung?
=======================

Dies ist Dein individueller Link zur Anmeldung:


***************************  W I C H T I G  ***************************

  {0}

Bitte teile uns dort rechtzeitig mit, ob Du teilnnimmst. Wir müssen
umgehend wissen, ob die Location ausreichend groß ist. Wenn irgend
möglich, antworte uns daher bitte bis zum 11. August.

***********************************************************************

Auf der verlinkten Seite kannst Du separat die Teilnahme für die
Generalversammlung und das Barcamp bestätigen. Auch Essen und
(natürlich) ein T-Shirt mit neuem Motiv für die tollen C3S-Tage am Rhein
kannst Du Dir holen - die T-Shirt-Preise haben wir für die
Veranstaltungen übrigens heruntergesetzt. 



Das wars! Versorge uns mit Themenvorschlägen, plane Deine Fahrt - dann
sehen wir uns Ende August in Düsseldorf und Köln! Bei Fragen kannst Du
Dich wie immer an info@c3s.cc wenden oder auch unsere neue
Xing-Community nutzen:

https://url.c3s.cc/xing


Wir freuen uns auf Dich & Deine Ideen!

Dein C3S-Team


====================

[1] Satzung der C3S SCE: https://url.c3s.cc/satzung
[2] Karte Fritz Thyssen Stiftung: https://url.c3s.cc/fritzthyssen
[3] Was ist ein Barcamp? https://url.c3s.cc/bcerklaerung
[4] Karte C3S HQ (Barcamp): https://url.c3s.cc/c3shq
[5] Karte Millowitsch-Theater (Generalversammlung):
https://url.c3s.cc/millowitsch
[6] Karte CAMPI Volksbühne (Party): https://url.c3s.cc/campi

++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++

Hello {1} {2},

the

Cultural Commons Collecting Society SCE
mit beschränkter Haftung
- C3S SCE -
Heyestraße 194
40625 Düsseldorf

invites you

* to the first annual general assembly, according to § 13 of the
  articles of association of the C3S SCE [1],
* to the C3S barcamp 2014,
* to the C3S party.

Please read the whole text of the invitation. It contains important
information.


The general assembly
====================

The first general assembly of the C3S SCE will be held in the context of
the c/o pop convention in Cologne

on     23rd August 2014
from   2 pm to 6 pm (extension possible)
at     Millowitsch Theater, Aachener Straße 5, 50674 Köln

Registration will commence at 12 noon in the foyer of the Millowitsch
Theater.

Please be punctual in order to avoid delays, because there is material
to be distributed to you. Of course, participation is free, Please let
us know until August 11th, 2014, via this form, whether you will attend
or not:

{0}


Why is it important that you participate?
=========================================

The general assembly is the body that takes the fundamental decisions
for the C3S. You are the general assembly, together with the other members.

One of our main objectives is the co-determination exercised by all user
members, and the participation of all members. You can voice your
opinions, you can become an active part of the C3S SCE, and you can
vote. Most of all, you can catch up on information about how the C3S SCE
operates, and what it is currently engaged with, and you can get to know
other members. The C3S SCE is your community, your cooperative. Once it
has been approved, it will be your collecting society.


Events: Agenda and supporting program
=====================================

21st August 2014: [c/o pop convention] "C3S SCE - The board of directors
                  answers your questions"
                  Fritz Thyssen Stiftung / Robert Ellscheid Saal [2]
                  Apostelnkloster 13-15, 50672 Köln
                  The time will be announced here:
                  http://c-o-pop.de/convention/programm/
                  Tickets for the c/o pop are available at a discount
                  rate of € 50 (please send an e-mail to office@c3s.cc).

22nd August 2014: [C3S SCE] Barcamp 2014 [3]
                  Alter Bahnhof Düsseldorf-Gerresheim [4]
                  Heyestraße. 194, 40625 Düsseldorf
                  12 noon until 8 pm
                  Participation € 9,00 // Participation and food € 19,00
                  Advance reservation required:
                  {0}

23rd August 2014: [C3S SCE] 1. General Assembly of the C3S SCE
                  Millowitsch Theater [5]
                  Aachener Straße 5, 50674 Köln
                  2 pm until 6 pm (extension possible)
                  Accrediting commences at 12 noon
                  Admission free
                  Advance reservation required:
                  {0}

23rd August 2014: [C3S SCE] Party with DJ - open for all
                  CAMPI Volksbühne (next to the Millowitsch Theater)
                  Aachener Straße 5, 50674 Köln
                  from 5 pm
                  Admission free


Agenda of the general assembly 2014 of the C3S SCE
==================================================

Welcoming address

# 1 Appointment of the chairperson of the assembly
    and the keeper of the minutes

# 2 Approval of the agenda

# 3 Recurring items on the agenda

## 3.1 Acceptance of the progress report of the executive directors and
       the board of directors, followed by debate
## 3.2 Approval of the annual report
## 3.3 Decision on the use of the annual net profit and the accounting
       for the annual deficit
## 3.4 Acceptance of the reports about the cooperative auditing and the
       formation report
## 3.5 Discharge of the executive directors and the board of directors

# 4 Proposals for amendments to the articles of association

# 5 Report from the C3S barcamp 2014

# 6 Proposal for the resolution to establish an advisory board

# 7 Establishment of the advisory commissions
## 7.1 Tariff commission
## 7.2 Distribution commission
## 7.3 Contracts commission
## 7.4 Membership development commission
## 7.5 Fees schedule commission

# 8 Discussions

You are entitled to contribute resolution proposals and proposals for
amendments to the agenda until August 16th, 2014 (cutoff period 12
midnight MET/CET) by sending them in written form to agenda@c3s.cc.


Organizational information
==========================

Entitled to participate in the general assembly are only members of the
C3S SCE and authorized representatives of absent members with voting
rights. According to § 13 (6), sentence 3, of the articles of
association, only members of the cooperative, their spouses, parents,
children or siblings are allowed to become authorized representatives of
absent members. Registered civil partners are treated as spouses. If you
cancel your participation, you may register a representatives online --
read more at:

{0}

Please make sure that your representatives brings a written
authorization signed by you. One representative may represent no more
than two members with voting power. You can find a blank form for the
authorization here:

https://url.c3s.cc/authorization

In order to prepare the general assembly and to shift forward
discussions, we will organize a barcamp [2] in Düsseldorf on August
22nd. You will receive a summary of the results of the barcamp when you
are accredited for the general assembly. Here you may read, and add to,
the topics that are to be discussed during the barcamp:

https://url.c3s.cc/barcamp2014

(Please ask for access: wiki@c3s.cc)

Before the general assembly you will receive the annual report and the
detailed agenda for download. Based on the information in the annual
report, the general assembly will decide about the discharge of the
executive directors and the board of directors.

An audio recording of the general assembly will be made in order to
ensure error-free minutes. The recording will not be published, but
archived internally as an appendix to the minutes.

Those who do not wish their speech contributions to be recorded, may
veto before commencing to speak.


OpenPGP Key-Signing-Party
=========================

If you already use OpenPGP to encrypt your e-mails you may take the
opportunity for a round of key-signing after the assembly. More
information will be available soon in our wiki:

https://url.c3s.cc/barcamp2014

(Please ask for access: wiki@c3s.cc)


Travel and accommodation
========================

Unfortunately, the C3S SCE is unable to organize, or finance, travel and
accommodation. But we can help you if you want to offer, or search for,
a lift or a couchsurfing place:

Lifts:         https://url.c3s.cc/lifts
Couchsurfing:  https://url.c3s.cc/sleep


Where do I register?
====================

This is your personal registration link:


*********************** I M P O R T A N T ***********************

  {0}

Please let us know in time whether you will participate. We must know as
soon as possible whether the location will be large enough. If possible,
please respond by August 11th at the latest.

*****************************************************************

On the linked page you can confirm your participation at the general
assembly and the barcamp separately. You can also book food, and (of
course) a t-shirt with a new image for the great days with the C3S on
the banks of the river Rhine -- we have reduced our t-shirt prices for
these events. 



That's all! Let us know your proposals for topics, plan your trip -- and
we shall meet at the end of August in Düsseldorf and Cologne! If you
have questions, you can get in touch, as always, via info@c3s.cc, or use
our brand-new Xing community (English is welcome):

https://url.c3s.cc/xing


We look forward to you and your ideas!

Your C3S team


====================

[1] Articles of association of the C3S SCE: https://url.c3s.cc/statutes
[2] Map of Fritz Thyssen Stiftung: https://url.c3s.cc/fritzthyssen
[3] What is a barcamp? https://url.c3s.cc/bcdefinition
[4] Map of C3S HQ (Barcamp): https://url.c3s.cc/c3shq
[5] Map of Millowitsch Theater (General Assembly):
    https://url.c3s.cc/millowitsch
[6] Map of CAMPI Volksbühne (Party): https://url.c3s.cc/campi
'''.format(
        _url,  # {0}
        _m.firstname,  # {1}
        _m.lastname,  # {2}
    )

    log.info("mailing event invitation to to AFM # %s" % _m.id)

    message = Message(
        subject=(u'[C3S] Invitation to Barcamp and Assembly '
                 u'/ Einladung zu Barcamp und Generalversammlung'),
        sender='yes@c3s.cc',
        recipients=[_m.email],
        body=_body
    )
    #print(message.subject)
    #print(message.body)
    mailer = get_mailer(request)
    mailer.send(message)
    #_m._token = _looong_token
    _m.email_invite_flag_bcgv14 = True
    _m.email_invite_date_bcgv14 = datetime.now()
    return HTTPFound(request.route_url('dashboard',
                                       number=request.cookies['on_page'],
                                       order=request.cookies['order'],
                                       orderby=request.cookies['orderby']) +
                     '#member_' + str(_m.id))
