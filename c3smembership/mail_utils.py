# -*- coding: utf-8 -*-


def make_payment_confirmation_emailbody(_input):
    """
    a mail body to confirm reception of payment for shares
    """
    _num_shares = _input.num_shares
    _sum_shares = _num_shares * 50

    if 'de' in _input.locale:
        _body = (u"""Liebes Neumitglied,

Deine Überweisung für """ + str(_num_shares) +
                 u""" Anteil(e) (""" + str(_sum_shares) +
                 u""" Euro) ist auf
unserem Konto eingegangen.

Falls Probleme aufgetreten sind, melde Dich bitte bei uns (yes@c3s.cc).

Danke für Deinen Beitrag zur C3S!


Liebe Grüße,

Das C3S-Team

-- 
      :::::::::::::::::: I sustain C3S! ::::::::::::::::::
      ::: dein beitrag zu fairer bezahlung für musiker :::
      :::            https://sustain.c3s.cc            :::
      ::::::::::::::::::::::::::::::::::::::::::::::::::::

                      :
              C3S SCE : Cultural Commons Collecting Society
                      : SCE mit beschränkter Haftung
                      : Heyestraße 194 : 40625 Düsseldorf : Germany
                      : https://C3S.cc

       M.eik Michalke :
          Max Gössler : Geschäftsführende Direktoren
                      :
   Meinhard Starostik : Vorsitzender des Verwaltungsrates
                      :
              GnR 506 : Genossenschaftsregister AG Düsseldorf
               USt-ID : DE294690528

"""
                 )
    else:
        _body = (u"""Dear new member,

Your transfer of """ + str(_sum_shares) + u" Euro for " + str(_num_shares) +
                 u""" share(s) just showed in our bank account.

In case of any problems please don't hesitate to contact us (yes@c3s.cc).

Thanks a lot for your contribution to the C3S!


Best wishes,

The C3S Team

-- 
      :::::::::::::::::: I sustain C3S! ::::::::::::::::::
      :::     support fair remuneration for artists    :::
      :::          https://sustain.c3s.cc/?en          :::
      ::::::::::::::::::::::::::::::::::::::::::::::::::::

                      :
              C3S SCE : Cultural Commons Collecting Society
                      : SCE mit beschränkter Haftung
                      : Heyestraße 194 : 40625 Düsseldorf : Germany
                      : https://C3S.cc

       M.eik Michalke :
          Max Gössler : executive directors
                      :
   Meinhard Starostik : chairperson of the board of directors
                      :
              GnR 506 : Genossenschaftsregister AG Düsseldorf
               USt-ID : DE294690528


"""
                 )

    return _body


def make_signature_confirmation_emailbody(_input):
    """
    a mail body to confirm reception of signature
    """
    _num_shares = _input.num_shares
    _sum_shares = _num_shares * 50

    if 'de' in _input.locale:
        _body = (u"""Liebes Neumitglied,

Dein Beitrittsformular zur Zeichnung von """ +
                 str(_num_shares) +
                 u' Anteilen (' +
                 str(_sum_shares) + u""" Euro) ist sicher bei uns gelandet.

Falls Probleme aufgetreten sind, melde Dich bitte bei uns (yes@c3s.cc).

Schön, dass Du ein Teil der C3S werden möchtest!


Liebe Grüße,

Das C3S-Team

-- 
      :::::::::::::::::: I sustain C3S! ::::::::::::::::::
      ::: dein beitrag zu fairer bezahlung für musiker :::
      :::            https://sustain.c3s.cc            :::
      ::::::::::::::::::::::::::::::::::::::::::::::::::::

                      :
              C3S SCE : Cultural Commons Collecting Society
                      : SCE mit beschränkter Haftung
                      : Heyestraße 194 : 40625 Düsseldorf : Germany
                      : https://C3S.cc

       M.eik Michalke :
          Max Gössler : Geschäftsführende Direktoren
                      :
   Meinhard Starostik : Vorsitzender des Verwaltungsrates
                      :
              GnR 506 : Genossenschaftsregister AG Düsseldorf
               USt-ID : DE294690528

""")
    else:
        _body = (u"""Dear new member,

Your membership application form to sign """ +
                 str(_num_shares) +
                 u' shares (' +
                 str(_sum_shares) +
                 u""" Euro) safely arrived at our homebase.

In case of any problems please don't hesitate to contact us (yes@c3s.cc).

Great that you want to become a part of the C3S!


Best wishes,

The C3S Team

-- 
      :::::::::::::::::: I sustain C3S! ::::::::::::::::::
      :::     support fair remuneration for artists    :::
      :::          https://sustain.c3s.cc/?en          :::
      ::::::::::::::::::::::::::::::::::::::::::::::::::::

                      :
              C3S SCE : Cultural Commons Collecting Society
                      : SCE mit beschränkter Haftung
                      : Heyestraße 194 : 40625 Düsseldorf : Germany
                      : https://C3S.cc

       M.eik Michalke :
          Max Gössler : executive directors
                      :
   Meinhard Starostik : chairperson of the board of directors
                      :
              GnR 506 : Genossenschaftsregister AG Düsseldorf
               USt-ID : DE294690528

""")
    return _body
