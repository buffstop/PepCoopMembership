# -*- coding: utf-8 -*-
from pyramid.view import view_config

from c3smembership.models import (
    C3sMember,
)


@view_config(
    renderer='string',
    permission='manage',
    route_name='afms_awaiting_approval'
)
def afms_awaiting_approval(request):
    """
    list the applications for membership to be approved by the board
    """

    afms = C3sMember.afms_ready_for_approval()

    # print("there are {} afms ready for approval".format(len(afms)))

    output_string = u"""\n"""
    # output_string = u"""there are {} afms ready for approval \n""".format(
    #    len(afms))

    if len(afms) > 0:
        output_string += u"""Neue Genossenschaftsmitglieder\n"""
        output_string += u"""------------------------------\n\n"""
        output_string += u"""Vorname      | Name       | Anteile | Typ \n"""
        output_string += u"""-----------  | ---------- | ------- | ----- \n"""

    for afm in afms:
        output_string += u"""{}      | {}     |   {}    | {} \n""".format(
            unicode(afm.firstname),
            unicode(afm.lastname),
            afm.num_shares,
            'legal entity/inv.' if afm.is_legalentity else afm.membership_type
        )

    # we can not see aufstockers as of now, or?
    output_string += u"""\nAufstocker\n"""
    output_string += u"""------------------------------\n\n"""
    output_string += u"""Vorname      | Name        | Anteile | Typ \n"""
    output_string += u"""-----------  | ----------  | ------- | ----- \n"""
    output_string += u"""\n TODO: check! \n"""
    return output_string
