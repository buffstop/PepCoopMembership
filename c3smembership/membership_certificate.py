# -*- coding: utf-8 -*-
from datetime import (
    date,
    datetime
)
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.renderers import render
from pyramid.response import Response
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
import re
import shutil
import subprocess
import tempfile
from types import NoneType

from c3smembership.models import C3sMember


def make_random_token():
    """
    used as token to allow access to certificate
    """
    import random
    import string
    return u''.join(
        random.choice(
            string.ascii_lowercase + string.digits
        ) for x in range(15))


@view_config(permission='manage',
             route_name='certificate_mail')
def send_certificate_email(request):
    '''
    send a mail to a member with a link
    so the mamber can get her membership certificate
    '''
    mid = request.matchdict['id']
    _m = C3sMember.get_by_id(mid)
    if isinstance(_m, NoneType) or not _m.membership_accepted:
        return Response(
            'that id does not exist or is not an accepted member. go back',
            status='404 Not Found',)
    # create a token for the certificate
    _m.certificate_token = make_random_token()
    # construct mail
    _name = re.sub(  # # replace characters
        '[^a-zA-Z]',  # other than these
        '-',  # with a -
        _m.lastname + _m.firstname)

    _url = request.route_url('certificate_pdf',
                             id=_m.id, name=_name, token=_m.certificate_token)
    #print '#'*60
    #print _m.certificate_token
    #print _url
    #print '#'*60

    message_body_file_name = \
        'c3smembership/templates/mail/membership_certificate_' + \
        _m.locale + '.txt'
    with open(message_body_file_name, 'rb') as content_file:
        message_body = content_file.read().decode('utf-8')
        message_body = message_body.format(
            name=_m.firstname,
            url=_url
        )

    mailer = get_mailer(request)
    the_message = Message(
        subject=u'C3S-Mitgliedsbescheinigung' if (
            _m.locale == 'de') else u'C3S membership certificate',
        sender='office@c3s.cc',
        recipients=[_m.email, ],
        body = message_body
    )
    mailer.send(the_message)
    _m.certificate_email = True
    _m.certificate_email_date = datetime.now()
    return HTTPFound(
        location=request.route_url(
            'membership_listing_backend',
            number=request.cookies['m_on_page'],
            order=request.cookies['m_order'],
            orderby=request.cookies['m_orderby']) +
        '#member_' + str(_m.id))


@view_config(permission='view',
             route_name='certificate_pdf')
def generate_certificate(request):
    '''
    generate a membership_certificate for a member
    '''
    mid = request.matchdict['id']
    token = request.matchdict['token']

    try:
        _m = C3sMember.get_by_id(mid)
        #print _m.firstname
        #print _m.certificate_token
        #print type(_m.certificate_token)  # NoneType
        #print token
        #print type(token)  # unicode
        assert(_m.certificate_token is not None)
        assert(str(_m.certificate_token) in str(token))
        assert(str(token) in str(_m.certificate_token))
        # check age of token
        from datetime import timedelta
        _2weeks = timedelta(weeks=2)
        token_date = _m.certificate_email_date
        #print "token_date: {}".format(token_date)
        present = datetime.now()
        _delta = present - token_date
        #if (_delta > _2weeks):
        #    print "more than two weeks!"
        #else:
        #    print "less than two weeks!"
        assert(_delta < _2weeks)
    except:
        return Response(
            'Not found. Please contact office@c3s.cc. <br /><br /> '
            'Nicht gefunden. Bitte office@c3s.cc kontaktieren.',
            status='404 Not Found',
        )
    return gen_cert(request, _m)


@view_config(permission='manage',
             route_name='certificate_pdf_staff')
def generate_certificate_staff(request):
    '''
    generate a membership_certificate for staffers
    '''
    mid = request.matchdict['id']

    try:
        _m = C3sMember.get_by_id(mid)
        assert(not isinstance(_m, NoneType))
    except:
        return Response(
            'Not found. Please check URL.',
        )
    return gen_cert(request, _m)


def gen_cert(request, _m):
    '''
    create a membership certificate PDF file using pdflatex
    '''
    import os
    here = os.path.dirname(__file__)
    # latex header and footer
    latex_header_tex = os.path.abspath(
        os.path.join(here, '../certificate/urkunde_header.tex'))
    #print("latex header file: %s" % latex_header_tex)
    latex_footer_tex = os.path.abspath(
        os.path.join(here, '../certificate/urkunde_footer.tex'))
    #print("latex footer file: %s" % latex_footer_tex)
    #print '#'*60
    #print _m.locale
    #print '#'*60

    if _m.locale == 'de':
        latex_background_image = os.path.abspath(
            os.path.join(here, '../certificate/Urkunde_Hintergrund.pdf'))
    else:
        latex_background_image = os.path.abspath(
            os.path.join(here, '../certificate/Urkunde_Hintergrund_EN.pdf'))
    sign_meik = os.path.abspath(
        os.path.join(here, '../certificate/sign_meik.png'))
    sign_wolfgang = os.path.abspath(
        os.path.join(here, '../certificate/sign_wolfgang.png'))

    # a temporary directory for the latex run
    _tempdir = tempfile.mkdtemp()
    #print("new temporary directory: %s" % _tempdir)

    latex_file = tempfile.NamedTemporaryFile(
        suffix='.tex',
        dir=_tempdir,
        delete=False,  # directory will be deleted anyways
    )
    #print "the latex file: {}".format(latex_file.name)

    # using tempfile
    pdf_file = tempfile.NamedTemporaryFile(
        dir=_tempdir,
        delete=False,  # directory will be deleted anyways
    )
    pdf_file.name = latex_file.name.rstrip('.tex')  # + '.pdf'
    pdf_file.name += '.pdf'

    is_founder = True if 'dungHH_' in _m.email_confirm_code else False
    #print u"email confirm code: {}".format(_m.email_confirm_code)
    #print u"is a founding member? {}".format(
    #    True if 'dungHH_' in _m.email_confirm_code else False)
    # prepare the certificate text
    if _m.locale == 'de':  # german
        hereby_confirmed = u'Hiermit wird bestätigt, dass'
        is_member = u'Mitglied der Cultural Commons Collecting Society SCE ' \
                    u'mit beschränkter Haftung (C3S SCE) ist'
        one_more_share = u' und einen weiteren Geschäftsanteil übernommen hat'
        several_shares = u' weitere Geschäftsanteile übernommen hat'
        and_block = u' und '
        if is_founder:
            confirm_date = (
                u'Der Beitritt erfolgte im Rahmen der Gründung am 25.09.2013')
        else:
            confirm_date = u'Der Beitritt wurde am {} zugelassen'.format(
                datetime.strftime(_m.membership_date, '%d.%m.%Y'))
        mship_num = u'Die Mitgliedsnummer lautet {}.'.format(
            _m.membership_number
        )
        mship_num_text = u'Mitgliedsnummer {}'.format(
            _m.membership_number
        )
        exec_dir = u'Geschäftsführender Direktor'

    else:  # default fallback is english
        hereby_confirmed = u'This is to certify that'
        is_member = u'is a member of the >>Cultural Commons Collecting ' \
                    u'Society SCE mit beschränkter Haftung (C3S SCE)<<'
        one_more_share = u' and has subscribed to one additional share'
        several_shares = u'additional shares'
        and_block = u' and has subscribed to'
        if is_founder:
            confirm_date = (
                u'Membership was aquired as a founding member '
                'on the 25th of September 2013')
        else:
            confirm_date = u'Registered on the {}'.format(
                datetime.strftime(_m.membership_date, '%Y-%m-%d'))
        mship_num = u'The membership number is {}.'.format(
            _m.membership_number
        )
        mship_num_text = u'membership number {}'.format(
            _m.membership_number
        )
        exec_dir = 'Executive Director'

    # construct latex_file
    latex_data = '''
\input{%s}
\def\\backgroundImage{%s}
\def\\txtBlkHerebyConfirmed{%s}
\def\\firstName{%s}
\def\\lastName{%s}
\def\\addressOne{%s}
\def\\postCode{%s}
\def\\city{%s}
\def\\numShares{%s}
\def\\numAddShares{%s}
\def\\txtBlkIsMember{%s}
\def\\txtBlkMembershipNumber{%s}
\def\\txtBlkConfirmDate{%s}
\def\\signDate{%s}
\def\signMeik{%s}
\def\signWolfgang{%s}
\def\\txtBlkCEO{%s}
\def\\txtBlkMembershipNum{%s}
    ''' % (
        latex_header_tex,
        latex_background_image,
        hereby_confirmed,
        _m.firstname,
        _m.lastname,
        _m.address1,
        _m.postcode,
        _m.city,
        _m.num_shares,
        _m.num_shares-1,
        is_member,
        mship_num,
        confirm_date,
        datetime.strftime(
            date.today(), "%d.%m.%Y") if _m.locale == 'de' else date.today(),
        sign_meik,
        sign_wolfgang,
        exec_dir,
        mship_num_text,
    )
    if _m.is_legalentity:  # XXX TODO: field of company name
        latex_data += '''
\def\\company{%s}''' % _m.firstname
    if _m.address2 is not u'':  # add address part 2 iff exists
        latex_data += '''
\def\\addressTwo{%s}''' % _m.address2
    if _m.num_shares > 1:  # how many shares?
        if _m.num_shares == 2:  # iff member has exactely two shares...
            latex_data += '''
\def\\txtBlkAddShares{%s.}''' % one_more_share
        if _m.num_shares > 2:  # iff more than two
            latex_data += '''
\def\\txtBlkAddShares{%s %s %s.}''' % (
                and_block,
                _m.num_shares-1,
                several_shares
            )
    else:  # iff member has exactely one share..
        latex_data += '''
\def\\txtBlkAddShares{.}'''

    # escape some characters to appease LaTeX
    latex_data = re.sub('&', '\&', latex_data)
    latex_data = re.sub('#', '\#', latex_data)

    # finish the latex document
    latex_data += '''
\input{%s}''' % latex_footer_tex
    #print '*' * 70
    #print latex_data
    #print '*' * 70
    latex_file.write(latex_data.encode('utf-8'))
    latex_file.seek(0)  # rewind

    # pdflatex latex_file to pdf_file
    FNULL = open(os.devnull, 'w')  # hide output here ;-)
    #pdflatex_output =
    subprocess.call(
        [
            'pdflatex',
            '-output-directory=%s' % _tempdir,
            latex_file.name
        ],
        stdout=FNULL, stderr=subprocess.STDOUT  # hide output
    )
    #print("the output of pdflatex run: %s" % pdflatex_output)

    # debug: open the PDF in a viewer
    #subprocess.call(
    #    [
    #        'evince',
    #        pdf_file.name
    #    ],
    #    stdout=FNULL, stderr=subprocess.STDOUT  # hide output
    #)

    # return a pdf file
    response = Response(content_type='application/pdf')
    response.app_iter = open(pdf_file.name, "r")
    shutil.rmtree(_tempdir, ignore_errors=True)  # delete temporary directory
    return response
