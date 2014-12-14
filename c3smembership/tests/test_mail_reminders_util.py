# -*- coding: utf-8 -*-

import unittest
import transaction
from sqlalchemy import engine_from_config
from pyramid import testing
from c3smembership.models import hash_password
from datetime import date
from c3smembership.mail_reminders_util import make_payment_reminder_emailbody

from c3smembership.models import (
    C3sMember,
    DBSession,
    Base,
)

class TestMailMailConfirmationViews(unittest.TestCase):

    def setUp(self):
        self.__member = C3sMember(  # german
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

    def tearDown(self):
        DBSession.close()
        DBSession.remove()
        testing.tearDown()

    def test_make_payment_reminder_emailbody(self):
        payment_reminder_body = make_payment_reminder_emailbody(self.__member)

        # make sure the payment reference code is mentioned in the German as 
        # well as in the English section of the body.

        language_divider = u'+++++++++++++++'
        language_divider_index = payment_reminder_body.find(language_divider)
        german_part = payment_reminder_body[:language_divider_index]
        english_part = payment_reminder_body[language_divider_index + len(language_divider):]

        # make sure the German part is German
        self.assertTrue(german_part.find('Liebe_r') > 0)
        self.assertTrue(german_part.find('das Team der C3S') > 0)
        self.assertTrue(english_part.find('Liebe_r') < 0)
        self.assertTrue(english_part.find('das Team der C3S') < 0)

        # make sure the English part is English
        self.assertTrue(english_part.find('Dear') > 0)
        self.assertTrue(english_part.find('All the best') > 0)
        self.assertTrue(german_part.find('Dear') < 0)
        self.assertTrue(german_part.find('All the best') < 0)

        parts = [german_part, english_part]
        for part in parts:
            payment_reference_code = u'C3Shares ' + self.__member.email_confirm_code
            occurances = 0
            index = part.find(payment_reference_code)
            while index > -1:
                occurances += 1
                index = part.find(
                    payment_reference_code,
                    index + len(payment_reference_code))

        	self.assertTrue(occurances == 1)

