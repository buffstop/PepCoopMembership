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


class TestReminderViews(unittest.TestCase):
    """
    very basic tests for the main views
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        self.config.registry.settings['testing.mail_to_console'] = 'false'
        DBSession.remove()
        self.session = _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_reminder_signature(self):
        """
        test the mail_signature_reminder view
        """
        from c3smembership.accountants_views import mail_signature_reminder
        self.config.add_route('join', '/')
        self.config.add_route('dashboard', '/')
        from pyramid_mailer import get_mailer
        request = testing.DummyRequest()
        request.matchdict = {'memberid': '1'}
        request.cookies['on_page'] = 1
        request.cookies['order'] = 'asc'
        request.cookies['orderby'] = 'id'

        mailer = get_mailer(request)
        result = mail_signature_reminder(request)

        self.assertTrue(result.status_code == 302)  # redirect

        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(
            mailer.outbox[0].subject,
            u"C3S: don't forget to send your form "
            u"/ Bitte Beitrittsformular einsenden"
        )

        self.assertTrue(
            u"Dear SomeFirstnäme SomeLastnäme," in mailer.outbox[0].body)
        self.assertTrue(
            u"Liebe_r SomeFirstnäme SomeLastnäme," in mailer.outbox[0].body)

    def test_reminder_payment(self):
        """
        test the mail_payment_reminder view
        """
        from c3smembership.accountants_views import mail_payment_reminder
        self.config.add_route('join', '/')
        self.config.add_route('dashboard', '/')
        from pyramid_mailer import get_mailer
        request = testing.DummyRequest()
        request.matchdict = {'memberid': '1'}
        request.cookies['on_page'] = 1
        request.cookies['order'] = 'asc'
        request.cookies['orderby'] = 'id'

        mailer = get_mailer(request)
        result = mail_payment_reminder(request)

        self.assertTrue(result.status_code == 302)  # redirect

        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(
            mailer.outbox[0].subject,
            u"C3S: don't forget to pay your shares "
            u"/ Bitte Anteile bezahlen"
        )

        self.assertTrue(
            u"Dear SomeFirstnäme SomeLastnäme," in mailer.outbox[0].body)
        self.assertTrue(
            u"Liebe_r SomeFirstnäme SomeLastnäme," in mailer.outbox[0].body)
