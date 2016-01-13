# -*- coding: utf-8 -*-
"""
This module holds functionality to handle Membership Certificates.

- Send out email with individual links.
- Generate certificate PDFs for users.
- Generate certificate PDFs for staff.

The actual PDFs are generated using *pdflatex*.

The LaTeX templates for this have been factured out into a private repository,
because we do not want others to be able to re-create our membership
certificates and also because there are files contained
that we do not want to be public, e.g. signatures.
"""
from datetime import (
    date,
    datetime
)
import os
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.response import Response
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
import re
import shutil
import subprocess
import tempfile
from types import NoneType

from c3smembership.models import C3sMember

DEBUG = False


def make_random_token():
    """
    Generate a random token used to allow access to certificate.
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
    Send email to a member with a link
    so the member can get her membership certificate.
    '''
    # print request.referrer  # note: will fail in tests
    _special_condition = False  # for redirects to referrer

    mid = request.matchdict['id']
    member = C3sMember.get_by_id(mid)
    if isinstance(member, NoneType) or not member.membership_accepted:
        return Response(
            'that id does not exist or is not an accepted member. go back',
            status='404 Not Found',)
    # create a token for the certificate
    member.certificate_token = make_random_token()

    _url = request.route_url(
        'certificate_pdf',
        id=member.id,
        name=member.get_url_safe_name(),
        token=member.certificate_token)
    if DEBUG:  # pragma: no cover
        print '#'*60
        print member.certificate_token
        print _url
        print '#'*60

    here = os.path.dirname(__file__)
    message_body_file_name = os.path.join(
        here,  # construct path relative to *this* file
        ('templates/mail/membership_certificate_' +
         member.locale + '.txt'))
    with open(message_body_file_name, 'rb') as content_file:
        message_body = content_file.read().decode('utf-8')
        message_body = message_body.format(
            name=member.firstname,
            url=_url
        )

    mailer = get_mailer(request)
    the_message = Message(
        subject=u'C3S-Mitgliedsbescheinigung' if (
            member.locale == 'de') else u'C3S membership certificate',
        sender='office@c3s.cc',
        recipients=[member.email, ],
        body=message_body
    )
    if 'true' in request.registry.settings[
            'testing.mail_to_console']:  # pragma: no cover
        print('== 8< ======================================================')
        print(the_message.body)
        print('====================================================== >8 ==')
    else:
        mailer.send(the_message)
    member.certificate_email = True
    member.certificate_email_date = datetime.now()

    try:
        if 'detail' in request.referrer:  # pragma: no cover
            _special_condition = True
    except:
        pass

    if _special_condition:  # pragma: no cover
        return HTTPFound(
            location=request.referrer +
            '#certificate'
        )
    else:
        try:  # iff usefull cookie exists
            return HTTPFound(
                location=request.route_url(
                    'membership_listing_backend',
                    number=request.cookies['m_on_page'],
                    order=request.cookies['m_order'],
                    orderby=request.cookies['m_orderby']) +
                '#member_' + str(member.id))
        except:  # pragma: no cover  # iff no good cookie found
            return HTTPFound(
                location=request.route_url(
                    'membership_listing_backend',
                    number=0,
                    order='asc',
                    orderby='id') +
                '#member_' + str(member.id))


@view_config(permission='view',
             route_name='certificate_pdf')
def generate_certificate(request):
    '''
    Generate a membership_certificate for a member.
    '''
    mid = request.matchdict['id']
    token = request.matchdict['token']

    try:
        member = C3sMember.get_by_id(mid)

        if DEBUG:  # pragma: no cover
            print member.firstname
            print member.certificate_token
            print type(member.certificate_token)  # NoneType
            print token
            print type(token)  # unicode
        assert(member.certificate_token is not None)
        assert(str(member.certificate_token) in str(token))
        assert(str(token) in str(member.certificate_token))
        # check age of token
        from datetime import timedelta
        _2weeks = timedelta(weeks=2)
        token_date = member.certificate_email_date
        # print "token_date: {}".format(token_date)
        present = datetime.now()
        _delta = present - token_date
        # if (_delta > _2weeks):
        #    print "more than two weeks!"
        # else:
        #    print "less than two weeks!"
        assert(_delta < _2weeks)
    except:
        return Response(
            'Not found. Please contact office@c3s.cc. <br /><br /> '
            'Nicht gefunden. Bitte office@c3s.cc kontaktieren.',
            status='404 Not Found',
        )
    return gen_cert(member)


@view_config(permission='manage',
             route_name='certificate_pdf_staff')
def generate_certificate_staff(request):
    '''
    Generate a membership_certificate for staffers.
    '''
    mid = request.matchdict['id']

    try:
        member = C3sMember.get_by_id(mid)
        assert(not isinstance(member, NoneType))
    except:
        return Response(
            'Not found. Please check URL.',
        )
    return gen_cert(member)


def gen_cert(member):
    '''
    Utility function: create a membership certificate PDF file using pdflatex
    '''
    here = os.path.dirname(__file__)

    # print '#'*60
    # print member.locale
    # print '#'*60

    if 'de' in member.locale:
        latex_background_image = os.path.abspath(
            os.path.join(here, '../certificate/Urkunde_Hintergrund_blank.pdf'))
        # latex header and footer
        latex_header_tex = os.path.abspath(
            os.path.join(here, '../certificate/urkunde_header_de.tex'))
        # print("latex header file: %s" % latex_header_tex)
        latex_footer_tex = os.path.abspath(
            os.path.join(here, '../certificate/urkunde_footer_de.tex'))
        # print("latex footer file: %s" % latex_footer_tex)
    else:
        latex_background_image = os.path.abspath(
            os.path.join(here, '../certificate/Urkunde_Hintergrund_blank.pdf'))
        # latex header and footer
        latex_header_tex = os.path.abspath(
            os.path.join(here, '../certificate/urkunde_header_en.tex'))
        # print("latex header file: %s" % latex_header_tex)
        latex_footer_tex = os.path.abspath(
            os.path.join(here, '../certificate/urkunde_footer_en.tex'))
        # print("latex footer file: %s" % latex_footer_tex)

    sign_meik = os.path.abspath(
        os.path.join(here, '../certificate/sign_meik.png'))
    sign_max = os.path.abspath(
        os.path.join(here, '../certificate/sign_max.png'))

    # a temporary directory for the latex run
    _tempdir = tempfile.mkdtemp()
    # print("new temporary directory: %s" % _tempdir)

    latex_file = tempfile.NamedTemporaryFile(
        suffix='.tex',
        dir=_tempdir,
        delete=False,  # directory will be deleted anyways
    )
    # print "the latex file: {}".format(latex_file.name)

    # using tempfile
    pdf_file = tempfile.NamedTemporaryFile(
        dir=_tempdir,
        delete=False,  # directory will be deleted anyways
    )
    pdf_file.name = latex_file.name.rstrip('.tex')  # + '.pdf'
    pdf_file.name += '.pdf'

    is_founder = True if 'dungHH_' in member.email_confirm_code else False
    # print u"email confirm code: {}".format(member.email_confirm_code)
    # print u"is a founding member? {}".format(
    #    True if 'dungHH_' in member.email_confirm_code else False)
    # prepare the certificate text
    if member.locale == 'de':  # german
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
                datetime.strftime(member.membership_date, '%d.%m.%Y'))
        mship_num = u'Die Mitgliedsnummer lautet {}.'.format(
            member.membership_number
        )
        mship_num_text = u'Mitgliedsnummer {}'.format(
            member.membership_number
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
                datetime.strftime(member.membership_date, '%Y-%m-%d'))
        mship_num = u'The membership number is {}.'.format(
            member.membership_number
        )
        mship_num_text = u'membership number {}'.format(
            member.membership_number
        )
        exec_dir = 'Executive Director'

    # construct latex_file
    latex_data = '''
\\input{%s}
\\def\\backgroundImage{%s}
\\def\\txtBlkHerebyConfirmed{%s}
\\def\\firstName{%s}
\\def\\lastName{%s}
\\def\\addressOne{%s}
\\def\\postCode{%s}
\\def\\city{%s}
\\def\\numShares{%s}
\\def\\numAddShares{%s}
\\def\\txtBlkIsMember{%s}
\\def\\txtBlkMembershipNumber{%s}
\\def\\txtBlkConfirmDate{%s}
\\def\\signDate{%s}
\\def\\signMeik{%s}
\\def\\signMax{%s}
\\def\\txtBlkCEO{%s}
\\def\\txtBlkMembershipNum{%s}
    ''' % (
        latex_header_tex,
        latex_background_image,
        hereby_confirmed,
        member.firstname,
        member.lastname,
        member.address1,
        member.postcode,
        member.city,
        member.num_shares,
        member.num_shares-1,
        is_member,
        mship_num,
        confirm_date,
        datetime.strftime(
            date.today(), "%d.%m.%Y") \
                if member.locale == 'de' \
                else date.today(),
        sign_meik,
        sign_max,
        exec_dir,
        mship_num_text
    )
    if DEBUG:  # pragma: no cover
        print('#'*60)
        print(member.is_legalentity)
        print(member.lastname)
        print('#'*60)
    if member.is_legalentity:
        latex_data += '\n\\def\\company{%s}' % member.lastname
    if member.address2 is not u'':  # add address part 2 iff exists
        latex_data += '\n\\def\\addressTwo{%s}' % member.address2
    if member.num_shares > 1:  # how many shares?
        if member.num_shares == 2:  # iff member has exactely two shares...
            latex_data += '\n\\def\\txtBlkAddShares{%s.}' % one_more_share
        if member.num_shares > 2:  # iff more than two
            latex_data += '\n\\def\\txtBlkAddShares{%s %s %s.}' % (
                and_block,
                member.num_shares-1,
                several_shares
            )
    else:  # iff member has exactely one share..
        latex_data += '\n\\def\\txtBlkAddShares{.}'

    # escape some characters to appease LaTeX
    latex_data = re.sub('&', '\\&', latex_data)
    latex_data = re.sub('#', '\\#', latex_data)

    # finish the latex document
    latex_data += '\n\\input{%s}' % latex_footer_tex

    # DEBUG = True
    if DEBUG:  # pragma: no cover
        print '*' * 70
        print('*' * 30, 'latex data: ', '*' * 30)
        print '*' * 70
        print latex_data
        print '*' * 70
    latex_file.write(latex_data.encode('utf-8'))
    latex_file.seek(0)  # rewind

    # pdflatex latex_file to pdf_file
    fnull = open(os.devnull, 'w')  # hide output here ;-)
    # pdflatex_output =
    subprocess.call(
        [
            'pdflatex',
            '-output-directory=%s' % _tempdir,
            latex_file.name
        ],
        stdout=fnull, stderr=subprocess.STDOUT  # hide output
    )
    # print("the output of pdflatex run: %s" % pdflatex_output)

    # debug: open the PDF in a viewer
    # subprocess.call(
    #    [
    #        'evince',
    #        pdf_file.name
    #    ],
    #    stdout=fnull, stderr=subprocess.STDOUT  # hide output
    # )

    # return a pdf file
    response = Response(content_type='application/pdf')
    response.app_iter = open(pdf_file.name, "r")
    shutil.rmtree(_tempdir, ignore_errors=True)  # delete temporary directory
    return response
