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
    renderer='templates/annual_report.pt',
    permission='manage',
    route_name='annual_reporting'
)
def annual_report(request):
    """
    return the number of members and shares acquired during a given timeframe
    (start date and end date)

    also show the number of shares paid but not 'approved' yet
    - as part of a membership or
    - when additional shares were acquired
    """
    # defaults
    start_date = datetime(date.today().year, 1, 1)  # first day of this year
    end_date = end_date = datetime(date.today().year, 12, 31)  # and last
    appstruct = {
        'startdate': start_date,
        'enddate': end_date,
    }
    num_members = 0
    num_shares = 0

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
        print("SUBMITTED!")
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
            }

    else:  # if form not submitted, preload values
        form.set_appstruct(appstruct)

    # prepare: get information from the database
    # get memberships
    _order_by = 'lastname'
    _num = C3sMember.get_number()  # count objects in DB
    _all_members = C3sMember.member_listing(  # get all
        _order_by, how_many=_num, offset=0, order=u'asc')

    _members = []  # all the members matching the criteria
    _num_shares_paid_unapproved = 0
    _shares_paid_unapproved = []
    for m in _all_members:
        if (
                m.membership_accepted  # unneccessary!?
                and (m.membership_date >= start_date)
                and (m.membership_date <= end_date)
        ):
            # add this item to the list
            _members.append(m)
            num_members += 1
            # also count the shares
            # for _s in item.shares:
            #    if (_s.date_of_acquisition <= _date):
            #        _count_shares += _s.number
        elif (
                (not m.membership_accepted)
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
            _num_shares_paid_unapproved += m.num_shares
            _shares_paid_unapproved.append(m)

    # shares
    _count_shares = 0
    _new_shares = []
    _num_shares_in_db = Shares.get_number()
    for i in range(_num_shares_in_db):
        s = Shares.get_by_id(i+1)
        if s is not None:

            if (  # shares approved
                    (s.date_of_acquisition >= start_date)
                    and (s.date_of_acquisition <= end_date)
            ):
                _count_shares += s.number
                _new_shares.append(s)

    html = form.render()

    num_shares = _count_shares

    # print("the number of members acquired in this timeframe: {}".format(
    #     num_members))
    # print("the number of shares acquired: {}. in Euro: {}".format(
    #     num_shares,
    #     num_shares*50,
    # ))

    return {
        'form': html,
        'num_members': num_members,
        'num_shares': num_shares,
        'new_members': _members,
        'paid_unapproved_shares': _shares_paid_unapproved,
        'num_shares_paid_unapproved': _num_shares_paid_unapproved,
        'sum_shares': num_shares * 50,
        'new_shares': _new_shares,
    }
