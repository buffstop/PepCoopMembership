from datetime import datetime
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from c3smembership.models import (
    DBSession,
    C3sMember,
    Shares,
)


@view_config(renderer='templates/member_list.pt',
             permission='manage',
             route_name='membership_listing_alphabetical')
def member_list_print_view(request):
    _order_by = 'lastname'
    _num = C3sMember.get_number()
    _all = C3sMember.member_listing(
        _order_by, how_many=_num, offset=0, order=u'asc')
    _members = []
    _count = 0
    for item in _all:
        if item.membership_accepted:
            # check membership number
            try:
                assert(item.membership_number is not None)
            except:
                print "failed at id {} lastname {}".format(
                    item.id, item.lastname)
            # add this item to the list
            _members.append(item)
            _count += 1
    # sort members alphabetically
    import locale
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    _members.sort(key=lambda x: x.lastname, cmp=locale.strcoll)
    from datetime import date
    _today = date.today()
    return {
        'members': _members,
        'count': _count,
        '_today': _today,
    }


@view_config(renderer='templates/memberships_list_backend.pt',
             permission='manage',
             route_name='membership_listing_backend')
def membership_listing_backend(request):
    """
    This view lets accountants viev all members.
    """
    _message = ''
    try:  # check if page number, orderby and order were supplied with the URL
        _page_to_show = int(request.matchdict['number'])
        _order_by = request.matchdict['orderby']
        _order = request.matchdict['order']
    except:
        #print("Using default values")
        _page_to_show = 0
        _order_by = 'id'
        _order = 'asc'

    """
    num_display determines how many items are to be shown on one page
    """
    if 'num_to_show' in request.POST:
        try:
            _num = int(request.POST['num_to_show'])
            if isinstance(_num, type(1)):
                m_num_display = _num
        except:
            # choose default
            m_num_display = 20
    elif 'm_num_display' in request.cookies:
        #print("found it in cookie")
        m_num_display = int(request.cookies['m_num_display'])
    else:
        #print("setting default")
        if 'c3smembership.membership_number' in request.registry.settings:
            m_num_display = request.registry.settings[
                'c3smembership.membership_number']
        else:
            m_num_display = 20

    """
    base_offset helps us to minimize impact on the database
    when querying for results.
    we can choose just those results we need for the page to show
    """

    base_offset = int(_page_to_show) * int(m_num_display)
    # get data sets from DB
    memberships = C3sMember.get_members(
        _order_by, how_many=m_num_display, offset=base_offset, order=_order)

    # calculate next-previous-navi
    next_page = (int(_page_to_show) + 1)
    if (int(_page_to_show) > 0):
        previous_page = int(_page_to_show) - 1
    else:
        previous_page = int(_page_to_show)
    import math
    _last_page = int(math.ceil(
        C3sMember.get_num_members_accepted() / int(m_num_display)))
    if next_page > _last_page:
        next_page = _last_page
    # store info about current page in cookie
    request.response.set_cookie('m_on_page', value=str(_page_to_show))
    request.response.set_cookie('m_num_display', value=str(m_num_display))
    request.response.set_cookie('m_order', value=str(_order))
    request.response.set_cookie('m_orderby', value=str(_order_by))

    return {
        'members': memberships,
        '_number_of_datasets': C3sMember.get_num_members_accepted(),
        #'num_mships': C3sMember.get_num_members_accepted(),
        'num_display': m_num_display,
        'next': next_page,
        'previous': previous_page,
        'current': _page_to_show,
        'orderby': _order_by,
        'order': _order,
        'message': _message,
        'last_page': _last_page,
        'is_last_page': _page_to_show == _last_page,
        'is_first_page': _page_to_show == 0,
    }


@view_config(permission='manage',
             route_name='merge_member')
def merge_member_view(request):
    _id = request.matchdict['afm_id']
    _mid = request.matchdict['mid']
    print "shall merge {} to {}".format(_id, _mid)

    orig = C3sMember.get_by_id(_mid)
    merg = C3sMember.get_by_id(_id)

    if not (orig.membership_accepted):
        request.session.flash(
            'you can only merge to accepted members!',
            'merge_message')
        HTTPFound(request.route_url('make_member', afm_id=_id))
    #print "resulting number of shares: {}".format(
    #    int(orig.num_shares) + int(merg.num_shares))
    #print "resulting number of shares exceeds 60? {}".format(
    #    int(orig.num_shares) + int(merg.num_shares) > 60)
    exceeds_60 = int(orig.num_shares) + int(merg.num_shares) > 60
    if exceeds_60:
        request.session.flash(
            'merger would exceed 60 shares!',
            'merge_message')
        return HTTPFound(request.route_url('make_member', afm_id=_id))
    shares = Shares(
        number=merg.num_shares,
        date_of_acquisition=merg.date_of_submission,
        reference_code=merg.email_confirm_code,
        signature_received=merg.signature_received,
        signature_received_date=merg.signature_received_date,
        payment_received=merg.payment_received,
        payment_received_date=merg.payment_received_date,
    )
    DBSession.add(shares)  # persist
    orig.shares.append(shares)
    orig.num_shares += merg.num_shares
    DBSession.delete(merg)

    return HTTPFound(request.route_url('detail', memberid=_mid))


@view_config(renderer='templates/make_member.pt',
             permission='manage',
             route_name='make_member')
def make_member_view(request):
    _id = request.matchdict['afm_id']
    try:  # does that id make sense? member exists?
        _m = C3sMember.get_by_id(_id)
        assert(isinstance(_m, C3sMember))  # is an application
        #assert(isinstance(_m.membership_number, NoneType)  # not has number
    except:
        return HTTPFound(
            location=request.route_url('dashboard_only'))
    if _m.membership_accepted:
        #request.session.flash('id {} is already accepted member!')
        return HTTPFound(request.route_url('detail', memberid=_m.id))

    if 'make_member' in request.POST:
        #print "yes! contents: {}".format(request.POST['make_member'])
        try:
            _m.membership_date = datetime.strptime(
                request.POST['membership_date'], '%Y-%m-%d')
        except ValueError, ve:
            request.session.flash(ve.message, 'merge_message')
            return HTTPFound(request.route_url('make_member', afm_id=_m.id))

        _m.membership_accepted = True
        if _m.is_legalentity:
            _m.membership_type = 'investing'
        else:
            _m.is_legalentity = False
        _m.membership_number = C3sMember.get_next_free_membership_number()
        shares = Shares(
            number=_m.num_shares,
            date_of_acquisition=_m.date_of_submission,
            reference_code=_m.email_confirm_code,
            signature_received=_m.signature_received,
            signature_received_date=_m.signature_received_date,
            payment_received=_m.payment_received,
            payment_received_date=_m.payment_received_date
        )
        DBSession.add(shares)
        _m.shares = [shares]
        return HTTPFound(request.route_url('detail', memberid=_m.id))

    return {
        'member': _m,
        'next_mship_number': C3sMember.get_next_free_membership_number(),
        'same_mships_firstn': C3sMember.get_same_firstnames(_m.firstname),
        'same_mships_lastn': C3sMember.get_same_lastnames(_m.lastname),
        'same_mships_email': C3sMember.get_same_email(_m.email),
        'same_mships_dob': C3sMember.get_same_date_of_birth(
            _m.date_of_birth),
        #'same_mships_city': C3sMember.get_same_city(_m.city),
        #'same_mships_postcode': C3sMember.get_same_postcode(_m.postcode),
    }


@view_config(permission='manage',
             route_name='flag_duplicates')
def flag_duplicates(request):
    '''
    known duplicate entries by members that found their way into the DB
    need to be flagged so their packages of shares can be attributed
    to *one* account, and they may only get *one* membership number.

    mapping id ranges to membership applications:
    1st: founders:        #1017 - 1066 (50pc.)
    2nd: startnext items: #496 - #1016 (520pc. )order_by email_confirm_code
    3rd: yes submissions: #1 - #495 (410pc.) order_by date_of_submission
                          #1067 - #1092 (25pc.)
                          #1109 - end...
    4th: legal entities   #1093 - #1108

    '''
    duplicates = [
        #(original, duplicate),
        # founders first, with their duplicates
        (1017, 396),  # yes
        (1048, 682),  # startnext
        (1027, 829),  # startnext
        (1030, 102),  # yes
        # startnexter with duplicates (all yes'sers)
        (538, 92),
        (740, 98),
        (759, 93),
        (700, 113),
        (738, 123),
        (895, 129),
        (870, 141),
        (553, 151),
        (803, 156),
        (608, 159),
        (701, 192),
        (710, 218),
        (569, 220),
        (861, 252),
        (683, 284),
        # yes'er with duplicates (all yes'sers)
        (83, 211),
        (155, 368),
        (172, 479),
        (173, 480),
    ]
    # make sure the lastnames match and combined shares do not exceed 60
    for d in duplicates:
        #print "--> d[0]: {}; d[1]: {}".format(d[0], d[1])
        orig = C3sMember.get_by_id(d[0])
        dupl = C3sMember.get_by_id(d[1])
        assert(orig.lastname == dupl.lastname)
        assert(orig.num_shares + dupl.num_shares < 60)

    for d in duplicates:
        print "--> original: {}; duplicate: {}".format(d[0], d[1])
        orig = C3sMember.get_by_id(d[0])
        dupl = C3sMember.get_by_id(d[1])
        # set flags
        dupl.is_duplicate = True
        dupl.is_duplicate_of = orig.id
    request.session.flash('duplicates were flagged.', 'message_to_staff')
    return HTTPFound(
        location=request.route_url('toolbox'))


@view_config(permission='manage',
             route_name='make_founders_members')
def make_founders_members(request):
    '''
    give membership status, date and number to the founders
    '''
    _order_by = 'id'
    _founders = C3sMember.get_range_ids(
        _order_by,  # order as in database (by id)
        first_id=1017,  # we have 50 founders
        last_id=1066,  # starting at 932, omit 1st 931
        order=u'asc')
    print "got {} items.".format(len(_founders))
    #print "first:"
    #print _founders[0].firstname
    #print "last:"
    #print _founders[49].firstname
    try:  # sanity check
        for _f in _founders:
            #print u"founder id: {} firstname: {} refcode: {}".format(
            #_f.id, _f.firstname, _f.email_confirm_code
            #)
            assert(_f.email_confirm_code.split('_')[0].endswith('dungHH'))
            assert(_f.date_of_submission == datetime(2013, 9, 25))
            assert(_f.signature_received_date == datetime(2013, 9, 25))
            assert(_f.payment_received_date == datetime(2013, 9, 25))
    except:
        print "failed sanity check!"
        request.session.flash('failed sanity check.', 'message_to_staff')
        return HTTPFound(location=request.route_url('toolbox'))

    #try:
    for _f in _founders:
        # make member
        _f.membership_accepted = True
        _f.membership_date = datetime(2013, 9, 25)
        _f.is_legalentity = False
        # prepare numbering
        _number = int(_f.email_confirm_code.split('_')[1])
        #print "the number from refcode: {}".format(_number)
        # membership_number
        if _number < 20:
            _f.membership_number = _number
        elif _number == 20:  # the phorsicht case
            _f.membership_number = 999999999
        elif _number > 20:
            _f.membership_number = _number - 1
        print "number given to id {}: {}".format(
            _f.id, _f.membership_number
        )
        #debug
        #print u"email_confirm_code: {}".format(_f.email_confirm_code)
        #print "signature_received: {}".format(_f.signature_received)
        #print "signature_received_date: {}".format(_f.signature_received_date)
        #print "payment_received: {}".format(_f.payment_received)
        #print "payment_received_date: {}".format(_f.payment_received_date)
        #print ": {}".format(_f.)

        # handle shares
        try:
            shares = Shares(
                number=_f.num_shares,
                date_of_acquisition=datetime(2013, 9, 25),
                reference_code=_f.email_confirm_code,
                signature_received=_f.signature_received,
                signature_received_date=_f.signature_received_date,
                payment_received=_f.payment_received,
                payment_received_date=_f.payment_received_date
            )
            DBSession.add(shares)
            _f.shares = [shares]
        except:
            print "shares failed for id {}!".format(_f.id)

    request.session.flash('made founders members.', 'message_to_staff')
    return HTTPFound(
        location=request.route_url('toolbox'))


@view_config(permission='manage',
             route_name='make_crowdfounders_members')
def make_crowdfounders_members(request):
    '''
    give membership status, date and number to the crowdfounders
    '''
    _order_by = 'id'
    _crowdfounders = C3sMember.get_range_ids(
        _order_by,  # order as in database (by id)
        first_id=496,  # we have 520 founders
        last_id=1016,  # starting at 411, omit 1st 410
        order=u'asc')
    print "got {} items.".format(len(_crowdfounders))
    try:  # sanity check
        print "checking crowdfounder data"
        for _f in _crowdfounders:
            #print u"crowdfounder id: {} firstname: {} refcode: {}".format(
            #    _f.id, _f.firstname, _f.email_confirm_code
            #)
            assert(_f.email_confirm_code.startswith('TR001'))
            #assert(_f.date_of_submission == datetime(2014, 6, 27))
            assert(_f.signature_received_date == datetime(1970, 1, 1))
            assert(_f.payment_received_date == datetime(1970, 1, 1))
    except:
        print "failed sanity check!"
        return HTTPFound(location=request.route_url('toolbox'))
    #try:
    print "about to flag crowdfounders as members and register their shares"
    for _f in _crowdfounders:
        # if it is a duplicate, don't
        if _f.is_duplicate:
            print "found duplicate id {}, continuing with next...".format(_f.id)
            continue
        # make member
        _f.membership_accepted = True
        _f.membership_date = _f.date_of_submission
        #print "DEBUG: date of membership: {}".format(_f.date_of_submission)
        _f.is_legalentity = False

        # handle shares
        shares = Shares(
            number=_f.num_shares,
            date_of_acquisition=_f.date_of_submission,  # this holds for
            # all crowdfounders, because we imported it to that field.
            # we had no better data. and we got them only upon entry
            # into the register of cooperatives (genossenschaftsregister).
            # but still we have order within the crowdfounders because we
            # can use the startnext reference code for ordering
            reference_code=_f.email_confirm_code,
            signature_received=_f.signature_received,
            signature_received_date=_f.signature_received_date,
            payment_received=_f.payment_received,
            payment_received_date=_f.payment_received_date,
        )
        DBSession.add(shares)  # persist
        _f.shares = [shares]
        #print "number of shares before: {}".format(_f.num_shares)
        #_f.num_shares += shares.number  # update number of shares
        #print "number of shares after: {}".format(_f.num_shares)

    _cf_sorted = []
    _cf_sorted = sorted(
        _crowdfounders, key=lambda x: x.email_confirm_code)
    #print len(_cf_sorted)

    highest_mem_num = 49  # we know this (see make_founders_members)
    print "giving membership numbers to crowdfounders..."
    for i in _cf_sorted:
        # if is_duplicate: don't!
        if i.is_duplicate:
            print "found duplicate id {}, continuing with next...".format(i.id)
            continue
        highest_mem_num += 1
        i.membership_number = highest_mem_num
        print "member id {} with code {} got number {}".format(
            i.id, i.email_confirm_code, highest_mem_num)
    request.session.flash('made crowdfounders members.', 'message_to_staff')
    return HTTPFound(
        location=request.route_url('toolbox'))


@view_config(permission='manage',
             route_name='make_yesser_members')
def make_yesser_members(request):
    '''
    give membership status, date and number
    to the people who used the main form.

    some are at the top in the db, some at the bottom,
    because the crowdfounders and founders
    were imported in between.
    '''
    _order_by = 'id'
    _range_1 = C3sMember.get_range_ids(
        _order_by,  # order as in database (by id)
        first_id=1,  # the first set
        last_id=495,  # starting at 1
        order=u'asc')
    print "got {} items.".format(len(_range_1))

    #prepare membership_number
    #_next_mship_number = int(C3sMember.get_next_free_membership_number())

    yes_mergelater = []

    # iterate
    def make_members(_range):
        #global yes_mergelater
        for i in _range:
            if i.is_duplicate:
                print "--> id {} is a duplicate.".format(i.id)
                continue
            if (  # check for cutoff date
                    (i.signature_received and i.payment_received) and
                    ((i.signature_received_date > datetime(2014, 07, 16)) or
                    (i.payment_received_date > datetime(2014, 07, 16)))
            ):
                print "got one with date later than 2014-07-16: id {}".format(
                    i.id)
                continue  # do not make member now...

            if (  # check for date of registry
                    (i.signature_received and i.payment_received) and
                    ((i.signature_received_date > datetime(2014, 03, 29)) or
                     (i.payment_received_date > datetime(2014, 03, 29)))
            ):
                print "got one with date later than 2014-03-29: id {}".format(
                    i.id)
                yes_mergelater.append(i.id)
                continue  # do not make member now...
            if (
                    (i.signature_received and i.payment_received) and
                    (i.signature_received_date < datetime(2014, 07, 16)) and
                    (i.payment_received_date < datetime(2014, 07, 16))
            ):
                print u"id {} --> member w/ refcode {}".format(
                    i.id,
                    #_next_mship_number,
                    i.email_confirm_code,
                )
                # do it
                i.membership_accepted = True
                i.membership_date = datetime(2014, 3, 29)  # XXX
                # we don't have this date, do we?
                i.is_legalentity = False
                i.membership_number = C3sMember.get_next_free_membership_number()
                #_next_mship_number
                #_next_mship_number.__add__(1)

                # handle shares
                shares = Shares(
                    number=i.num_shares,
                    date_of_acquisition=i.date_of_submission,
                    reference_code=i.email_confirm_code,
                    signature_received=i.signature_received,
                    signature_received_date=i.signature_received_date,
                    payment_received=i.payment_received,
                    payment_received_date=i.payment_received_date,
                )
                DBSession.add(shares)  # persist
                i.shares = [shares]
                DBSession.flush()
                print "got membership number: {}".format(i.membership_number)

    make_members(_range_1)
    print "...done with the first range (id ), off to second..."
    _range_2 = C3sMember.get_range_ids(
        _order_by,  # order as in database (by id)
        first_id=1067,  # the second set
        last_id=1092,  # starting at 982 (id 1067)
        order=u'asc')
    print "got {} items.".format(len(_range_2))
    make_members(_range_2)
    print "...done with the second"

    #_range_3 = C3sMember.get_range_ids(
    #    _order_by,  # order as in database (by id)
    #    first_id=1109,  # the third set
    #    last_id=1500,  # starting at 1013 (id 1109)
    #    order=u'asc')
    #print "got {} items.".format(len(_range_2))
    #make_members(_range_3, count_yes_mergelater)
    print "...done with the last"
    print "did not touch {} afms to be merged later: {}".format(
        len(yes_mergelater), yes_mergelater
    )
    request.session.flash('made yessers members.', 'message_to_staff')
    return HTTPFound(
        location=request.route_url('toolbox'))


@view_config(permission='manage',
             route_name='merge_duplicates')
def merge_duplicates(request):
    '''
    the known duplicates must be attributed to their originals
    '''
    dupes = C3sMember.get_duplicates()
    for d in dupes:
        orig = C3sMember.get_by_id(d.is_duplicate_of)
        dupe = C3sMember.get_by_id(d.id)
        assert(orig.membership_accepted)
        assert(orig.lastname == dupe.lastname)
        assert(orig.num_shares + dupe.num_shares < 60)
        # only if duplicate fulfills requirements
        if dupe.signature_received and dupe.payment_received:

            # the duplicates shares are added to the originals shares
            share_pkg = Shares(
                number=dupe.num_shares,
                date_of_acquisition=dupe.date_of_submission,  # this holds for
                # all crowdfounders, because we imported it to that field.
                # we had no better data.
                # but still we have order within the crowdfounders because we
                # can use the startnext reference code for ordering
                reference_code=dupe.email_confirm_code,
                signature_received=dupe.signature_received,
                signature_received_date=dupe.signature_received_date,
                payment_received=dupe.payment_received,
                payment_received_date=dupe.payment_received_date,
            )
            DBSession.add(share_pkg)  # persist
            orig.shares.append(share_pkg)
            orig.num_shares += dupe.num_shares  # update num_shares
            DBSession.delete(dupe)  # delete the duplicate
            print u"gave {} shares to id {}, now totalling {} shares.".format(
                dupe.num_shares, orig.id,
                orig.num_shares,
            )
    request.session.flash('merged duplicates.', 'message_to_staff')
    return HTTPFound(
        location=request.route_url('toolbox'))
