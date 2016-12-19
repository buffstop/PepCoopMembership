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
from datetime import (
    date,
    datetime,
)

import os
import shutil
import subprocess
import tempfile

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config

from c3smembership.data.model.base import DBSession
from c3smembership.models import (
    C3sMember,
    Shares,
)
from c3smembership.tex_tools import TexTools

DEBUG = False


@view_config(permission='manage',
             route_name='membership_listing_date_pdf')
def member_list_date_pdf_view(request):
    """
    The membership list *for a given date* for printout as PDF.
    The date is supplied in and parsed from the URL, e.g.
    http://0.0.0.0:6543/aml-2014-12-31.pdf

    The PDF is generated using pdflatex.

    If the date is not parseable, an error message is shown.
    """
    DEBUG = False
    try:
        _date_m = request.matchdict['date']
        _date = datetime.strptime(_date_m, '%Y-%m-%d').date()
    except (KeyError, ValueError):
        request.session.flash(
            "Invalid date! '{}' does not compute! "
            "try again, please! (YYYY-MM-DD)".format(
                _date_m),
            'message_to_user'
        )
        return HTTPFound(request.route_url('error_page'))

    """
    All member entries are loaded.
    """
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

    """
    ...and filtered for

    * active members (membership_accepted)
    * with membership numbers (cross-check)
    * who have become members before the given date.

    They are added to a list and counted.
    Their shares (those acquired before the date) are counted as well.

    """
    # filter and count memberships and shares
    for item in _all_members:
        if (
                (item.membership_number is not None) and
                item.is_member(_date)):
            # add this item to the filtered list of members
            _members.append(item)
            _count_members += 1
            # also count their shares iff acquired in the timespan
            for share in item.shares:
                if (date(
                        share.date_of_acquisition.year,
                        share.date_of_acquisition.month,
                        share.date_of_acquisition.day,
                ) <= _date):
                    _count_shares += share.number

    """
    The list of members is then sorted by

    * their given name
    * their last name,

    using locale.strcoll with german locale.
    This achieves a sort order like in phone books.
    """

    # sort members alphabetically
    import locale
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    # ...by fist name
    _members.sort(key=lambda x: x.firstname, cmp=locale.strcoll)
    # ...and then by their last name
    _members.sort(key=lambda x: x.lastname, cmp=locale.strcoll)

    """
    Then a LaTeX file is constructed...
    """
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
    pdf_file.name = latex_file.name.replace('.tex', '.pdf')

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
            if date(
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
            ''' {0} & {1} & {2} & {3} & {4} & {5} & {6}  \\\\\\hline %
            '''.format(
                TexTools.escape(member.lastname).encode('utf-8'),  # 0
                ' \\footnotesize ' + TexTools.escape(
                    member.firstname).encode('utf-8'),  # 1
                ' \\footnotesize ' + TexTools.escape(
                    str(member.membership_number)),  # 2
                _address,  # 3
                ' \\footnotesize ' + member.membership_date.strftime(
                    '%d.%m.%Y'),  # 4
                ' \\footnotesize ' + membership_loss + ' ',  # 5
                ' \\footnotesize ' + str(_acquired_shares_until_date)  # 6
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
    if DEBUG:  # pragma: no cover
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
            if DEBUG:  # pragma: no cover
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
    This view produces printable HTML output, i.e. HTML without links

    It was used before the PDF-generating view above existed
    """
    all_members = C3sMember.member_listing(
        'lastname', how_many=C3sMember.get_number(), offset=0, order=u'asc')
    member_list = []
    count = 0
    for member in all_members:
        if member.is_member():
            # check membership number
            try:
                assert(member.membership_number is not None)
            except AssertionError:
                pass
                if DEBUG:  # pragma: no cover
                    print u"failed at id {} lastname {}".format(
                        member.id, member.lastname)
            member_list.append(member)
            count += 1
    # sort members alphabetically
    import locale
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")

    member_list.sort(key=lambda x: x.firstname, cmp=locale.strcoll)
    member_list.sort(key=lambda x: x.lastname, cmp=locale.strcoll)

    return {
        'members': member_list,
        'count': count,
        '_today': date.today(),
    }


@view_config(permission='manage',
             route_name='merge_member')
def merge_member_view(request):
    """
    Merges member duplicates into one member record.

    Some people have more than one entry in our C3SMember table,
    e.g. because they used the application form more than once
    to acquire more shares.

    They shall not, however, become members twice and get more than one
    membership number. So we try and merge them:

    If a person is already a member and acquires a second package of shares,
    this package of shares is added to the former membership entry.
    The second entry in the C3sMember table is given the 'is_duplicate' flag
    and also the 'duplicate_of' is given the *id* of the original entry.
    """
    DEBUG = False
    _id = request.matchdict['afm_id']
    _mid = request.matchdict['mid']
    if DEBUG:  # pragma: no cover
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
    # print "the date for the shares: {} (s: {}; p: {})".format(
    #    _date_for_shares,
    #    merg.signature_received_date,
    #    merg.payment_received_date
    # )
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
    Turns a membership applicant into an accepted member.

    When both the signature and the payment for the shares have arrived at
    headquarters, an application for membership can be turned into an
    **accepted membership**, if the board of directors decides so.

    This view lets staff enter a date of approval through a form.

    It also provides staff with listings of

    * members with same first name
    * members with same last name
    * members with same email address
    * members with same date of birth

    so staff can decide if this may become a proper membership
    or whether this application is a duplicate of some accepted membership
    and should be merged with some other entry.

    In case of duplicate/merge, also check if the number of shares
    when combining both entries would exceed 60,
    the maximum number of shares a member can hold.
    """
    _id = request.matchdict['afm_id']
    try:  # does that id make sense? member exists?
        member = C3sMember.get_by_id(_id)
        assert(isinstance(member, C3sMember))  # is an application
        # assert(isinstance(member.membership_number, NoneType)
        # not has number
    except AssertionError:
        return HTTPFound(
            location=request.route_url('dashboard'))
    if member.membership_accepted:
        # request.session.flash('id {} is already accepted member!')
        return HTTPFound(request.route_url('detail', memberid=member.id))

    if not (member.signature_received and member.payment_received):
        request.session.flash('signature or payment missing!', 'messages')
        return HTTPFound(request.route_url('dashboard'))

    if 'make_member' in request.POST:
        # print "yes! contents: {}".format(request.POST['make_member'])
        try:
            member.membership_date = datetime.strptime(
                request.POST['membership_date'], '%Y-%m-%d').date()
        except ValueError, value_error:
            request.session.flash(value_error.message, 'merge_message')
            return HTTPFound(
                request.route_url('make_member', afm_id=member.id))

        member.membership_accepted = True
        if member.is_legalentity:
            member.membership_type = u'investing'
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
        # return the user to the page she came from
        if 'referrer' in request.POST:
            if request.POST['referrer'] == 'dashboard':
                return HTTPFound(request.route_url('dashboard'))
            if request.POST['referrer'] == 'detail':
                return HTTPFound(
                    request.route_url('detail', memberid=member.id))
        return HTTPFound(request.route_url('detail', memberid=member.id))

    referrer = ''
    if 'dashboard' in request.referrer:
        referrer = 'dashboard'
    if 'detail' in request.referrer:
        referrer = 'detail'
    return {
        'member': member,
        'next_mship_number': C3sMember.get_next_free_membership_number(),
        'same_mships_firstn': C3sMember.get_same_firstnames(member.firstname),
        'same_mships_lastn': C3sMember.get_same_lastnames(member.lastname),
        'same_mships_email': C3sMember.get_same_email(member.email),
        'same_mships_dob': C3sMember.get_same_date_of_birth(
            member.date_of_birth),
        # keep information about the page the user came from in order to
        # return her to this page
        'referrer': referrer,
    }
