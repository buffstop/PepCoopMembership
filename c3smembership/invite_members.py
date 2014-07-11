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

- zur ersten Generalversammlung nach § 13 der Satzung der C3S SCE [1],
- zum C3S Barcamp 2014 und
- zur C3S-Party.

Bitte lies zunächst den gesamten Einladungstext. Er enthält wichtige Hinweise.


Die Generalversammlung
=======================

Die erste Generalversammlung findet im Rahmen der c/o pop convention statt:

am     23. August 2014
von    14:00 bis 18:00 Uhr (Verlängerung möglich)
im     Millowitsch-Theater, Aachener Straße 5, 50674 Köln

Die Anmeldung beginnt um 12:00 Uhr im Foyer des Millowitsch-Theaters. Bitte
kommt zeitig, um Verzögerungen zu vermeiden. Die Teilnahme ist
selbstverständlich kostenlos. Am Ende der Mail findest Du den Link zur
Bestätigung der Teilnahme oder zur Absage.


Warum ist Eure Teilnahme wichtig?

Die Generalversammlung ist das Organ, das die grundlegenden Entscheidungen der
C3S SCE trifft. Ihr seid die Generalversammlung.

Eines unserer Hauptziele ist die Mitbestimmung durch alle nutzenden Mitglieder
und die Mitwirkung aller Mitglieder. Wir glauben fest daran, dass es machbar
ist. Gemeinsam mit Euch treten wir den Beweis an: Ihr könnt Eure Meinung sagen,
Ihr könnt diskutieren, Ihr könnt aktiver Teil der C3S SCE werden, und Ihr könnt
abstimmen. Vor allem könnt Ihr Euch informieren, woran und wie die C3S SCE
arbeitet, und wir können uns kennenlernen. Die C3S SCE ist Eure Community, Eure
Genossenschaft. Nach der Zulassung wird sie Eure Verwertungsgesellschaft sein.


Veranstaltungen: Ablauf und Rahmenprogramm

21.08.2014: [c/o pop convention] "C3S SCE - Der Verwaltungsrat steht Rede und
Antwort"
                    Fritz Thyssen Stiftung / Robert Ellscheid Saal [2]
                    Apostelnkloster 13-15, 50672 Köln
                    Uhrzeit wird angekündigt
                    Tickets zur c/o pop sind bei uns zum vergünstigten Preis
                    von 50 € erhältlich. [office@c3s.cc]

22.08.2014: [C3S SCE] Barcamp [3]
                    Alter S-Bahnhof Düsseldorf-Gerresheim [4]
                    Heyestr. 194, 40625 Düsseldorf
                    @ m.eik: *** Uhrzeiten einfügen ***
                    @ m.eik: Eintritt: x €, incl. Essen y €

23.08.2014: [C3S SCE] 1. Generalversammlung
                    Millowitsch-Theater [5]
                    Aachener Straße 5, 50674 Köln
                    14:00 Uhr bis 18:00 Uhr (Verlängerung möglich)
                    Akkreditierung ab 12:00 Uhr
                    kostenfrei

23.08.2014: [C3S SCE] Party - offen für alle
                    CAMPI Volksbühne (neben Millowitsch-Theater)
                    Aachener Straße 5, 50674 Köln
                    kläre ich gerade: ab 20:00 Uhr
                    kläre ich gerade: Eintritt?


Die Generalversammlung

Mit Tonaufzeichnung.


Agenda
=======
Begrüßung der Anwesenden
# 1 Bestimmen der Versammlungsleitung und de(s/r) Protokollführer(s/in)
[Vorschlag: Meinhard, Protokoll?]

# 2 Genehmigung der Tagesordnung

# 3 Wiederkehrende Tagesordnungspunkte

## 3.1 Entgegennahme der Tätigkeitsberichte der geschäftsführenden
       Direktoren und des Verwaltungsrates mit anschließender Aussprache
## 3.2 Feststellung des Jahresabschlusses
## 3.3 Entscheidung über die Verwendung des Jahresüberschusses und die
       Verrechnung des Jahresfehlbetrages
## 3.4 Entgegennahme der Berichte über die genossenschaftliche Prüfung
       (inkl. des Gründungsberichts)
## 3.5 Entlastung der geschäftsführenden Direktoren und des Verwaltungsrates

# 4 Beirat

## 4.1 Beschluss Neuwahl eines VRlers ja/nein und ggf Neuwahl
## 4.2 Beschluss zur Einrichtung eines Beirats

# 5 Bericht Barcamp

# 6 Einrichtung der Beratungskommissionen
## 6.1 Kommission Tarife
## 6.2 Kommission Verteilung
## 6.3 Kommission Wahrnehmungsverträge

# 7 Diskussionen

Beschlussanträge und Anträge zur Änderung der Tagesordnung können bis zum
16. August (Ausschlussfrist 24 Uhr MEZ/CET) in Textform unter agenda@c3s.cc
eingereicht werden.


Organisatorisches
------------------

Teilnahmeberechtigt an der Generalversammlung sind nur Mitglieder der C3S SCE
und Bevollmächtigte nicht anwesender, aber stimmberechtigter Mitglieder.
Bevollmächtigte dürfen nach § 13 (6), Satz 3 der Satzung nur Mitglieder der
Genossenschaft, Ehegatten, Eltern, Kinder oder Geschwister eines Mitglieds
sein.

Bitte denkt daran, dass der/die Bevollmächtigte Eure von Euch unterzeichnete
schriftliche Vollmacht mitbringen muss. Eine Person kann maximal zwei
Stimmberechtigte vertreten. Einen Vordruck für die Vollmacht findet Ihr hier:

  https://archive.c3s.cc/legal/vollmacht_gv14_de.pdf

Um die Generalversammlung vorzubereiten und Diskussionen vorzuverlagern,
werden wir am 22. August ein Barcamp [2] in Düsseldorf organisieren.
Themen, die dort besprochen werden sollen, könnt Ihr hier im Wiki ergänzen:

  https://wiki.c3s.cc (zugang bitte bei bedarf erfragen: office@c3s.cc)

Vor der Generalversammlung erhaltet Ihr den Geschäftsbericht zum Download.
Auf der Basis der Informationen im Geschäftsbericht entscheidet die
Generalversammlung über die Entlastung des Verwaltungsrats und der
Geschäftsführenden Direktoren.

Wenn Ihr für eine der Positionen unter dem Tagesordnungspunkt #4 kandidieren
möchtet, sendet uns bitte eine Mail an: election@c3s.cc Wir werden Euch um
einige Zusatzinformationen bitten und Euch im Vorfeld den Mitgliedern
vorstellen.


Anreise und Unterbringung
--------------------------

Leider können wir als C3S SCE keine Anreisen oder Unterbringung selber
organisieren oder finanzieren. Wir können Euch aber helfen.

[Können wir hier eine Wiki-Seite des Barcamps für MfG-Vermittlung einrichten?]

  öffentliche (!) mitfahrgelegenheiten-liste:
  https://pad.c3s.cc/mitfahrgelegenheiten_barcamp_gv_2014


Wo geht's zur Anmeldung?

Dies ist Euer individueller Link zur Anmeldung:


  **************** W I C H T I G  ****************************************
  *
  *  {0}
  *
  ************************************************************************


Bitte teilt uns dort bis zum 11. August mit, ob Ihr teilnehmt.

DEUTLICHER HINWEIS AUF RASCHE ANMELDUNG - Orga, Kapazität

Auf der verlinkten Seite könnt Ihr separat die Teilnahme für die
Generalversammlung und das Barcamp bestätigen. Auch Essen und (natürlich)
ein T-Shirt mit neuem Motiv für die tollen C3S-Tage am Rhein könnt Ihr Euch
holen - die T-Shirt-Preise haben wir für die Veranstaltungen übrigens
heruntergesetzt. ;-)



Das war's! Versorgt uns mit Themenvorschlägen, plant Eure Fahrt - dann
sehen wir uns Ende August in Düsseldorf und Köln! Bei Fragen könnt Ihr Euch
an info@c3s.cc wenden oder auch unsere neue Xing-Community nutzen:
http://url.c3s.cc/xing


Wir freuen uns drauf.

Das C3S-Team


====================

[1] URL Satzung
[2] Wegbeschreibung/URL Fritz Thyssen Stiftung / Robert Ellscheid Saal
[3] URL: Was ist ein Barcamp?
[4] Wegbeschreibung/URL C3S HQ
[5] Wegbeschreibung/URL Millowitsch-Theater
[6] Wegbeschreibung/URL Location Party
-> [2], [5], [6] können auf einer einzigen Karte dargestellt werden


++++++++++++++++++++++++++++++++++++++++++++++++++

Hello {1} {2},

<replace this text with something more useful>

Best wishes :: The C3S Team
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
    print(message.subject)
    print(message.body)
    mailer = get_mailer(request)
    #mailer.send(message)
    #_m._token = _looong_token
    _m.email_invite_flag_bcgv14 = True
    _m.email_invite_date_bcgv14 = datetime.now()
    return HTTPFound(request.route_url('dashboard',
                                       number=request.cookies['on_page'],
                                       order=request.cookies['order'],
                                       orderby=request.cookies['orderby']) +
                     '#member_' + str(_m.id))
