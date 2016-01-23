# -*- coding: utf-8 -*-
"""
This module holds functionality to handle the C3S SCEs membership list.

Having and maintaining an alphabetical membership list is one of the
obligations of an association like the C3S SCE.

The list is available in several formats:

- HTML with clickable links for browsing
- HTML without links for printout
- PDF (created with pdflatex) for printout (preferred!)

There are also some historic utility functions for reference:

- Turn founders into members
- Turn crowdfunders into members
- Turn form users into members
- Flag duplicates
- Merge duplicates
"""
from datetime import datetime
import os
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
import shutil
import subprocess
import tempfile

from c3smembership.models import (
    DBSession,
    C3sMember,
    Shares,
)
from c3smembership.tex_tools import TexTools


@view_config(renderer='templates/aufstockers_list.pt',
             permission='manage',
             route_name='membership_listing_aufstockers')
def member_list_aufstockers_view(request):
    """
    this view shows all accepted members with
    more than one package of (accepted) shares
    """
    _order_by = 'lastname'
    _num = C3sMember.get_number()
    _all = C3sMember.member_listing(
        _order_by, how_many=_num, offset=0, order=u'asc')
    _members = []
    _count = 0
    for item in _all:
        if item.membership_accepted and (len(item.shares) > 1):
            # check membership number
            try:
                assert(item.membership_number is not None)
            except AssertionError:
                print "failed at id {} lastname {}".format(
                    item.id, item.lastname)
            # add this item to the list
            _members.append(item)
            _count += 1
    # sort members alphabetically
    import locale
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")

    _members.sort(key=lambda x: x.firstname, cmp=locale.strcoll)
    _members.sort(key=lambda x: x.lastname, cmp=locale.strcoll)

    from datetime import date
    _today = date.today()
    return {
        'members': _members,
        'count': _count,
        '_today': _today,
    }


@view_config(renderer='templates/member_list.pt',
             permission='manage',
             route_name='membership_listing_date_pdf')
def member_list_date_pdf_view(request):
    """
    returns the membership list *for a given date* for printout as PDF.
    the date is supplied in and parsed from the URL, e.g.
    http://0.0.0.0:6543/aml-2014-12-31.pdf

    The PDF is generated using pdflatex.
    """
    try:
        _date_m = request.matchdict['date']
        _date = datetime.strptime(_date_m, '%Y-%m-%d')
    except (KeyError, ValueError):
        request.session.flash(
            'Invalid date! ',
            'membership_list_errors'
        )
        return {
            'form': 'nope, invalid date!',
            'count': 'zero',
            '_today': 'n/a',
            'members': [],
        }
    # query the database
    _order_by = 'lastname'
    _num = C3sMember.get_number()
    _all_members = C3sMember.member_listing(
        _order_by, how_many=_num, offset=0, order=u'asc')

    # prepare variables
    _members = []  # the members, filtered
    _count_members = 0  # count those members
    _count_shares = 0  # count their shares
    _count_shares_printed = 0  # cross-check...

    # filter and count memberships and shares
    for item in _all_members:
        if (
                (item.membership_number is not None)
                and (item.membership_accepted)
                and (datetime(  # use only Date, not Hours etc.
                    item.membership_date.year,
                    item.membership_date.month,
                    item.membership_date.day,
                ) <= _date)):
            # add this item to the filtered list of members
            _members.append(item)
            _count_members += 1
            # also count their shares iff acquired in the timespan
            for share in item.shares:
                if (datetime(
                        share.date_of_acquisition.year,
                        share.date_of_acquisition.month,
                        share.date_of_acquisition.day,
                ) <= _date):
                    _count_shares += share.number

    # sort members alphabetically
    import locale
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    # ...by fist name
    _members.sort(key=lambda x: x.firstname, cmp=locale.strcoll)
    # ...and then by their last name
    _members.sort(key=lambda x: x.lastname, cmp=locale.strcoll)

    here = os.path.dirname(__file__)
    latex_header_tex = os.path.abspath(
        os.path.join(here, '../membership_list_pdflatex/header'))
    latex_footer_tex = os.path.abspath(
        os.path.join(here, '../membership_list_pdflatex/footer'))

    # a temporary directory for the latex run
    _tempdir = tempfile.mkdtemp()
    # now we prepare a .tex file to be pdflatex'ed
    latex_file = tempfile.NamedTemporaryFile(
        suffix='.tex',
        dir=_tempdir,
        delete=False,  # directory will be deleted anyways
    )
    # and where to store the output
    pdf_file = tempfile.NamedTemporaryFile(
        dir=_tempdir,
        delete=False,  # directory will be deleted anyways
    )
    pdf_file.name = latex_file.name.rstrip('.tex')
    pdf_file.name += '.pdf'

    # construct latex data: header + variables
    latex_data = '''
\\input{%s}
\\def\\numMembers{%s}
\\def\\numShares{%s}
\\def\\sumShares{%s}
\\def\\today{%s}
    ''' % (
        latex_header_tex,
        _count_members,
        _count_shares,
        _count_shares * 50,
        _date.strftime('%d.%m.%Y'),
    )

    # add to the latex document
    latex_data += '''
\\input{%s}''' % latex_footer_tex

    # print '*' * 70
    # print latex_data
    # print '*' * 70
    latex_file.write(latex_data.encode('utf-8'))

    # make table rows per member
    for member in _members:
        _address = '''\\scriptsize{}'''
        _address += '''{}'''.format(
            unicode(TexTools.escape(member.address1)).encode('utf-8'))

        # check for contents of address2:
        if len(member.address2) > 0:
            _address += '''\\linebreak {}'''.format(
                unicode(TexTools.escape(member.address2)).encode('utf-8'))
        # add more...
        _address += ''' \\linebreak {} '''.format(
            unicode(TexTools.escape(member.postcode)).encode('utf-8'))
        _address += '''{}'''.format(
            unicode(TexTools.escape(member.city)).encode('utf-8'))
        _address += ''' ({})'''.format(
            unicode(TexTools.escape(member.country)).encode('utf-8'))

        # check shares acquired until $date
        _acquired_shares_until_date = 0
        for share in member.shares:
            if datetime(
                    share.date_of_acquisition.year,
                    share.date_of_acquisition.month,
                    share.date_of_acquisition.day) <= _date:
                _acquired_shares_until_date += share.number
                _count_shares_printed += share.number

        membership_loss = u''
        if member.membership_loss_date is not None:
            membership_loss += \
                member.membership_loss_date.strftime('%d.%m.%Y') + \
                '\linebreak '
        if member.membership_loss_type is not None:
            membership_loss += member.membership_loss_type
        latex_file.write(
            ''' {0} & {1} & {2} & {3} & {4} & {5} & {6} & {7} \\\\\\hline %
            '''.format(
                TexTools.escape(member.lastname).encode('utf-8'),  # 0
                ' \\footnotesize ' + TexTools.escape(member.firstname).encode('utf-8'),  # 1
                ' \\footnotesize ' + TexTools.escape(str(member.membership_number)),  # 2
                _address,  # 3
                ' \\footnotesize ' + member.date_of_birth.strftime(
                    '%d.%m.%Y'),  # 4
                ' \\footnotesize ' + member.membership_date.strftime(
                    '%d.%m.%Y'),  # 5
                ' \\footnotesize ' + membership_loss + ' ',  # 6
                ' \\footnotesize ' + str(_acquired_shares_until_date)  # 7
            ))

    latex_file.write('''
%\\end{tabular}%
\\end{longtable}%
\\label{LastPage}
\\end{document}
''')
    latex_file.seek(0)  # rewind

    # pdflatex latex_file to pdf_file
    fnull = open(os.devnull, 'w')  # hide output
    pdflatex_output = subprocess.call(
        [
            'pdflatex',
            '-output-directory=%s' % _tempdir,
            latex_file.name
        ],
        stdout=fnull, stderr=subprocess.STDOUT  # hide output
    )
    print("the output of pdflatex run: %s" % pdflatex_output)

    # if run was a success, run X times more...
    if pdflatex_output == 0:
        for i in range(2):
            pdflatex_output = subprocess.call(
                [
                    'pdflatex',
                    '-output-directory=%s' % _tempdir,
                    latex_file.name
                ],
                stdout=fnull, stderr=subprocess.STDOUT  # hide output
            )
            print("run #{} finished.".format(i+1))

    # sanity check: did we print exactly as many shares as calculated?
    assert(_count_shares == _count_shares_printed)

    # return a pdf file
    response = Response(content_type='application/pdf')
    response.app_iter = open(pdf_file.name, "r")
    shutil.rmtree(_tempdir, ignore_errors=True)  # delete temporary directory
    return response


@view_config(renderer='templates/member_list.pt',
             permission='manage',
             route_name='membership_listing_alphabetical')
def member_list_print_view(request):
    """
    this view produces printable HTML output, i.e. HTML without links

    it was used before the PDF-generating view above existed
    """
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
            except AssertionError:
                print "failed at id {} lastname {}".format(
                    item.id, item.lastname)
            # add this item to the list
            _members.append(item)
            _count += 1
    # sort members alphabetically
    import locale
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")

    _members.sort(key=lambda x: x.firstname, cmp=locale.strcoll)
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
             route_name='membership_listing_backend_only')
@view_config(renderer='templates/memberships_list_backend.pt',
             permission='manage',
             route_name='membership_listing_backend')
def membership_listing_backend(request):
    """
    This view lets accountants view all members.

    the list is HTML with clickable links,
    not good for printout.
    """
    try:  # check if page number, orderby and order were supplied with the URL
        _page_to_show = int(request.matchdict['number'])
        _order_by = request.matchdict['orderby']
        _order = request.matchdict['order']
    except ValueError:
        _page_to_show = 0
        _order_by = 'id'
        _order = 'asc'

    # num_display determines how many items are to be shown on one page
    if 'num_to_show' in request.POST:
        try:
            _num = int(request.POST['num_to_show'])
            if isinstance(_num, int):
                m_num_display = _num
        except ValueError:
            # choose default
            m_num_display = 20
    elif 'm_num_display' in request.cookies:
        m_num_display = int(request.cookies['m_num_display'])
    else:
        if 'c3smembership.membership_number' in request.registry.settings:
            m_num_display = request.registry.settings[
                'c3smembership.membership_number']
        else:
            m_num_display = 20

    # base_offset helps us to minimize impact on the database when querying
    # for results. we can choose just those results we need for the page to
    # show

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

    _message = None
    if 'message' in request.GET:
        _message = request.GET['message']

    return {
        'members': memberships,
        '_number_of_datasets': C3sMember.get_num_members_accepted(),
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
    """
    Merges member duplicates into one member record.
    """
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
    exceeds_60 = int(orig.num_shares) + int(merg.num_shares) > 60
    if exceeds_60:
        request.session.flash(
            'merger would exceed 60 shares!',
            'merge_message')
        return HTTPFound(request.route_url('make_member', afm_id=_id))

    # XXX TODO: this needs fixing!!!
    # date must be set manually according to date of approval of the board
    _date_for_shares = merg.signature_received_date if (
        merg.signature_received_date > merg.payment_received_date
    ) else merg.payment_received_date
    print "the date for the shares: {} (s: {}; p: {})".format(
        _date_for_shares,
        merg.signature_received_date,
        merg.payment_received_date
    )
    shares = Shares(
        number=merg.num_shares,
        date_of_acquisition=_date_for_shares,
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
    """
    Makes a membership applicant into an accepted member.
    """
    _id = request.matchdict['afm_id']
    try:  # does that id make sense? member exists?
        member = C3sMember.get_by_id(_id)
        assert(isinstance(member, C3sMember))  # is an application
        # assert(isinstance(member.membership_number, NoneType)
        # not has number
    except AssertionError:
        return HTTPFound(
            location=request.route_url('dashboard_only'))
    if member.membership_accepted:
        # request.session.flash('id {} is already accepted member!')
        return HTTPFound(request.route_url('detail', memberid=member.id))

    if not (member.signature_received and member.payment_received):
        request.session.flash('signature or payment missing!', 'messages')
        return HTTPFound(request.route_url('dashboard_only'))

    if 'make_member' in request.POST:
        # print "yes! contents: {}".format(request.POST['make_member'])
        try:
            member.membership_date = datetime.strptime(
                request.POST['membership_date'], '%Y-%m-%d')
        except ValueError, value_error:
            request.session.flash(value_error.message, 'merge_message')
            return HTTPFound(request.route_url('make_member', afm_id=member.id))

        member.membership_accepted = True
        if member.is_legalentity:
            member.membership_type = 'investing'
        else:
            member.is_legalentity = False
        member.membership_number = C3sMember.get_next_free_membership_number()
        shares = Shares(
            number=member.num_shares,
            date_of_acquisition=member.membership_date,
            reference_code=member.email_confirm_code,
            signature_received=member.signature_received,
            signature_received_date=member.signature_received_date,
            payment_received=member.payment_received,
            payment_received_date=member.payment_received_date
        )
        DBSession.add(shares)
        member.shares = [shares]
        return HTTPFound(request.route_url('detail', memberid=member.id))

    return {
        'member': member,
        'next_mship_number': C3sMember.get_next_free_membership_number(),
        'same_mships_firstn': C3sMember.get_same_firstnames(member.firstname),
        'same_mships_lastn': C3sMember.get_same_lastnames(member.lastname),
        'same_mships_email': C3sMember.get_same_email(member.email),
        'same_mships_dob': C3sMember.get_same_date_of_birth(
            member.date_of_birth),
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
        # (original, duplicate),
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
    for duplicate in duplicates:
        orig = C3sMember.get_by_id(duplicate[0])
        dupl = C3sMember.get_by_id(duplicate[1])
        assert(orig.lastname == dupl.lastname)
        assert(orig.num_shares + dupl.num_shares < 60)

    for duplicate in duplicates:
        print "--> original: {}; duplicate: {}".format(
            duplicate[0],
            duplicate[1])
        orig = C3sMember.get_by_id(duplicate[0])
        dupl = C3sMember.get_by_id(duplicate[1])
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
    try:  # sanity check
        for founder in _founders:
            assert(founder.email_confirm_code.split('_')[0].endswith('dungHH'))
            assert(founder.date_of_submission == datetime(2013, 9, 25))
            assert(founder.signature_received_date == datetime(2013, 9, 25))
            assert(founder.payment_received_date == datetime(2013, 9, 25))
    except AssertionError:
        print "failed sanity check!"
        request.session.flash('failed sanity check.', 'message_to_staff')
        return HTTPFound(location=request.route_url('toolbox'))

    for founder in _founders:
        # make member
        founder.membership_accepted = True
        founder.membership_date = datetime(2013, 9, 25)
        founder.is_legalentity = False
        # prepare numbering
        _number = int(founder.email_confirm_code.split('_')[1])
        # membership_number
        if _number < 20:
            founder.membership_number = _number
        elif _number == 20:  # the phorsicht case
            founder.membership_number = 999999999
        elif _number > 20:
            founder.membership_number = _number - 1
        print "number given to id {}: {}".format(
            founder.id, founder.membership_number
        )
        # handle shares
        try:
            shares = Shares(
                number=founder.num_shares,
                date_of_acquisition=datetime(2013, 9, 25),
                reference_code=founder.email_confirm_code,
                signature_received=founder.signature_received,
                signature_received_date=founder.signature_received_date,
                payment_received=founder.payment_received,
                payment_received_date=founder.payment_received_date
            )
            DBSession.add(shares)
            founder.shares = [shares]
        except:
            print "shares failed for id {}!".format(founder.id)

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
        for crowdfounder in _crowdfounders:
            assert(crowdfounder.email_confirm_code.startswith('TR001'))
            assert(crowdfounder.signature_received_date == datetime(1970, 1, 1))
            assert(crowdfounder.payment_received_date == datetime(1970, 1, 1))
    except AssertionError:
        print "failed sanity check!"
        return HTTPFound(location=request.route_url('toolbox'))

    print "about to flag crowdfounders as members and register their shares"
    for crowdfounder in _crowdfounders:
        # if it is a duplicate, don't
        if crowdfounder.is_duplicate:
            print "found duplicate id {}, continuing with next...".format(
                crowdfounder.id)
            continue
        # make member
        crowdfounder.membership_accepted = True
        crowdfounder.membership_date = crowdfounder.date_of_submission
        crowdfounder.is_legalentity = False

        # handle shares
        shares = Shares(
            number=crowdfounder.num_shares,
            date_of_acquisition=crowdfounder.date_of_submission,
            # this holds for all crowdfounders, because we imported it to that
            # field. we had no better data. and we got them only upon entry
            # into the register of cooperatives (genossenschaftsregister). but
            # still we have order within the crowdfounders because we can use
            # the startnext reference code for ordering
            reference_code=crowdfounder.email_confirm_code,
            signature_received=crowdfounder.signature_received,
            signature_received_date=crowdfounder.signature_received_date,
            payment_received=crowdfounder.payment_received,
            payment_received_date=crowdfounder.payment_received_date,
        )
        DBSession.add(shares)  # persist
        crowdfounder.shares = [shares]

    _cf_sorted = []
    _cf_sorted = sorted(
        _crowdfounders, key=lambda x: x.email_confirm_code)

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

    # prepare membership_number
    # _next_mship_number = int(C3sMember.get_next_free_membership_number())

    yes_mergelater = []

    # iterate
    def make_members(_range):
        """
        Makes a range of membership applicants to members.
        """
        # global yes_mergelater
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
                    # _next_mship_number,
                    i.email_confirm_code,
                )
                # do it
                i.membership_accepted = True
                i.membership_date = datetime(2014, 3, 29)  # XXX
                # we don't have this date, do we?
                i.is_legalentity = False
                i.membership_number = \
                    C3sMember.get_next_free_membership_number()
                # _next_mship_number
                # _next_mship_number.__add__(1)

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

    # _range_3 = C3sMember.get_range_ids(
    #    _order_by,  # order as in database (by id)
    #    first_id=1109,  # the third set
    #    last_id=1500,  # starting at 1013 (id 1109)
    #    order=u'asc')
    # print "got {} items.".format(len(_range_2))
    # make_members(_range_3, count_yes_mergelater)
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
    duplicates = C3sMember.get_duplicates()
    for duplicate in duplicates:
        orig = C3sMember.get_by_id(duplicate.is_duplicate_of)
        dupe = C3sMember.get_by_id(duplicate.id)
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
