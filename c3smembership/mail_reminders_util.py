# -*- coding: utf-8 -*-
from time import strftime


def make_signature_reminder_emailbody(_member):
    '''
    a mail body to remind membership applicants
    to send the form with their signature
    '''
    _text = u'''[English version below]

Liebe_r {0} {1},

vielen Dank, dass Du Mitglied der C3S werden und uns unterstützen
möchtest!

Du hast Deine Beitrittserklärung am {2} ausgefüllt. Leider fehlt uns aber noch
das Formular. Bitte sende es unterschrieben und per Post an:

C3S SCE
Heyestraße 194
40625 Düsseldorf

Falls Du Deine Beitrittserklärung nicht mehr findest oder andere Fragen
zum Beitritt hast, melde Dich bitte unter office@c3s.cc.

Wenn Deine Beitrittserklärung eingegangen ist, erhältst Du eine Eingangs-
bestätigung per E-Mail.

Wir freuen uns darauf, Dich bei der C3S willkommen zu heißen!

Liebe Grüße


das Team der C3S

+++++++++++++++

Dear {0} {1},

we appreciate that you want to join C3S as a member and thereby support
us.

You have submitted your declaration to join C3S on {3}. But the form did not
reach us. Please sign the form and send it by postal service to:

C3S SCE
Heyestrasse 194
40625 Düsseldorf
Germany

In case you can't find your form anymore, or you have more questions on
joining C3S, please contact us at office@c3s.cc.

When your declaration to join is in our mailbox you will receive a
confirmation email.

We are looking forward to welcome you at C3S!

All the best


the team of C3S
    '''.format(
        _member.firstname,
        _member.lastname,
        _member.date_of_submission.strftime("%d. %m. %Y"),
        _member.date_of_submission.strftime("%d %b %Y"),
    )
    return _text


def make_payment_reminder_emailbody(_member):
    '''
    a mail body to remind membership applicants
    to send the payment for their shares
    '''
    _text = u'''[English version below]

Liebe_r {0} {1},

vielen Dank, dass Du Mitglied der C3S werden und uns unterstützen
möchtest!

Du hast Deine Beitrittserklärung am {2} ausgefüllt. Leider hast Du versäumt,
die Überweisung von {3} Euro für {4} Anteile vorzunehmen. Bitte überweise die
genannte Summe auf folgendes Konto der C3S SCE:

IBAN: DE79 8309 4495 0003 2643 78
BIC: GENODEF1ETK
Bank: Ethikbank

Bei der Überweisung des Geldes für die Genossenschaftsanteile bitte den 
folgenden Verwendungszweck angeben: {6}

Falls Du kein Mitglied mehr werden möchtest, melde Dich bitte unter
office@c3s.cc. Wenn Deine Überweisung eingegangen ist, erhältst Du eine
Eingangsbestätigung per E-Mail.

Wir freuen uns darauf, Dich bei der C3S willkommen zu heißen!

Liebe Grüße


das Team der C3S

+++++++++++++++

Dear {0} {1},

we appreciate that you want to join C3S as a member and thereby support
us.

You already downloaded your declaration to join C3S on {5}.
However, you still have to transfer {3} Euro for
the {4} shares you purchased. Please transfer the aforementioned
amount to this bank account of C3S SCE:

IBAN: DE79 8309 4495 0003 2643 78
BIC: GENODEF1ETK
Bank: Ethikbank

When transfering money for your shares to us, please use the following
confirmation code as reference: {6}

In case you don't want to become a member anymore, or you have more
questions on joining C3S, please contact us at office@c3s.cc.

When we have received the money we will send you a confirmation email.

We are looking forward to welcome you at C3S!

All the best


the team of C3S
    '''.format(
        _member.firstname,
        _member.lastname,
        _member.date_of_submission.strftime("%d.%m.%Y"),
        int(_member.num_shares) * 50,
        _member.num_shares,
        _member.date_of_submission.strftime("%d %b %Y"),
        u'C3Shares ' + _member.email_confirm_code
    )
    return _text
