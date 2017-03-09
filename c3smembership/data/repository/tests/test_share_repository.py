# -*- coding: utf-8  -*-

from datetime import date

from sqlalchemy import engine_from_config
import transaction
import unittest

from c3smembership.data.model.base import (
    DBSession,
    Base,
)
from c3smembership.models import (
    C3sMember,
    Shares,
)
from c3smembership.data.repository.share_repository import ShareRepository


class TestShareRepository(unittest.TestCase):

    def setUp(self):
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
            member3 = C3sMember(
                firstname=u'Not Approved',
                lastname=u'Member',
                email=u'not.approved@example.com',
                address1=u'Some Street 123',
                address2=u'',
                postcode=u"12345",
                city=u"Some City",
                country=u"Some Country",
                locale=u"DE",
                date_of_birth=date(1980, 1, 2),
                email_is_confirmed=False,
                email_confirm_code=u'NOT_APPROVED_MEMBER',
                password=u'not_approved_member',
                date_of_submission=date(1970, 1, 1),
                membership_type=u'normal',
                member_of_colsoc=True,
                name_of_colsoc=u'',
                num_shares=u'7',
            )
            DBSession.add(member1)
            DBSession.add(member2)
            DBSession.add(member3)

            member1.membership_number = u'member1'
            member2.membership_number = u'member2'
            member3.payment_received_date = date(2016, 10, 11)

            share = Shares()
            share.reference_code = u'share1'
            share.date_of_acquisition = date(2013, 1, 2)
            share.payment_received_date = date(2012, 11, 10)
            share.number = 12
            member1.shares.append(share)

            share = Shares()
            share.reference_code = u'share2'
            share.date_of_acquisition = date(2014, 2, 3)
            share.payment_received_date = date(2012, 12, 31)
            share.number = 23
            member1.shares.append(share)

            share = Shares()
            share.reference_code = u'share3'
            share.date_of_acquisition = date(2014, 3, 4)
            share.payment_received_date = date(2014, 3, 3)
            share.number = 34
            member2.shares.append(share)

            share = Shares()
            share.reference_code = u'share4'
            share.date_of_acquisition = date(2015, 4, 5)
            share.payment_received_date = date(2014, 11, 15)
            share.number = 45
            member2.shares.append(share)

    def tearDown(self):
        DBSession.close()
        DBSession.remove()

    def test_create(self):
        """
        Tests the ShareRepository.create method.
        """
        # pylint: disable=no-member
        member1 = DBSession.query(C3sMember).filter(
            C3sMember.membership_number == 'member1').first()
        self.assertEqual(member1.num_shares, 12 + 23)

        share_id = ShareRepository.create('member1', 25, date(2016, 4, 23))
        self.assertEqual(member1.num_shares, 12 + 23 + 25)
        self.assertEqual(len(member1.shares), 3)

        # pylint: disable=no-member
        shares = DBSession.query(Shares).filter(Shares.id == share_id).first()
        self.assertEqual(shares.number, 25)
        self.assertEqual(shares.date_of_acquisition, date(2016, 4, 23))
        self.assertEqual(shares.reference_code, None)
        self.assertEqual(shares.signature_received, False)
        self.assertEqual(shares.signature_received_date, date(1970, 1, 1))
        self.assertEqual(shares.signature_confirmed, False)
        self.assertEqual(shares.signature_confirmed_date, date(1970, 1, 1))
        self.assertEqual(shares.payment_received, False)
        self.assertEqual(shares.payment_received_date, date(1970, 1, 1))
        self.assertEqual(shares.payment_confirmed, False)
        self.assertEqual(shares.payment_confirmed_date, date(1970, 1, 1))
        self.assertEqual(shares.accountant_comment, None)

    def test_get_member_shares(self):
        shares = ShareRepository.get_member_shares('member1')
        self.assertEqual(len(shares), 2)
        reference_codes = []
        for share in shares:
            reference_codes.append(share.reference_code)
        self.assertTrue('share1' in reference_codes)
        self.assertTrue('share2' in reference_codes)

        shares = ShareRepository.get_member_shares('member2')
        self.assertEqual(len(shares), 2)
        for share in shares:
            reference_codes.append(share.reference_code)
        self.assertTrue('share3' in reference_codes)
        self.assertTrue('share4' in reference_codes)

    def test_get_approved(self):
        share_processes = ShareRepository.get_approved(
            date(2013, 1, 1),
            date(2013, 12, 31))
        self.assertEqual(len(share_processes), 1)
        self.assertEqual(share_processes[0].reference_code, 'share1')

        share_processes = ShareRepository.get_approved(
            date(2013, 1, 2),
            date(2013, 12, 31))
        self.assertEqual(len(share_processes), 1)
        self.assertEqual(share_processes[0].reference_code, 'share1')

        share_processes = ShareRepository.get_approved(
            date(2013, 1, 3),
            date(2013, 12, 31))
        self.assertEqual(len(share_processes), 0)

        share_processes = ShareRepository.get_approved(
            date(2013, 1, 1),
            date(2014, 2, 2))
        self.assertEqual(len(share_processes), 1)
        self.assertEqual(share_processes[0].reference_code, 'share1')

        share_processes = ShareRepository.get_approved(
            date(2013, 1, 1),
            date(2014, 2, 3))
        self.assertEqual(len(share_processes), 2)
        reference_codes = []
        for share_process in share_processes:
            reference_codes.append(share_process.reference_code)
        self.assertTrue('share1' in reference_codes)
        self.assertTrue('share2' in reference_codes)

        share_processes = ShareRepository.get_approved(
            date(2013, 1, 1),
            date(2014, 12, 31))
        self.assertEqual(len(share_processes), 3)
        reference_codes = []
        for share_process in share_processes:
            reference_codes.append(share_process.reference_code)
        self.assertTrue('share1' in reference_codes)
        self.assertTrue('share2' in reference_codes)
        self.assertTrue('share3' in reference_codes)

        share_processes = ShareRepository.get_approved(
            date(2013, 1, 1),
            date(2015, 12, 31))
        self.assertEqual(len(share_processes), 4)
        reference_codes = []
        for share_process in share_processes:
            reference_codes.append(share_process.reference_code)
        self.assertTrue('share1' in reference_codes)
        self.assertTrue('share2' in reference_codes)
        self.assertTrue('share3' in reference_codes)
        self.assertTrue('share4' in reference_codes)

        share_processes = ShareRepository.get_approved(
            date(2013, 1, 3),
            date(2015, 12, 31))
        self.assertEqual(len(share_processes), 3)
        reference_codes = []
        for share_process in share_processes:
            reference_codes.append(share_process.reference_code)
        self.assertTrue('share2' in reference_codes)
        self.assertTrue('share3' in reference_codes)
        self.assertTrue('share4' in reference_codes)

    def test_get_approved_count(self):
        count = ShareRepository.get_approved_count(
            date(2013, 1, 1),
            date(2013, 12, 31))
        self.assertEqual(count, 12)

        count = ShareRepository.get_approved_count(
            date(2013, 1, 2),
            date(2013, 12, 31))
        self.assertEqual(count, 12)

        count = ShareRepository.get_approved_count(
            date(2013, 1, 3),
            date(2013, 12, 31))
        self.assertEqual(count, 0)

        count = ShareRepository.get_approved_count(
            date(2013, 1, 1),
            date(2014, 2, 2))
        self.assertEqual(count, 12)

        count = ShareRepository.get_approved_count(
            date(2013, 1, 1),
            date(2014, 2, 3))
        self.assertEqual(count, 12+23)

        count = ShareRepository.get_approved_count(
            date(2013, 1, 1),
            date(2014, 12, 31))
        self.assertEqual(count, 12+23+34)

        count = ShareRepository.get_approved_count(
            date(2013, 1, 1),
            date(2015, 12, 31))
        self.assertEqual(count, 12+23+34+45)

        count = ShareRepository.get_approved_count(
            date(2013, 1, 3),
            date(2015, 12, 31))
        self.assertEqual(count, 23+34+45)

    def test_get_paid_not_approved(self):
        share_processes = ShareRepository.get_paid_not_approved(
            date(2012, 1, 1),
            date(2012, 11, 10))
        self.assertEqual(len(share_processes), 1)
        self.assertEqual(share_processes[0].shares_count, 12)

        share_processes = ShareRepository.get_paid_not_approved(
            date(2012, 11, 10),
            date(2012, 11, 30))
        self.assertEqual(len(share_processes), 1)
        self.assertEqual(share_processes[0].shares_count, 12)

        share_processes = ShareRepository.get_paid_not_approved(
            date(2012, 11, 11),
            date(2012, 11, 30))
        self.assertEqual(len(share_processes), 0)

        share_processes = ShareRepository.get_paid_not_approved(
            date(2012, 1, 1),
            date(2012, 11, 10))
        self.assertEqual(len(share_processes), 1)
        self.assertEqual(share_processes[0].shares_count, 12)

        share_processes = ShareRepository.get_paid_not_approved(
            date(2012, 1, 1),
            date(2012, 12, 31))
        self.assertEqual(len(share_processes), 2)
        shares_counts = []
        for share_process in share_processes:
            shares_counts.append(share_process.shares_count)
        self.assertTrue(12 in shares_counts)
        self.assertTrue(23 in shares_counts)

        share_processes = ShareRepository.get_paid_not_approved(
            date(2014, 1, 1),
            date(2014, 3, 3))
        self.assertEqual(len(share_processes), 1)
        self.assertEqual(share_processes[0].shares_count, 34)

        share_processes = ShareRepository.get_paid_not_approved(
            date(2014, 1, 1),
            date(2014, 12, 31))
        self.assertEqual(len(share_processes), 1)
        self.assertEqual(share_processes[0].shares_count, 45)

        share_processes = ShareRepository.get_paid_not_approved(
            date(2016, 1, 1),
            date(2016, 12, 31))
        self.assertEqual(len(share_processes), 1)
        self.assertEqual(share_processes[0].shares_count, 7)

    def test_get_paid_not_approved_count(self):
        count = ShareRepository.get_paid_not_approved_count(
            date(2012, 1, 1),
            date(2012, 11, 10))
        self.assertEqual(count, 12)

        count = ShareRepository.get_paid_not_approved_count(
            date(2012, 11, 10),
            date(2012, 11, 30))
        self.assertEqual(count, 12)

        count = ShareRepository.get_paid_not_approved_count(
            date(2012, 11, 11),
            date(2012, 11, 30))
        self.assertEqual(count, 0)

        count = ShareRepository.get_paid_not_approved_count(
            date(2012, 1, 1),
            date(2012, 11, 10))
        self.assertEqual(count, 12)

        count = ShareRepository.get_paid_not_approved_count(
            date(2012, 1, 1),
            date(2012, 12, 31))
        self.assertEqual(count, 12+23)

        count = ShareRepository.get_paid_not_approved_count(
            date(2014, 1, 1),
            date(2014, 3, 3))
        self.assertEqual(count, 34)

        count = ShareRepository.get_paid_not_approved_count(
            date(2014, 1, 1),
            date(2014, 12, 31))
        self.assertEqual(count, 45)

        count = ShareRepository.get_paid_not_approved_count(
            date(2016, 1, 1),
            date(2016, 12, 31))
        self.assertEqual(count, 7)
