"""
The Annual Report shows a bunch of numbers and lists:

- the number of members and
- the number of shares

... acquired during a given timeframe.

The default timeframe is the current year, but start date and end date can be
specified to 'debug' other periods, too.

The report also shows the number of (and a list of) shares paid but not
'approved' yet

- as part of a membership or
- when additional shares were acquired
"""

from datetime import (
    date,
    datetime,
)

import colander
import deform
from deform import ValidationFailure
from pyramid.view import view_config

from c3smembership.models import (
    C3sMember,
    Shares,
)
from c3smembership.presentation.i18n import _


@view_config(
    renderer='c3smembership:templates/annual_report.pt',
    permission='manage',
    route_name='annual_reporting'
)
def annual_report(request):  # pragma: no cover
    """
    Sift, sort, count and calculate data for the report of a given timeframe.

    XXX TODO write testcases for this
    """
    # defaults
    start_date = date(date.today().year, 1, 1)  # first day of this year
    end_date = end_date = date(date.today().year, 12, 31)  # and last
    appstruct = {
        'startdate': start_date,
        'enddate': end_date,
    }

    # construct a form
    class DatesForm(colander.Schema):
        """
        Defines the colander schema for start and end date.
        """
        startdate = colander.SchemaNode(
            colander.Date(),
            title='start date',
        )
        enddate = colander.SchemaNode(
            colander.Date(),
            title='end date',
        )

    schema = DatesForm()
    form = deform.Form(
        schema,
        buttons=[deform.Button('submit', _(u'Submit'))],
    )
    # form generation complete

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)

            start = appstruct['startdate']
            end = appstruct['enddate']
            start_date = date(start.year, start.month, start.day)
            end_date = date(end.year, end.month, end.day)

        except ValidationFailure, validation_failure:  # pragma: no cover

            request.session.flash(
                _(u'Please note: There were errors, please check the form '
                  u'below.'),
                'message_above_form',
                allow_duplicate=False)
            return {
                'form': validation_failure.render(),
                'num_members': 0,
                'num_shares': 0,
                'new_members': [],
                'paid_unapproved_shares': [],
                'num_shares_paid_unapproved': 0,
                'sum_shares': 0,
                'new_shares': [],
                'start_date': start_date,
                'end_date': end_date,
            }

    else:  # if form not submitted, preload values
        form.set_appstruct(appstruct)

    # prepare: get information from the database
    # get memberships
    all_members = C3sMember.get_all()

    # prepare filtering and counting
    members = []  # all the members matching the criteria
    members_count = 0

    afm_shares_paid_unapproved_cnt = 0
    afm_shares_paid_unapproved = []

    # now filter and count the afms and members
    for member in all_members:
        payment_received_date = date(
            member.payment_received_date.year,
            member.payment_received_date.month,
            member.payment_received_date.day)
        # if membership granted during time period
        if member.membership_date >= start_date \
                and member.membership_date <= end_date:
            members.append(member)
            members_count += 1
        # but payment has been received during timespan
        elif member.payment_received \
                and payment_received_date >= start_date \
                and payment_received_date <= end_date:
            afm_shares_paid_unapproved_cnt += member.num_shares
            afm_shares_paid_unapproved.append(member)

    # shares
    shares_count = 0
    new_shares = []
    shares_paid_unapproved_count = 0
    shares_paid_unapproved = []

    all_shares = Shares.get_all()
    for share in all_shares:
        if share is not None:
            date_of_acquisition = date(
                share.date_of_acquisition.year,
                share.date_of_acquisition.month,
                share.date_of_acquisition.day)
            payment_received_date = date(
                share.payment_received_date.year,
                share.payment_received_date.month,
                share.payment_received_date.day)

            # if shares approved during span
            if start_date <= date_of_acquisition \
                    and end_date >= date_of_acquisition:
                shares_count += share.number
                new_shares.append(share)

            elif (  # shares not approved before end of time period
                    date_of_acquisition >= end_date
                    # payment received during time period
                    and payment_received_date >= start_date
                    # payment received during time period
                    and payment_received_date <= end_date):
                shares_paid_unapproved_count += share.number
                shares_paid_unapproved.append(share)

    html = form.render()

    return {
        'form': html,
        # dates
        'start_date': start_date,
        'end_date': end_date,
        'datetime': datetime,
        'date': date,
        # members
        'new_members': members,
        'num_members': members_count,
        # shares
        'num_shares': shares_count,
        'sum_shares': shares_count * 50,
        'new_shares': new_shares,
        # afm shares paid but unapproved
        'num_afm_shares_paid_unapproved': afm_shares_paid_unapproved_cnt,
        'afm_paid_unapproved_shares': afm_shares_paid_unapproved,
        # other shares paid but unapproved
        'num_shares_paid_unapproved': shares_paid_unapproved_count,
        'paid_unapproved_shares': shares_paid_unapproved,
    }
