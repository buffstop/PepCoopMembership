# -*- coding: utf-8 -*-

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

country_default = u'DE'
locale_default = u'de'

log = logging.getLogger(__name__)


@view_config(route_name="edit",
             permission="manage",
             renderer="templates/edit_member.pt")
def edit_member(request):
    '''
    let staff edit a member entry

    XXX should be saved under existing id/code
    '''
    try:
        _id = request.matchdict['_id']
        assert(isinstance(int(_id), int))
        _m = C3sMember.get_by_id(_id)
        if isinstance(_m, NoneType):
            return HTTPFound(request.route_url('dashboard_only'))
    except:
        return HTTPFound(request.route_url('dashboard_only'))

    # if we have a valid id, we can load a members data from the db
    # and put the data in an appstruct to fill the form
    appstruct = {}
    _email_is_confirmed = 'yes' if _m.email_is_confirmed else 'no'
    appstruct['person'] = {
        'firstname': _m.firstname,
        'lastname': _m.lastname,
        'email': _m.email,
        'email_is_confirmed': _email_is_confirmed,
        'address1': _m.address1,
        'address2': _m.address2,
        'postcode': _m.postcode,
        'city': _m.city,
        'country': _m.country,
        'date_of_birth': _m.date_of_birth,
        '_LOCALE_': _m.locale,
    }

    appstruct['membership_meta'] = {
        'membership_accepted': _m.membership_accepted,
        'membership_date': _m.membership_date,
        'is_duplicate': _m.is_duplicate,
        'is_duplicate_of': '' if (
            _m.is_duplicate_of is None) else _m.is_duplicate_of,
        'accountant_comment': _m.accountant_comment,
        'signature_received': _m.signature_received,
        'signature_received_date': _m.signature_received_date,
        'payment_received': _m.payment_received,
        'payment_received_date': _m.payment_received_date,
    }
    appstruct['membership_info'] = {
        'membership_type': _m.membership_type,
        'entity_type': u'legalentity' if _m.is_legalentity else 'person',
        'member_of_colsoc': 'yes' if _m.member_of_colsoc else 'no',
        'name_of_colsoc': _m.name_of_colsoc,
    }
    appstruct['shares'] = {
        'num_shares': _m.num_shares
    }

    class PersonalData(colander.MappingSchema):
        """
        colander schema for membership application form
        """
        firstname = colander.SchemaNode(
            colander.String(),
            title='Vorname',
            oid="firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            title='Nachnahme',
            oid="lastname",
        )
        email = colander.SchemaNode(
            colander.String(),
            title=_(u'Email'),
            validator=colander.Email(),
            oid="email",
        )
        email_is_confirmed = colander.SchemaNode(
            colander.String(),
            title=u'Email bestätigt?',
            widget=deform.widget.RadioChoiceWidget(
                values=(
                    (u'yes', u'Ja, bestätigt'),
                    (u'no', u'Nein, unklar'),)),
            missing=u'',
            oid="email_is_confirmed",
        )

        passwort = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default='NoneSet',
            missing='NoneSetPurposefully'
        )
        address1 = colander.SchemaNode(
            colander.String(),
            title='Addresse Zeile 1'
        )
        address2 = colander.SchemaNode(
            colander.String(),
            missing=unicode(''),
            title='Addresse Zeile 2'
        )
        postcode = colander.SchemaNode(
            colander.String(),
            title='Postleitzahl',
            oid="postcode"
        )
        city = colander.SchemaNode(
            colander.String(),
            title='Ort',
            oid="city",
        )
        country = colander.SchemaNode(
            colander.String(),
            title='Land',
            default=country_default,
            widget=deform.widget.SelectWidget(
                values=country_codes),
            oid="country",
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
            oid="date_of_birth",
        )
        _LOCALE_ = colander.SchemaNode(
            colander.String(),
            title='Locale',
            widget=deform.widget.SelectWidget(
                values=locale_codes),
            missing='',
        )

    class MembershipMeta(colander.Schema):
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
            oid="membership_date",
        )
        is_duplicate = colander.SchemaNode(
            colander.Boolean(),
            title=_(u'ist weiterer, späterer Mitgliedsantrag, gehört zu einem '
                    u'anderen Antrag oder einer bestehenden Mitgliedschaft.'),
            oid="is_duplicate",
        )
        is_duplicate_of = colander.SchemaNode(
            colander.String(),
            title='Id',
            missing='',
            oid="duplicate_of",
        )
        signature_received = colander.SchemaNode(
            colander.Boolean(),
            title=_(u'Signature received'),
            oid="signature_received",
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
            oid="_received_date",
        )

        accountant_comment = colander.SchemaNode(
            colander.String(),
            title='Staff Comment: (255 letters)',
            missing='',
            oid="accountant_comment",
        )

    class MembershipInfo(colander.Schema):

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
            missing=unicode(''),
            oid="entity_type",
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
            oid="other_colsoc",
            default=u'',
            missing=unicode(''),
        )
        name_of_colsoc = colander.SchemaNode(
            colander.String(),
            title=(u'Falls ja, welche?'),
            description=u' Mehrere Mitgliedschaften bitte durch Kommata ' + \
                'voneinander trennen.',
            missing=unicode(''),
            oid="colsoc_name",
        )


    class Shares(colander.Schema):
        """
        the number of shares a member wants to hold

        this involves a slider widget: added to deforms widgets.
        see README.Slider.rst
        """
        num_shares = colander.SchemaNode(
            colander.Integer(),
            title='Anzahl Anteile (1-60)',
            default="1",
            validator=colander.Range(
                min=1,
                max=60,
                min_err=u'mindestens 1',
                max_err=u'höchstens 60',
            ),
            oid="num_shares")

    class MembershipForm(colander.Schema):
        """
        The Form consists of
        - Personal Data
        - Membership Information
        - Shares
        """
        person = PersonalData(
            title=_(u"Personal Data"),
        )
        membership_meta = MembershipMeta(
            title=_(u"Membership Bureaucracy")
        )
        membership_info = MembershipInfo(
            title=_(u"Membership Requirements")
        )
        shares = Shares(
            title=_(u"Shares")
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

    # if the form has NOT been used and submitted, remove error messages if any
    if not 'submit' in request.POST:
        request.session.pop_flash()

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{'form': e.render()}

        # to store the data in the DB, the old objet is updated
        listing = [  # map data attributes to appstruct items
            ('firstname', appstruct['person']['firstname']),
            ('lastname', appstruct['person']['lastname']),
            ('date_of_birth', appstruct['person']['date_of_birth']),
            ('email', appstruct['person']['email']),
            ('email_is_confirmed',
             1 if (appstruct['person']['email_is_confirmed'] == 'yes') else 0),
            ('address1', appstruct['person']['address1']),
            ('address2', appstruct['person']['address2']),
            ('postcode', appstruct['person']['postcode']),
            ('city', appstruct['person']['city']),
            ('country', appstruct['person']['country']),
            ('locale', appstruct['person']['_LOCALE_']),
            ('membership_date',
             appstruct['membership_meta']['membership_date']),
            ('is_duplicate',
             appstruct['membership_meta']['is_duplicate']),
            ('is_duplicate_of',
             appstruct['membership_meta']['is_duplicate_of']),
            ('accountant_comment',
             appstruct['membership_meta']['accountant_comment']),
            ('membership_type', appstruct[
                'membership_info']['membership_type']),
            ('is_legalentity', 1 if (appstruct[
                'membership_info']['entity_type'] == 'legalentity') else 0),
            ('name_of_colsoc', appstruct['membership_info']['name_of_colsoc']),
            ('num_shares', appstruct['shares']['num_shares']),
            ('signature_received',
             appstruct['membership_meta']['signature_received']),
            ('signature_received_date',
             appstruct['membership_meta']['signature_received_date']),
            ('payment_received',
             appstruct['membership_meta']['payment_received']),
            ('payment_received_date',
             appstruct['membership_meta']['payment_received_date']),

        ]

        for thing in listing:
            v = thing[0]

            if _m.__getattribute__(v) == thing[1]:
                pass
            else:
                log.info(  # XXX this needs to go into the logs
                    "%s changes %s of id %s to %s" % (
                        authenticated_userid(request),
                        thing[0],
                        _m.id,
                        thing[1]
                    )
                )
                setattr(_m, v, thing[1])

        # membership acceptance status can be set or unset.
        # TODO: mark end of term/date_canceled for quitters
        if appstruct['membership_meta'][
                'membership_accepted'] == _m.membership_accepted:
            pass
        else:
            _m.membership_accepted = appstruct[
                'membership_meta']['membership_accepted']
            if isinstance(_m.membership_number, NoneType) \
                    and _m.membership_accepted:
                _m.membership_number = \
                    C3sMember.get_next_free_membership_number()

        if appstruct['membership_info']['entity_type'] == 'legalentity':
            _m.is_legalentity = True
        else:
            _m.is_legalentity = False

        # empty the messages queue (as validation worked anyways)
        deleted_msg = request.session.pop_flash()
        del deleted_msg
        return HTTPFound(  # redirect to details page
            location=request.route_url(
                'detail',
                memberid=_m.id),
        )

    form.set_appstruct(appstruct)
    html = form.render()

    return {'form': html}
