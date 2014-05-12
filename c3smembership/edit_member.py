# -*- coding: utf-8 -*-

from c3smembership.models import (
    C3sMember,
    #DBSession,
)
from c3smembership.utils import (
    _,
    country_codes,
    locale_codes
)

import colander
from colander import (
    #Invalid,
    Range,
)
from datetime import (
    date,
    #datetime,
)
import deform
from deform import ValidationFailure

import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
#from sqlalchemy.exc import (
    #InvalidRequestError,
    #IntegrityError
#)
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
        #print("type of _id is %s" % type(_id))
        assert(isinstance(int(_id), int))
        _m = C3sMember.get_by_id(_id)
        if isinstance(_m, NoneType):
            return HTTPFound(request.route_url('dashboard_only'))
        #def record_to_appstruct(self):
        #    return dict(
        #        [(k, self.__dict__[k]) for k in sorted(self.__dict__) if '_sa_' != k[:4]]
        #    )
        #print(_m.record_to_appstruct())

    except:
        #print "pong!"
        return HTTPFound(request.route_url('dashboard_only'))

    appstruct = {}
    appstruct['person'] = {
        'firstname': _m.firstname,
        'lastname': _m.lastname,
        'email': _m.email,
        'address1': _m.address1,
        'address2': _m.address2,
        'postcode': _m.postcode,
        'city': _m.city,
        'country': _m.country,
        'date_of_birth': _m.date_of_birth,
        '_LOCALE': _m.locale,
    }

    #print("MEMBER of COLSOC?: %s" % _m.member_of_colsoc)
    appstruct['membership_info'] = {
        'membership_type': _m.membership_type,
        'member_of_colsoc': 'yes' if _m.member_of_colsoc else 'no',
        'name_of_colsoc': _m.name_of_colsoc,
    }
    appstruct['shares'] = {
        'num_shares': _m.num_shares
    }
    #print('the appstruct: %s' % appstruct)

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
            #widget=deform.widget.DatePartsWidget(
            #    inline=True),
            default=date(2013, 1, 1),
            validator=Range(
                min=date(1913, 1, 1),
                max=date(2000, 1, 1),
                min_err=_(u'${val} is earlier than earliest date ${min}'),
                max_err=_(u'${val} is later than latest date ${max}')
            ),
            oid="date_of_birth",
        )
#        locale = colander.SchemaNode(
#            colander.String(),
#            title='Sprache',
#            default=locale_default,
##            widget=deform.widget.SelectWidget(
#                values=locale_codes),
        #    oid="locale",
        #)
        _LOCALE_ = colander.SchemaNode(
            colander.String(),
            title='Locale',
            #widget=deform.widget.HiddenWidget(),
            #default=locale_default,
            widget=deform.widget.SelectWidget(
                values=locale_codes),
            #    default='DE',
            missing='',
        )

    class MembershipInfo(colander.Schema):

        yes_no = ((u'yes', _(u'Yes')),
                  (u'no', _(u'No')))

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
                ),
            )
        )
        member_of_colsoc = colander.SchemaNode(
            colander.String(),
            title='Mitglied einer Verwertungsgesellschaft?',
            validator=colander.OneOf([x[0] for x in yes_no]),
            widget=deform.widget.RadioChoiceWidget(values=yes_no),
            oid="other_colsoc",
            #validator=colsoc_validator
        )
        name_of_colsoc = colander.SchemaNode(
            colander.String(),
            title=(u'Falls ja, welche? (Kommasepariert)'),
            missing=unicode(''),
            oid="colsoc_name",
            #validator=colander.All(
            #    colsoc_validator,
            #)
        )

        # def statute_validator(node, value):
        #     if not value:
        #         raise Invalid(
        #             node,
        #             _(u'You must confirm to have access '
        #               u'to the C3S SCE statute'))

        # got_statute = colander.SchemaNode(
        #     #colander.String(),
        #     colander.Bool(true_val=u'yes'),
        #     title='Satzung akzeptiert?',
        #     widget=deform.widget.CheckboxWidget(),
        #     #validator=colander.OneOf(['yes', ]),
        #     #validator=statute_validator,
        #     required=True,
        #     label=_('Yes'),
        # )

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
            #widget=deform.widget.TextInputSliderWidget(
            #    size=3, css_class='num_shares_input'),
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
            #description=_(u"this is a test"),
            #css_class="thisisjustatest"
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
        #renderer=zpt_renderer
    )

    # if the form has NOT been used and submitted, remove error messages if any
    if not 'submit' in request.POST:
        request.session.pop_flash()
        #print('not submitted')

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
            #print("the appstruct from the form: %s \n") % appstruct
            #for thing in appstruct:
                #print("the thing: %s") % thing
                #print("type: %s") % type(thing)

            # data sanity: if not in collecting society, don't save
            #  collsoc name even if it was supplied through form
            #if 'no' in appstruct['membership_info']['member_of_colsoc']:
            #    appstruct['membership_info']['name_of_colsoc'] = ''
            #    print appstruct['membership_info']['name_of_colsoc']
            #print '-'*80

        except ValidationFailure as e:
            #print("Validation Failure!")
            #print("the request.POST: %s \n" % request.POST)
            #for thing in request.POST:
            #    print("the thing: %s") % thing
            #    print("type: %s") % type(thing)
            #print(e.args)
            #print(e.error)
            #print(e.message)
            #message.append(
            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{'form': e.render()}

        # debug
        #print("appstruct['membership_info']['membership_type'] "
        #      "is %s" % appstruct['membership_info']['membership_type'])
        # to store the data in the DB, the old objet is updated
        listing = [  # map data attributes to appstruct items
            ('firstname', appstruct['person']['firstname']),
            ('lastname', appstruct['person']['lastname']),
            ('date_of_birth', appstruct['person']['date_of_birth']),
            ('email', appstruct['person']['email']),
            ('address1', appstruct['person']['address1']),
            ('address2', appstruct['person']['address2']),
            ('postcode', appstruct['person']['postcode']),
            ('city', appstruct['person']['city']),
            ('country', appstruct['person']['country']),
            ('locale', appstruct['person']['_LOCALE_']),
            ('date_of_birth', appstruct['person']['date_of_birth']),
            ('membership_type', appstruct[
                'membership_info']['membership_type']),
            # 1 if appstruct[
            #        'membership_info']['membership_type'] == 'yes' else 0),
            #('member_of_colsoc',
            # appstruct['membership_info']['member_of_colsoc']),
            ('name_of_colsoc', appstruct['membership_info']['name_of_colsoc']),
            ('num_shares', appstruct['shares']['num_shares']),
        ]

        for thing in listing:
            v = thing[0]

            if _m.__getattribute__(v) == thing[1]:
                #print "no change for %s" % thing[0]
                pass
            else:
                #print ("change in %s:" % thing[0])
                log.info (  # XXX this needs to go into the logs
                    "%s changes %s of id %s to %s" % (
                        request.authenticated_userid,
                        thing[0],
                        _m.id,
                        thing[1]
                    )
                )
                setattr(_m, v, thing[1])

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
