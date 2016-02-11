# -*- coding: utf-8 -*-

import unittest
from pyramid import testing
from datetime import date
from c3smembership.mail_reminders_util import make_payment_reminder_email

from c3smembership.models import (
    C3sMember,
    DBSession,
)


class TestMailMailConfirmationViews(unittest.TestCase):
    """
    Test the emails that are sent to confirm email addresses.
    """
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
        """
        test creation of email bodies for both english and german versions
        """
        payment_reference_code = u'C3Shares ABCDEFGFOO'

        # test English
        self.__member.locale = 'en'
        email_subject, email_body = make_payment_reminder_email(self.__member)

        # make sure the English part is English
        self.assertTrue('Dear' in email_body)
        self.assertTrue('All the best' in email_body)
        self.assertTrue(payment_reference_code in email_body)

        # test German
        self.__member.locale = 'de'
        email_subject, email_body = make_payment_reminder_email(self.__member)

        # make sure the German part is German
        self.assertTrue('Liebe_r' in email_body)
        self.assertTrue('Das Team der C3S' in email_body)
        self.assertTrue(payment_reference_code in email_body)
