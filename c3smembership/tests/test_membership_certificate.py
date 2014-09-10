# -*- coding: utf-8 -*-

from datetime import (
    date,
    datetime,
    timedelta,
)
from pyramid import testing
from sqlalchemy import engine_from_config
import transaction
import unittest

from c3smembership.models import (
    C3sMember,
    DBSession,
    Base,
)
#Base = declarative_base()


def _initTestingDB():
    #from sqlalchemy import create_engine
    #from c3smembership.models import initialize_sql
    #session = initialize_sql(create_engine('sqlite:///memory'))
    #session = DBSession
    my_settings = {'sqlalchemy.url': 'sqlite:///:memory:', }
    engine = engine_from_config(my_settings)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        member1 = C3sMember(  # german
            firstname=u'SomeFirstnäme',
            lastname=u'SomeLastnäme',
            email=u'some@shri.de',
            address1=u"addr one",
            address2=u"addr two",
            postcode=u"12345",
            city=u"Footown Mäh",
            country=u"Foocountry",
            locale=u"de",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'ABCDEFGFOO',
            password=u'arandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'23',
        )
        member2 = C3sMember(  # english
            firstname=u'AAASomeFirstnäme',
            lastname=u'XXXSomeLastnäme',
            email=u'some2@shri.de',
            address1=u"addr one",
            address2=u"addr two",
            postcode=u"12345",
            city=u"Footown Mäh",
            country=u"Foocountry",
            locale=u"en",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'ABCDEFGBAR',
            password=u'arandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'2',
        )
        DBSession.add(member1)
        DBSession.add(member2)

    return DBSession


class TestMembershipCertificateViews(unittest.TestCase):
    """
    tests for the membership certificate views
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        self.config.include('pyramid_chameleon')
        DBSession.remove()
        self.session = _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_send_certificate_email_german(self):
        """
        test the send_certificate_email view (german)
        """
        from c3smembership.membership_certificate import send_certificate_email
        self.config.add_route('join', '/')
        self.config.add_route('dashboard', '/')
        self.config.add_route('certificate_pdf', '/')
        self.config.add_route('membership_listing_backend', '/')
        from pyramid_mailer import get_mailer
        request = testing.DummyRequest()
        request.matchdict = {
            'id': '1',
            'name': 'foobar',
            'token': 'hotzenplotz'  # WRONG/INVALID token
        }
        request.cookies['on_page'] = 1
        request.cookies['order'] = 'asc'
        request.cookies['orderby'] = 'id'

        mailer = get_mailer(request)
        result = send_certificate_email(request)

        #print result
        self.assertTrue(result.status_code == 404)  # not found
        self.assertEqual(len(mailer.outbox), 0)

        request.matchdict = {
            'id': '1',
            'name': 'foobar',
            'token': 'hotzenplotz123'
        }
        member1 = C3sMember.get_by_id(1)
        #member1.certificate_token = u'hotzenplotz123'
        member1.membership_accepted = True
        result = send_certificate_email(request)
        #print result
        self.assertTrue(result.status_code == 302)  # redirect

        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(
            mailer.outbox[0].subject,
            u"C3S-Mitgliedsbescheinigung"
        )
        #print mailer.outbox[0].body
        self.assertTrue(
            u"Hallo SomeFirstnäme," in mailer.outbox[0].body)
        self.assertTrue(
            u"Deine persönliche Mitgliederbescheinig" in mailer.outbox[0].body)

    def test_send_certificate_email_english(self):
        """
        test the send_certificate_email view (english)
        """
        from c3smembership.membership_certificate import send_certificate_email
        self.config.add_route('join', '/')
        self.config.add_route('dashboard', '/')
        self.config.add_route('certificate_pdf', '/')
        self.config.add_route('membership_listing_backend', '/')
        from pyramid_mailer import get_mailer
        request = testing.DummyRequest()
        request.matchdict = {
            'id': '2',
            'name': 'foobar',
            'token': 'hotzenplotz'  # WRONG/INVALID token
        }
        request.cookies['on_page'] = 1
        request.cookies['order'] = 'asc'
        request.cookies['orderby'] = 'id'

        mailer = get_mailer(request)
        result = send_certificate_email(request)

        #print result
        self.assertTrue(result.status_code == 404)  # not found
        self.assertEqual(len(mailer.outbox), 0)

        request.matchdict = {
            'id': '2',
            'name': 'foobar',
            'token': 'hotzenplotz123'
        }
        member2 = C3sMember.get_by_id(2)
        #member1.certificate_token = u'hotzenplotz123'
        member2.membership_accepted = True
        result = send_certificate_email(request)
        #print result
        self.assertTrue(result.status_code == 302)  # redirect

        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(
            mailer.outbox[0].subject,
            u"C3S membership certificate"
        )
        #print mailer.outbox[0].body
        self.assertTrue(
            u"Hello AAASomeFirstnäme," in mailer.outbox[0].body)
        self.assertTrue(
            u"your personal membership certificate" in mailer.outbox[0].body)

    def test_generate_certificate_english(self):
        """
        test the certificate download view (english)
        """
        from c3smembership.membership_certificate import generate_certificate
        request = testing.DummyRequest()
        request.matchdict = {
            'id': '2',
            'name': 'foobar',
            'token': 'hotzenplotz'
        }

        result = generate_certificate(request)

        # check: this is *not* found because the token is *invalid*
        self.assertTrue(result.status_code == 404)  # not found

        request.matchdict = {
            'id': '2',
            'name': 'foobar',
            'token': 'hotzenplotz123'
        }
        member2 = C3sMember.get_by_id(2)
        member2.certificate_token = u'hotzenplotz123'
        # now the database matches the matchdict

        member2.certificate_email_date = datetime.now(
        ) - timedelta(weeks=1)
        member2.membership_accepted = True

        result = generate_certificate(request)
        self.assertTrue(100000 < len(result.body) < 110000)
        self.assertTrue(result.content_type == 'application/pdf')

    def test_generate_certificate_german(self):
        """
        test the certificate download view (german)
        """
        from c3smembership.membership_certificate import generate_certificate
        request = testing.DummyRequest()
        request.matchdict = {
            'id': '1',
            'name': 'foobar',
            'token': 'hotzenplotz'
        }

        result = generate_certificate(request)

        self.assertTrue(result.status_code == 404)  # not found

        request.matchdict = {
            'id': '1',
            'name': 'foobar',
            'token': 'hotzenplotz123'
        }
        member = C3sMember.get_by_id(1)
        member.certificate_token = u'hotzenplotz123'
        member.membership_accepted = True


        result = generate_certificate(request)
        #print result.body
        self.assertTrue(result.status_code == 404)  # not found

        # test: email/token is too old
        member.certificate_email_date = datetime.now(
        ) - timedelta(weeks=3)
        result = generate_certificate(request)
        self.assertTrue(result.status_code == 404)  # not found
        # need to get the date right!
        member.certificate_email_date = datetime.now(
        ) - timedelta(weeks=1)
        result = generate_certificate(request)

        # print result.body
        self.assertTrue(100000 < len(result.body) < 110000)
        self.assertTrue(result.content_type == 'application/pdf')

        # edge case: member has one share
        member.certificate_token = u'hotzenplotz123'
        member.num_shares = 1

        result = generate_certificate(request)
        self.assertTrue(100000 < len(result.body) < 110000)
        self.assertTrue(result.content_type == 'application/pdf')

        # edge case: member has one share
        member.certificate_token = u'hotzenplotz123'
        member.is_legalentity = True

        result = generate_certificate(request)
        self.assertTrue(100000 < len(result.body) < 110000)
        self.assertTrue(result.content_type == 'application/pdf')
