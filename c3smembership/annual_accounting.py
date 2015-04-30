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
    """
    # defaults
    start_date = datetime(date.today().year, 1, 1)  # first day of this year
    end_date = end_date = datetime(date.today().year, 12, 31)  # and last
    appstruct = {
        'startdate': start_date,
        'enddate': end_date
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
            return{'form': e.render()}

    else:  # if form not submitted, preload values
        form.set_appstruct(appstruct)

    # prepare: get information from the database
    # get memberships
    _order_by = 'lastname'
    _num = C3sMember.get_number()  # count objects in DB
    _all = C3sMember.member_listing(  # get all
        _order_by, how_many=_num, offset=0, order=u'asc')

    _members = []  # all the members matching the criteria

    for item in _all:
        if (
                item.membership_accepted  # unneccessary!?
                and (item.membership_date >= start_date)
                and (item.membership_date <= end_date)
        ):
            # add this item to the list
            _members.append(item)
            num_members += 1
            # also count the shares
            # for _s in item.shares:
            #    if (_s.date_of_acquisition <= _date):
            #        _count_shares += _s.number

    # shares
    _count_shares = 0
    _num_shares_in_db = Shares.get_number()
    for i in range(_num_shares_in_db):
        s = Shares.get_by_id(i+1)

        if (
                (s.date_of_acquisition >= start_date)
                and (s.date_of_acquisition <= end_date)
        ):
            _count_shares += s.number

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
        'sum_shares': num_shares * 50,
    }
