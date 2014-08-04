# -*- coding: utf-8 -*-

from datetime import date
from pyramid import testing
from sqlalchemy import engine_from_config
import transaction
import unittest
from sqlalchemy.ext.declarative import declarative_base

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
    my_settings = {
        'sqlalchemy.url': 'sqlite:///:memory:', }
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
            locale=u"DE",
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
        member2 = C3sMember(  # german
            firstname=u'AAASomeFirstnäme',
            lastname=u'XXXSomeLastnäme',
            email=u'some2@shri.de',
            address1=u"addr one",
            address2=u"addr two",
            postcode=u"12345",
            city=u"Footown Mäh",
            country=u"Foocountry",
            locale=u"DE",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'ABCDEFGBAR',
            password=u'arandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'23',
        )
        DBSession.add(member1)
        DBSession.add(member2)

    return DBSession


class TestMailMailConfirmationViews(unittest.TestCase):
    """
    tests for the mail_mail_confirmation views
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        self.config.registry.settings['c3smembership.url'] = 'http://foo.com'
        self.config.registry.settings['c3smembership.mailaddr'] = 'c@c3s.cc'
        DBSession.remove()
        self.session = _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_mail_mail_confirmation_invalid_id(self):
        """
        test the mail_mail_confirmation view
        """
        from c3smembership.administration import mail_mail_conf
        self.config.add_route('join', '/')
        self.config.add_route('dashboard', '/dashboard/0/id/asc')
        from pyramid_mailer import get_mailer
        request = testing.DummyRequest()
        request.matchdict = {'memberid': '10000'}  # invalid!
        request.cookies['on_page'] = 1
        request.cookies['order'] = 'asc'
        request.cookies['orderby'] = 'id'

        result = mail_mail_conf(request)

        self.assertTrue(result.status_code == 302)  # redirect
        self.assertTrue(  # to dashboard
            'http://example.com/dashboard/0/id/asc' in result.location)

    def test_mail_mail_confirmation(self):
        """
        test the mail_mail_confirmation view
        """
        from c3smembership.administration import mail_mail_conf
        self.config.add_route('join', '/')
        self.config.add_route('dashboard', '/')
        from pyramid_mailer import get_mailer
        request = testing.DummyRequest()
        request.matchdict = {'memberid': '1'}
        request.cookies['on_page'] = 1
        request.cookies['order'] = 'asc'
        request.cookies['orderby'] = 'id'

        mailer = get_mailer(request)
        result = mail_mail_conf(request)

        self.assertTrue(result.status_code == 302)  # redirect

        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(
            mailer.outbox[0].subject,
            u"[C3S] Please confirm your email address! "
            u"/ Bitte E-Mail-Adresse bestätigen!"
        )
        #print mailer.outbox[0].body
        self.assertTrue(
            u"Hello" in mailer.outbox[0].body)
        self.assertTrue(
            u"Hallo" in mailer.outbox[0].body)
        _m = C3sMember.get_by_id(1)
        self.assertTrue(
            u'{} {}'.format(
                _m.firstname, _m.lastname) in mailer.outbox[0].body)
        self.assertTrue(
            u"http://foo.com/vae/" in mailer.outbox[0].body)

    def test_verify_mailaddress_conf_invalid_token(self):
        """
        test the verify_mailaddress_conf view
        """
        from c3smembership.administration import verify_mailaddress_conf
        from pyramid_mailer import get_mailer
        request = testing.DummyRequest()
        request.matchdict = {
            'email': u'test@shri.de',
            'refcode': u'ABCDEFGRefCode',
            'token': u'veryloooongtoken',
        }
        request.cookies['on_page'] = 1
        request.cookies['order'] = 'asc'
        request.cookies['orderby'] = 'id'

        mailer = get_mailer(request)
        result = verify_mailaddress_conf(request)

        self.assertTrue(
            'bad URL / bad codes. '
            'please contact office@c3s.cc!' in result['result_msg'])
        self.assertTrue(result['confirmed'] is False)

    def test_verify_mailaddress_conf_valid_token(self):
        """
        test *both* the mail_mail_confirmation view
        *and* the verify_mailaddress_conf view
        """
        from c3smembership.administration import mail_mail_conf
        from c3smembership.administration import verify_mailaddress_conf
        from pyramid_mailer import get_mailer
        # prepare: send mail confirmatio email and thus have a token for her
        request1 = testing.DummyRequest()
        self.config.add_route('dashboard', '/')
        request1.matchdict = {'memberid': '1'}
        request1.cookies['on_page'] = 1
        request1.cookies['order'] = 'asc'
        request1.cookies['orderby'] = 'id'

        result1 = mail_mail_conf(request1)
        result1
        _member = C3sMember.get_by_id(1)
        _refcode = _member.email_confirm_code
        _token = _member.email_confirm_token
        _email = _member.email
        # check: try with good refcode and token, but wrong email
        request = testing.DummyRequest()
        request.matchdict = {
            'email': u'test@shri.de',
            'refcode': _refcode,
            'token': _token,
        }

        mailer = get_mailer(request)
        result = verify_mailaddress_conf(request)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertTrue(
            'bad token/email. '
            'please contact office@c3s.cc!' in result['result_msg'])
        self.assertTrue(result['confirmed'] is False)

        # check: try with good refcode and token AND good email
        request = testing.DummyRequest()
        request.matchdict = {
            'email': _email,
            'refcode': _refcode,
            'token': _token,
        }

        result = verify_mailaddress_conf(request)
        self.assertEqual(len(mailer.outbox), 2)
        self.assertTrue(
            '[C3S Yes!] afm email confirmed' in mailer.outbox[1].subject)
        self.assertTrue(
            'see http://foo.com/detail/1' in mailer.outbox[1].body)

        # another test: try again: token works only once!
        request = testing.DummyRequest()
        request.matchdict = {
            'email': _email,
            'refcode': _refcode,
            'token': _token,
        }

        result = verify_mailaddress_conf(request)
        self.assertEqual(len(mailer.outbox), 2)  # no change

        self.assertTrue(
            'your token is invalid. '
            'please contact office@c3s.cc!' in result['result_msg'])
        self.assertTrue(result['confirmed'] is False)
