"""
    The Annual Report shows a bunch of numbers and lists:

    - the number of members and
    - the number of shares

    ... acquired during a given timeframe.

    The default timeframe is the current year,
    but start date and end date can be specified to 'debug' other periods, too.

    The report also shows the number of (and a list of)
    shares paid but not 'approved' yet

    - as part of a membership or
    - when additional shares were acquired

"""

import colander
from datetime import date
from datetime import datetime
import deform
from deform import ValidationFailure
from pyramid.view import view_config

from c3smembership.models import (
    C3sMember,
    Shares,
)
from c3smembership.views import _


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
    start_date = datetime(date.today().year, 1, 1)  # first day of this year
    end_date = end_date = datetime(date.today().year, 12, 31)  # and last
    appstruct = {
        'startdate': start_date,
        'enddate': end_date,
    }

    # construct a form
    class DatesForm(colander.Schema):
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
        # print("SUBMITTED!")
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
            # print("the appstruct from the form: %s \n") % appstruct
            # for thing in appstruct:
            #    print("the thing: %s") % thing
            #    print("type: %s") % type(thing)

            start = appstruct['startdate']  # date
            end = appstruct['enddate']  # date
            # convert to datetime
            start_date = datetime(start.year, start.month, start.day)
            end_date = datetime(end.year, end.month, end.day)

        except ValidationFailure, e:  # pragma: no cover

            print(e)
            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{
                'form': e.render(),
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
    _all_members = C3sMember.get_all()

    # prepare filtering and counting
    _members = []  # all the members matching the criteria
    _num_members = 0

    _num_afm_shares_paid_unapproved = 0
    _afm_shares_paid_unapproved = []

    # now filter and count the afms and members
    for m in _all_members:
        if (
                m.membership_accepted  # unneccessary!?
                and (m.membership_date >= start_date)
                and (m.membership_date <= end_date)
        ):
            # add this item to the list
            _members.append(m)
            _num_members += 1
            # also count the shares
            # for _s in item.shares:
            #    if (_s.date_of_acquisition <= _date):
            #        _count_shares += _s.number
        elif (  # member is not accepted yet
                (
                    (not m.membership_accepted)
                    or (m.membership_accepted is None)
                )
                # but payment has been received during timespan
                and (m.payment_received)
                and (datetime(
                    m.payment_received_date.year,
                    m.payment_received_date.month,
                    m.payment_received_date.day,
                ) >= start_date)
                and (datetime(
                    m.payment_received_date.year,
                    m.payment_received_date.month,
                    m.payment_received_date.day,
                ) <= end_date)):
            _num_afm_shares_paid_unapproved += m.num_shares
            _afm_shares_paid_unapproved.append(m)

    # shares
    _count_shares = 0
    _new_shares = []
    _num_shares_paid_unapproved = 0
    _shares_paid_unapproved = []

    _all_shares = Shares.get_all()
    for s in _all_shares:
        if s is not None:

            if (  # shares approved during span
                    (datetime(
                        s.date_of_acquisition.year,
                        s.date_of_acquisition.month,
                        s.date_of_acquisition.day,
                    ) >= start_date)
                    and (datetime(
                        s.date_of_acquisition.year,
                        s.date_of_acquisition.month,
                        s.date_of_acquisition.day,
                    ) <= end_date)
            ):
                _count_shares += s.number
                _new_shares.append(s)

            elif (  # shares NOT approved before end of span
                    (datetime(
                        s.date_of_acquisition.year,
                        s.date_of_acquisition.month,
                        s.date_of_acquisition.day,
                    ) >= end_date)
                    and (datetime(  # payment received during ...
                        s.payment_received_date.year,
                        s.payment_received_date.month,
                        s.payment_received_date.day,
                    ) >= start_date)
                    and (datetime(  # payment received during ...
                        s.payment_received_date.year,
                        s.payment_received_date.month,
                        s.payment_received_date.day,
                    ) <= end_date)
            ):
                _num_shares_paid_unapproved += s.number
                _shares_paid_unapproved.append(s)

    html = form.render()

    return {
        'form': html,
        # dates
        'start_date': start_date,
        'end_date': end_date,
        'datetime': datetime,
        # members
        'new_members': _members,
        'num_members': _num_members,
        # shares
        'num_shares': _count_shares,
        'sum_shares': _count_shares * 50,
        'new_shares': _new_shares,
        # afm shares paid but unapproved
        'num_afm_shares_paid_unapproved': _num_afm_shares_paid_unapproved,
        'afm_paid_unapproved_shares': _afm_shares_paid_unapproved,
        # other shares paid but unapproved
        'num_shares_paid_unapproved': _num_shares_paid_unapproved,
        'paid_unapproved_shares': _shares_paid_unapproved,
    }
