# -*- coding: utf-8 -*-
"""
Views for editing member data including form generation from schema.
"""

from c3smembership.models import (
    C3sMember,
)
from c3smembership.utils import (
    _,
    country_codes,
    locale_codes
)

import colander
from colander import (
    Range,
)
from datetime import (
    date,
)
import deform
from deform import ValidationFailure

import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.view import view_config
from types import NoneType

COUNTRY_DEFAULT = u'DE'
LOCALE_DEFAULT = u'de'

LOG = logging.getLogger(__name__)


@view_config(route_name='edit',
             permission='manage',
             renderer='templates/edit_member.pt')
def edit_member(request):
    """
    Let staff edit a member entry.
    """
    try:
        _id = request.matchdict['_id']
        assert(isinstance(int(_id), int))
        member = C3sMember.get_by_id(_id)
        if isinstance(member, NoneType):
            return HTTPFound(request.route_url('dashboard_only'))
    except:
        return HTTPFound(request.route_url('dashboard_only'))

    # if we have a valid id, we can load a members data from the db
    # and put the data in an appstruct to fill the form
    appstruct = {}
    email_is_confirmed = 'yes' if member.email_is_confirmed else 'no'
    appstruct['person'] = {
        'firstname': member.firstname,
        'lastname': member.lastname,
        'email': member.email,
        'email_is_confirmed': email_is_confirmed,
        'address1': member.address1,
        'address2': member.address2,
        'postcode': member.postcode,
        'city': member.city,
        'country': member.country,
        'date_of_birth': member.date_of_birth,
        '_LOCALE_': member.locale,
    }

    appstruct['membership_meta'] = {
        'membership_accepted': member.membership_accepted,
        'membership_date': member.membership_date,
        'is_duplicate': member.is_duplicate,
        'is_duplicate_of': (
            u'' if member.is_duplicate_of is None
            else member.is_duplicate_of),
        'accountant_comment': member.accountant_comment,
        'signature_received': member.signature_received,
        'signature_received_date': member.signature_received_date,
        'payment_received': member.payment_received,
        'payment_received_date': member.payment_received_date,
    }
    appstruct['membership_info'] = {
        'membership_type': member.membership_type,
        'entity_type': u'legalentity' if member.is_legalentity else 'person',
        'member_of_colsoc': 'yes' if member.member_of_colsoc else 'no',
        'name_of_colsoc': member.name_of_colsoc,
    }
    appstruct['shares'] = {
        'num_shares': member.num_shares
    }

    class PersonalData(colander.MappingSchema):
        """
        Colander schema of the personal data for editing member data.
        """
        firstname = colander.SchemaNode(
            colander.String(),
            title='Vorname',
            oid='firstname',
        )
        lastname = colander.SchemaNode(
            colander.String(),
            title='Nachname',
            oid='lastname',
        )
        email = colander.SchemaNode(
            colander.String(),
            title=_(u'E-Mail-Adresse'),
            validator=colander.Email(),
            oid='email',
        )
        email_is_confirmed = colander.SchemaNode(
            colander.String(),
            title=u'E-Mail-Adresse bestätigt?',
            widget=deform.widget.RadioChoiceWidget(
                values=(
                    (u'yes', u'Ja, bestätigt'),
                    (u'no', u'Nein, unklar'),)),
            missing=u'',
            oid='email_is_confirmed',
        )

        passwort = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default='NoneSet',
            missing='NoneSetPurposefully'
        )
        address1 = colander.SchemaNode(
            colander.String(),
            title='Adesse Zeile 1'
        )
        address2 = colander.SchemaNode(
            colander.String(),
            missing=u'',
            title=u'Adresse Zeile 2'
        )
        postcode = colander.SchemaNode(
            colander.String(),
            title='Postleitzahl',
            oid='postcode'
        )
        city = colander.SchemaNode(
            colander.String(),
            title='Ort',
            oid='city',
        )
        country = colander.SchemaNode(
            colander.String(),
            title='Land',
            default=COUNTRY_DEFAULT,
            widget=deform.widget.SelectWidget(
                values=country_codes),
            oid='country',
        )
        date_of_birth = colander.SchemaNode(
            colander.Date(),
            title='Geburtsdatum',
            default=date(2013, 1, 1),
            validator=Range(
                min=date(1913, 1, 1),
                max=date(2000, 1, 1),
                min_err=_(u'${val} is earlier than earliest date ${min}'),
                max_err=_(u'${val} is later than latest date ${max}')
            ),
            oid='date_of_birth',
        )
        _LOCALE_ = colander.SchemaNode(
            colander.String(),
            title='Locale',
            widget=deform.widget.SelectWidget(
                values=locale_codes),
            missing=u'',
        )

    class MembershipMeta(colander.Schema):
        """
        Colander schema of the meta data for editing member data.
        """
        membership_accepted = colander.SchemaNode(
            colander.Boolean(),
            title='ist aufgenommenes Mitglied'
        )
        membership_date = colander.SchemaNode(
            colander.Date(),
            title='Aufnahmedatum',
            validator=Range(
                min=date(2013, 9, 24),
                max=date.today(),
                min_err=_(u'${val} is earlier than earliest date ${min}'),
                max_err=_(u'${val} is later than latest date ${max}')
            ),
            missing=date(1970, 1, 1),
            oid='membership_date',
        )
        is_duplicate = colander.SchemaNode(
            colander.Boolean(),
            title=_(u'ist weiterer, späterer Mitgliedsantrag, gehört zu '
                    u'einem anderen Antrag oder einer bestehenden '
                    u'Mitgliedschaft.'),
            oid='is_duplicate',
        )
        is_duplicate_of = colander.SchemaNode(
            colander.String(),
            title=u'Id',
            missing=u'',
            oid='duplicate_of',
        )
        signature_received = colander.SchemaNode(
            colander.Boolean(),
            title=_(u'Signature received'),
            oid='signature_received',
        )
        signature_received_date = colander.SchemaNode(
            colander.Date(),
            title=_('Datum Unterschriftseingang'),
            validator=Range(
                min=date(1070, 1, 1),
                max=date.today(),
                min_err=_(u'${val} is earlier than earliest date ${min}'),
                max_err=_(u'${val} is later than latest date ${max}')
            ),
            missing=date(1970, 1, 1),
        )
        payment_received = colander.SchemaNode(
            colander.Boolean(),
            title=_(u'Zahlung eingegangen'),
        )
        payment_received_date = colander.SchemaNode(
            colander.Date(),
            title='Datum Zahlungserhalt',
            validator=Range(
                min=date(1970, 1, 1),
                max=date.today(),
                min_err=_(u'${val} is earlier than earliest date ${min}'),
                max_err=_(u'${val} is later than latest date ${max}')
            ),
            missing=date(1970, 1, 1),
            oid='_received_date',
        )
        accountant_comment = colander.SchemaNode(
            colander.String(),
            title=u'Staff Comment: (255 letters)',
            missing=u'',
            oid='accountant_comment',
        )

    class MembershipInfo(colander.Schema):
        """
        Colander schema of the additional data for editing member data.
        """
        yes_no = ((u'yes', _(u'Yes')),
                  (u'no', _(u'No')),
                  (u'dontknow', u'Unbekannt'),)

        entity_type = colander.SchemaNode(
            colander.String(),
            title=(u'Person oder Körperschaft?'),
            description=u'Bitte die Kategorie des Mitglied auswählen.',
            widget=deform.widget.RadioChoiceWidget(
                values=(
                    (u'person',
                     (u'Person')),
                    (u'legalentity',
                     u'Körperschaft'),
                ),
            ),
            missing=u'',
            oid='entity_type',
        )
        membership_type = colander.SchemaNode(
            colander.String(),
            title=(u'Art der Mitgliedschaft (lt. Satzung, §4)'),
            description=u'Bitte die Art der Mitgliedschaft auswählen.',
            widget=deform.widget.RadioChoiceWidget(
                values=(
                    (u'normal',
                     (u'Normales Mitglied')),
                    (u'investing',
                     u'Investierendes Mitglied'),
                    (u'unknown',
                     u'Unbekannt.'),
                ),
            ),
            missing=u'',
            oid='membership_type',
        )
        member_of_colsoc = colander.SchemaNode(
            colander.String(),
            title='Mitglied einer Verwertungsgesellschaft?',
            widget=deform.widget.RadioChoiceWidget(values=yes_no),
            oid='other_colsoc',
            default=u'',
            missing=u'',
        )
        name_of_colsoc = colander.SchemaNode(
            colander.String(),
            title=u'Falls ja, welche?',
            description=u' Mehrere Mitgliedschaften bitte durch Kommata '
                        u'voneinander trennen.',
            missing=u'',
            oid='colsoc_name',
        )

    class Shares(colander.Schema):
        """
        the number of shares a member wants to hold
        """
        num_shares = colander.SchemaNode(
            colander.Integer(),
            title='Anzahl Anteile (1-60)',
            default='1',
            validator=colander.Range(
                min=1,
                max=60,
                min_err=u'mindestens 1',
                max_err=u'höchstens 60',
            ),
            oid='num_shares')

    class MembershipForm(colander.Schema):
        """
        The Form consists of
        - Personal Data
        - Membership Information
        - Shares
        """
        person = PersonalData(
            title=_(u'Personal Data'),
        )
        membership_meta = MembershipMeta(
            title=_(u'Membership Bureaucracy')
        )
        membership_info = MembershipInfo(
            title=_(u'Membership Requirements')
        )
        shares = Shares(
            title=_(u'Shares')
        )

    schema = MembershipForm()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit')),
            deform.Button('reset', _(u'Reset'))
        ],
        use_ajax=True,
    )

    # if the form has NOT been used and submitted, remove error messages if
    # any
    if not 'submit' in request.POST:
        request.session.pop_flash()

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as validationfailure:
            request.session.flash(
                _(u'Please note: There were errors, '
                  u'please check the form below.'),
                'message_above_form',
                allow_duplicate=False)
            return{'form': validationfailure.render()}

        # to store the data in the DB, the old object is updated
        listing = [  # map data attributes to appstruct items
            ('firstname', appstruct['person']['firstname']),
            ('lastname', appstruct['person']['lastname']),
            ('date_of_birth', appstruct['person']['date_of_birth']),
            ('email', appstruct['person']['email']),
            (
                'email_is_confirmed',
                1 if appstruct['person']['email_is_confirmed'] == 'yes'
                else 0
            ),
            ('address1', appstruct['person']['address1']),
            ('address2', appstruct['person']['address2']),
            ('postcode', appstruct['person']['postcode']),
            ('city', appstruct['person']['city']),
            ('country', appstruct['person']['country']),
            ('locale', appstruct['person']['_LOCALE_']),
            (
                'membership_date',
                appstruct['membership_meta']['membership_date']
            ),
            ('is_duplicate', appstruct['membership_meta']['is_duplicate']),
            (
                'is_duplicate_of',
                appstruct['membership_meta']['is_duplicate_of']
            ),
            (
                'accountant_comment',
                appstruct['membership_meta']['accountant_comment']
            ),
            (
                'membership_type',
                appstruct['membership_info']['membership_type']
            ),
            (
                'is_legalentity',
                1 if (appstruct['membership_info']['entity_type'] ==
                      'legalentity')
                else 0
            ),
            (
                'name_of_colsoc',
                appstruct['membership_info']['name_of_colsoc']
            ),
            ('num_shares', appstruct['shares']['num_shares']),
            (
                'signature_received',
                appstruct['membership_meta']['signature_received']
            ),
            (
                'signature_received_date',
                appstruct['membership_meta']['signature_received_date']
            ),
            (
                'payment_received',
                appstruct['membership_meta']['payment_received']
            ),
            (
                'payment_received_date',
                appstruct['membership_meta']['payment_received_date']
            ),
        ]

        for thing in listing:
            attribute_name = thing[0]
            attribute_value = thing[1]

            if member.__getattribute__(attribute_name) == attribute_value:
                pass
            else:
                LOG.info(
                    u'{0} changes {1} of id {2} to {3}'.format(
                        authenticated_userid(request),
                        attribute_name,
                        member.id,
                        attribute_value
                    )
                )
                setattr(member, attribute_name, attribute_value)

        # membership acceptance status can be set or unset.
        if appstruct['membership_meta'][
                'membership_accepted'] == member.membership_accepted:
            pass
        else:
            member.membership_accepted = appstruct[
                'membership_meta']['membership_accepted']
            if isinstance(member.membership_number, NoneType) \
                    and member.membership_accepted:
                member.membership_number = \
                    C3sMember.get_next_free_membership_number()

        if appstruct['membership_info']['entity_type'] == 'legalentity':
            member.is_legalentity = True
        else:
            member.is_legalentity = False

        # empty the messages queue (as validation worked anyways)
        deleted_msg = request.session.pop_flash()
        del deleted_msg
        return HTTPFound(  # redirect to details page
            location=request.route_url(
                'detail',
                memberid=member.id),
        )

    form.set_appstruct(appstruct)
    html = form.render()

    return {'form': html}
