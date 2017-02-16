# -*- coding: utf-8  -*-

from datetime import date
from pyramid import testing
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
            DBSession.add(member1)
            DBSession.add(member2)

            member1.membership_number = u'member1'
            member2.membership_number = u'member2'

            share = Shares()
            share.reference_code = u'share1'
            share.date_of_acquisition = date.today()
            member1.shares.append(share)
            share = Shares()
            share.date_of_acquisition = date.today()
            share.reference_code = u'share2'
            member1.shares.append(share)
            share = Shares()
            share.date_of_acquisition = date.today()
            share.reference_code = u'share3'
            member2.shares.append(share)
            share = Shares()
            share.date_of_acquisition = date.today()
            share.reference_code = u'share4'
            member2.shares.append(share)

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
