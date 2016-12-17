# -*- coding: utf-8 -*-

from datetime import date
from pyramid import testing
from pyramid_mailer import get_mailer
from sqlalchemy import engine_from_config
import transaction
import unittest

from c3smembership.data.model.base import (
    DBSession,
    Base,
)
from c3smembership.models import C3sMember


def _initTestingDB():
    my_settings = {
        'sqlalchemy.url': 'sqlite:///:memory:', }
    engine = engine_from_config(my_settings)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    with transaction.manager:
        # There is a side effect of test_initialization.py after which there are
        # still records in the database although it is setup from scratch.
        # Therefore, remove all members to have an empty table.
        members = C3sMember.get_all()
        for member in members:
            DBSession.delete(member)
        DBSession.flush()

        member1 = C3sMember(  # german person
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
            email_confirm_code=u'ABCDEFG1',
            password=u'arandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=False,
            name_of_colsoc=u"",
            num_shares=u'23',
        )
        member2 = C3sMember(  # english person
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
            email_confirm_code=u'ABCDEFG2',
            password=u'arandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=False,
            name_of_colsoc=u"",
            num_shares=u'23',
        )
        member3 = C3sMember(  # german legalentity
            firstname=u'Cooles PlattenLabel',
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
            email_confirm_code=u'ABCDEFG3',
            password=u'arandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=False,
            name_of_colsoc=u"",
            num_shares=u'42',
        )
        member4 = C3sMember(  # english legalentity
            firstname=u'Incredible Records',
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
            email_confirm_code=u'ABCDEFG4',
            password=u'arandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=False,
            name_of_colsoc=u"",
            num_shares=u'2',
        )
        member1.membership_accepted = True
        DBSession.add(member1)
        member2.membership_accepted = True
        DBSession.add(member2)
        member3.membership_accepted = True
        DBSession.add(member3)
        member4.membership_accepted = True
        DBSession.add(member4)
        DBSession.flush()
    return DBSession


class TestInvitation(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        self.config.add_route('membership_listing_backend', '/')
        self.config.add_route('toolbox', '/toolbox')
        self.config.add_route('dashboard', '/dashboard')
        self.config.registry.settings['c3smembership.url'] = 'http://foo.com'
        self.config.registry.settings['ticketing.url'] = 'http://bar.com'
        self.config.registry.settings['testing.mail_to_console'] = 'false'
        self.session = _initTestingDB()

    def tearDown(self):
        DBSession.close()
        DBSession.remove()
        testing.tearDown()

    def test_invitation(self):
        """
        Test the invitation procedure for one single member at a time.

        Load this member from the DB,
        assure the email_invite_flag_bcgv16 and token are not set,
        prepare cookies, invite this member,
        assure the email_invite_flag_bcgv16 and token are now set,
        """
        from c3smembership.invite_members import invite_member_BCGV

        m1 = C3sMember.get_by_id(1)
        self.assertEqual(m1.email_invite_flag_bcgv16, False)
        self.assertTrue(m1.email_invite_token_bcgv16 is None)

        req = testing.DummyRequest()
        # have some cookies
        req.cookies['on_page'] = 0
        req.cookies['order'] = 'asc'
        req.cookies['orderby'] = 'id'

        # try with nonexistant id
        req.matchdict = {'m_id': 10000}
        res = invite_member_BCGV(req)
        self.assertEquals(302, res.status_code)

        req.matchdict = {'m_id': m1.id}
        res = invite_member_BCGV(req)

        self.assertEqual(m1.email_invite_flag_bcgv16, True)
        self.assertTrue(m1.email_invite_token_bcgv16 is not None)

        # now really send email
        self.config.registry.settings['testing.mail_to_console'] = 'false'
        mailer = get_mailer(req)
        res = invite_member_BCGV(req)

        self.assertEqual(len(mailer.outbox), 2)
        self.assertTrue(u'[C3S] Einladung zu Barcamp und Generalversammlung'
                        in mailer.outbox[0].subject)
        self.assertTrue(u'[C3S] Einladung zu Barcamp und Generalversammlung'
                        in mailer.outbox[1].subject)
        self.assertTrue(m1.firstname
                        in mailer.outbox[1].body)
        self.assertTrue(m1.email_invite_token_bcgv16
                        in mailer.outbox[1].body)

        # now send invitation to english member
        m2 = C3sMember.get_by_id(2)
        self.assertEqual(m2.email_invite_flag_bcgv16, False)
        self.assertTrue(m2.email_invite_token_bcgv16 is None)
        req.matchdict = {'m_id': m2.id}
        res = invite_member_BCGV(req)
        self.assertEqual(m2.email_invite_flag_bcgv16, True)
        self.assertTrue(m2.email_invite_token_bcgv16 is not None)
        self.assertEqual(len(mailer.outbox), 3)
        self.assertTrue(u'[C3S] Invitation to Barcamp and General Assembly'
                        in mailer.outbox[2].subject)
        self.assertTrue(m2.firstname
                        in mailer.outbox[2].body)
        self.assertTrue(m2.email_invite_token_bcgv16
                        in mailer.outbox[2].body)

    def test_invitation_batch(self):
        """
        Test the invitation procedure, batch mode.
        """
        from c3smembership.invite_members import batch_invite

        all = C3sMember.get_all()
        for m in all:
            self.assertEqual(m.email_invite_flag_bcgv16, False)
            self.assertTrue(m.email_invite_token_bcgv16 is None)
            self.assertTrue(m.membership_accepted is True)

        req = testing.DummyRequest()
        # have some cookies
        req.cookies['on_page'] = 0
        req.cookies['order'] = 'asc'
        req.cookies['orderby'] = 'id'

        # with matchdict
        req.matchdict = {'number': 1}  # this will trigger 1 invitation
        res = batch_invite(req)

        _messages = req.session.peek_flash('message_to_staff')
        # print("messages: {}".format(_messages))
        self.assertTrue(
            'sent out 1 mails (to members with ids [1]' in _messages)

        # without matchdict
        req.matchdict = {'number': ''}  # this triggers remaining 3
        res = batch_invite(req)
        self.assertEqual(res.status_code, 302)
        _messages = req.session.peek_flash('message_to_staff')
        # print("messages: {}".format(_messages))

        self.assertTrue(
            'sent out 3 mails (to members with ids [2, 3, 4]' in _messages)
        # send more request with POST['number']
        req = testing.DummyRequest(
            POST={
                'number': 'foo',
                'submit': True,
            })
        res = batch_invite(req)

        req = testing.DummyRequest(
            POST={
                'number': 1,
                'submit': True,
            })
        res = batch_invite(req)

        _messages = req.session.peek_flash('message_to_staff')
        # print("messages: {}".format(_messages))
        self.assertTrue(
            'no invitees left. all done!' in _messages)

        mailer = get_mailer(req)
        self.assertEqual(len(mailer.outbox), 4)

        # assumptions about those members and emails sent
        self.assertTrue('[C3S] Einladung' in mailer.outbox[0].subject)  # de
        self.assertTrue('[C3S] Invitation' in mailer.outbox[1].subject)  # en
        self.assertTrue('[C3S] Einladung' in mailer.outbox[2].subject)  # de
        self.assertTrue('[C3S] Invitation' in mailer.outbox[3].subject)  # en

        for m in all:
            # has been invited
            self.assertEqual(m.email_invite_flag_bcgv16, True)
            # has a token
            self.assertTrue(m.email_invite_token_bcgv16 is not None)
            # firstname and token are in email body
            self.assertTrue(
                all[m.id - 1].firstname in mailer.outbox[m.id - 1].body)
            self.assertTrue(
                all[m.id - 1].email_invite_token_bcgv16 in mailer.outbox[
                    m.id - 1].body)
