# -*- coding: utf-8  -*-
# import os
from datetime import(
    date,
    datetime,
    timedelta,
)
from decimal import Decimal as D
from decimal import InvalidOperation
from pyramid import testing
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import transaction
import unittest

from c3smembership.data.model.base import (
    Base,
    DBSession,
)
from c3smembership.models import (
    C3sMember,
    C3sStaff,
    Dues15Invoice,
    Dues16Invoice,
    Dues17Invoice,
    Group,
    Shares,
)

DEBUG = False


class C3sMembershipModelTestBase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
            # print("removing old DBSession ==============================")
        except:
            # print("no DBSession to remove ==============================")
            pass
        # engine = create_engine('sqlite:///test_models.db')
        engine = create_engine('sqlite:///:memory:')
        self.session = DBSession
        DBSession.configure(bind=engine)  # XXX does influence self.session!?!
        Base.metadata.create_all(engine)

    def tearDown(self):
        self.session.close()
        self.session.remove()
        # os.remove('test_models.db')

    def _getTargetClass(self):
        return C3sMember

    def _makeOne(self,
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
                 email_confirm_code=u'ABCDEFGHIK',
                 password=u'arandompassword',
                 date_of_submission=date.today(),
                 membership_type=u'normal',
                 member_of_colsoc=True,
                 name_of_colsoc=u"GEMA",
                 num_shares=u'23',
                 ):
        # print "type(self.session): " + str(type(self.session))
        return self._getTargetClass()(  # order of params DOES matter
            firstname, lastname, email,
            password,
            address1, address2, postcode,
            city, country, locale,
            date_of_birth, email_is_confirmed, email_confirm_code,
            num_shares,
            date_of_submission,
            membership_type,
            member_of_colsoc, name_of_colsoc,
        )

    def _makeAnotherOne(self,
                        firstname=u'SomeFirstname',
                        lastname=u'SomeLastname',
                        email=u'some@shri.de',
                        address1=u"addr one",
                        address2=u"addr two",
                        postcode=u"12345",
                        city=u"Footown Muh",
                        country=u"Foocountry",
                        locale=u"DE",
                        date_of_birth=date.today(),
                        email_is_confirmed=False,
                        email_confirm_code=u'0987654321',
                        password=u'arandompassword',
                        date_of_submission=date.today(),
                        membership_type=u'investing',
                        member_of_colsoc=False,
                        name_of_colsoc=u"deletethis",
                        num_shares=u'23',
                        ):
        return self._getTargetClass()(  # order of params DOES matter
            firstname, lastname, email,
            password,
            address1, address2, postcode,
            city, country, locale,
            date_of_birth, email_is_confirmed, email_confirm_code,
            num_shares,
            date_of_submission,
            membership_type, member_of_colsoc, name_of_colsoc,
        )


class C3sMembershipModelTests(C3sMembershipModelTestBase):

    def setUp(self):
        """
        prepare for tests: have one member in the database
        """
        super(C3sMembershipModelTests, self).setUp()
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
            DBSession.add(member1)
            DBSession.flush()

    def test_constructor(self):
        instance = self._makeOne()
        # print(instance.address1)
        self.assertEqual(instance.firstname, u'SomeFirstnäme', "No match!")
        self.assertEqual(instance.lastname, u'SomeLastnäme', "No match!")
        self.assertEqual(instance.email, u'some@shri.de', "No match!")
        self.assertEqual(instance.address1, u'addr one', "No match!")
        self.assertEqual(instance.address2, u'addr two', "No match!")
        self.assertEqual(instance.email, u'some@shri.de', "No match!")
        self.assertEqual(
            instance.email_confirm_code, u'ABCDEFGHIK', "No match!")
        self.assertEqual(instance.email_is_confirmed, False, "expected False")
        self.assertEqual(instance.membership_type, u'normal', "No match!")

    def test_get_password(self):
        """
        Test the _get_password function.
        """
        instance = self._makeOne()
        res = instance._get_password()
        self.assertEqual(res, instance._password)

    def test_get_number(self):
        """
        test: get the number of entries in the database
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        number_from_DB = myMembershipSigneeClass.get_number()
        # print number_from_DB
        self.assertEqual(number_from_DB, 2)

    # GET BY .. tests # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def test_get_by_code(self):
        """
        test: get one entry by code
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_code(u'ABCDEFGHIK')
        if DEBUG:
            print "myMembershipSigneeClass: " + str(myMembershipSigneeClass)
            #        print "str(myUserClass.get_by_username('SomeUsername')): "
            # + str(myUserClass.get_by_username('SomeUsername'))
            #        foo = myUserClass.get_by_username(instance.username)
            #        print "test_get_by_username: type(foo): " + str(type(foo))
        self.assertEqual(instance.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.email, u'some@shri.de')

    def test_get_by_bcgvtoken(self):
        """
        test: get one entry by bcgv17 token
        """
        instance = self._makeOne()
        self.session.add(instance)
        instance.email_invite_token_bcgv17 = u'SHINY_TOKEN'
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_bcgvtoken(
            u'SHINY_TOKEN')
        self.assertEqual(instance_from_DB.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.email, u'some@shri.de')
        self.assertEqual(
            instance_from_DB.email_invite_token_bcgv17, u'SHINY_TOKEN')

    def test_get_by_dues15_token(self):
        """
        test: get one entry by token
        """
        instance = self._makeOne()
        self.session.add(instance)
        instance.dues15_token = u'THIS_ONE'
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_dues15_token(
            u'THIS_ONE')
        self.assertEqual(instance_from_DB.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.email, u'some@shri.de')

    def test_get_by_dues16_token(self):
        """
        test: get one entry by token
        """
        instance = self._makeOne()
        self.session.add(instance)
        instance.dues16_token = u'F73sjf29g4eEf9giJ'
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_dues16_token(
            u'F73sjf29g4eEf9giJ')
        self.assertEqual(instance_from_DB.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.email, u'some@shri.de')

    def test_get_by_dues17_token(self):
        """
        test: get one entry by token
        """
        instance = self._makeOne()
        self.session.add(instance)
        instance.dues17_token = u'aa84f59a8fjf79oa83kd'
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_dues17_token(
            u'aa84f59a8fjf79oa83kd')
        self.assertEqual(instance_from_DB.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.email, u'some@shri.de')

    def test_get_by_email(self):
        """
        test: get one entry by email
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        list_from_DB = myMembershipSigneeClass.get_by_email(
            u'some@shri.de')
        self.assertEqual(list_from_DB[0].firstname, u'SomeFirstnäme')
        self.assertEqual(list_from_DB[0].email, u'some@shri.de')

    def test_get_by_id(self):
        """
        test: get one entry by id
        """
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush()
        _id = instance.id
        _date_of_birth = instance.date_of_birth
        _date_of_submission = instance.date_of_submission
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_id(_id)
        if DEBUG:
            print "myMembershipSigneeClass: " + str(myMembershipSigneeClass)
            #        print "str(myUserClass.get_by_username('SomeUsername')): "
            # + str(myUserClass.get_by_username('SomeUsername'))
            #        foo = myUserClass.get_by_username(instance.username)
            #        print "test_get_by_username: type(foo): " + str(type(foo))
        self.assertEqual(instance_from_DB.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.lastname, u'SomeLastnäme')
        self.assertEqual(instance_from_DB.email, u'some@shri.de')
        self.assertEqual(instance_from_DB.address1, u'addr one')
        self.assertEqual(instance_from_DB.address2, u'addr two')
        self.assertEqual(instance_from_DB.postcode, u'12345')
        self.assertEqual(instance_from_DB.city, u'Footown Mäh')
        self.assertEqual(instance_from_DB.country, u'Foocountry')
        self.assertEqual(instance_from_DB.locale, u'DE')
        self.assertEqual(instance_from_DB.date_of_birth, _date_of_birth)
        self.assertEqual(instance_from_DB.email_is_confirmed, False)
        self.assertEqual(instance_from_DB.email_confirm_code, u'ABCDEFGHIK')
        self.assertEqual(instance_from_DB.date_of_submission,
                         _date_of_submission)
        self.assertEqual(instance_from_DB.membership_type, u'normal')
        self.assertEqual(instance_from_DB.member_of_colsoc, True)
        self.assertEqual(instance_from_DB.name_of_colsoc, u'GEMA')
        self.assertEqual(instance_from_DB.num_shares, u'23')

    def test_get_all(self):
        """
        test: get all entries
        """
        instance = self._makeOne()
        instance2 = self._makeAnotherOne()
        self.session.add(instance, instance2)
        self.session.flush()
        myMembershipSigneeClass = self._getTargetClass()
        all = myMembershipSigneeClass.get_all()
        self.assertEquals(len(all), 2)

    def test_get_dues15_invoicees(self):
        """
        test: get all members that haven't had their invoices sent
        """
        instance = self._makeOne()
        instance2 = self._makeAnotherOne()
        self.session.add(instance, instance2)
        self.session.flush()
        myMembershipSigneeClass = self._getTargetClass()
        invoicees = myMembershipSigneeClass.get_dues15_invoicees(27)
        self.assertEquals(len(invoicees), 0)
        # change details so they be found
        instance.membership_accepted = True
        instance2.membership_accepted = True
        invoicees = myMembershipSigneeClass.get_dues15_invoicees(27)
        self.assertEquals(len(invoicees), 1)

    def test_get_dues16_invoicees(self):
        """
        test: get all members that haven't had their invoices sent
        """
        instance = self._makeOne()
        instance2 = self._makeAnotherOne()
        self.session.add(instance, instance2)
        self.session.flush()
        myMembershipSigneeClass = self._getTargetClass()
        invoicees = myMembershipSigneeClass.get_dues16_invoicees(27)
        self.assertEquals(len(invoicees), 0)
        # change details so they be found
        instance.membership_accepted = True
        instance2.membership_accepted = True
        invoicees = myMembershipSigneeClass.get_dues16_invoicees(27)
        self.assertEquals(len(invoicees), 1)

    def test_get_dues17_invoicees(self):
        """
        test: get all members that haven't had their invoices sent
        """
        instance = self._makeOne()
        instance2 = self._makeAnotherOne()
        self.session.add(instance)
        self.session.add(instance2)
        self.session.flush()
        myMembershipSigneeClass = self._getTargetClass()

        instance.membership_accepted = False
        instance.membership_date = None
        instance2.membership_accepted = False
        instance2.membership_date = None
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 0)

        # change details so they be found
        instance.membership_accepted = True
        instance.membership_date = date(2016, 12, 1)
        instance2.membership_accepted = False
        instance2.membership_date = None
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 1)

        instance.membership_accepted = True
        instance.membership_date = date(2016, 12, 1)
        instance2.membership_accepted = True
        instance2.membership_date = date(2016, 12, 2)
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 2)

        # test boundary cases for membership date with one instance
        self.session.delete(instance2)
        self.session.flush()
        instance.membership_date = date(2017, 1, 1)
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 1)

        instance.membership_date = date(2017, 12, 31)
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 1)

        instance.membership_date = date(2016, 12, 31)
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 1)

        instance.membership_date = date(2018, 1, 1)
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 0)

        # test membership loss
        instance.membership_date = date(2016, 2, 3)

        instance.membership_loss_date = None
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 1)

        instance.membership_loss_date = date(2018, 1, 1)
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 1)

        instance.membership_loss_date = date(2017, 12, 31)
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 1)

        instance.membership_loss_date = date(2017, 1, 1)
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 1)

        instance.membership_loss_date = date(2016, 12, 31)
        invoicees = myMembershipSigneeClass.get_dues17_invoicees(27)
        self.assertEquals(len(invoicees), 0)

    def test_delete_by_id(self):
        """
        test: delete one entry by id
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_id('1')
        del_instance_from_DB = myMembershipSigneeClass.delete_by_id('1')
        del_instance_from_DB
        instance_from_DB = myMembershipSigneeClass.get_by_id('1')
        self.assertEqual(None, instance_from_DB)

    def test_check_user_or_none(self):
        """
        XXX TODO
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        # get first dataset (id = 1)
        result1 = myMembershipSigneeClass.check_user_or_none('1')
        self.assertEqual(1, result1.id)
        # get invalid dataset
        result2 = myMembershipSigneeClass.check_user_or_none('1234567')
        self.assertEqual(None, result2)

    def test_check_for_existing_confirm_code(self):
        """
        XXX TODO
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()

        result1 = myMembershipSigneeClass.check_for_existing_confirm_code(
            u'ABCDEFGHIK')
        self.assertEqual(result1, True)
        result2 = myMembershipSigneeClass.check_for_existing_confirm_code(
            u'ABCDEFGHIK0000000000')
        self.assertEqual(result2, False)

    def test_member_listing(self):
        """
        Test the member_listing classmethod in models.py
        """
        instance = self._makeOne()
        self.session.add(instance)
        instance2 = self._makeAnotherOne()
        self.session.add(instance2)
        myMembershipSigneeClass = self._getTargetClass()

        result1 = myMembershipSigneeClass.member_listing("id")
        self.failUnless(result1[0].firstname == u"SomeFirstnäme")
        self.failUnless(result1[1].firstname == u"SomeFirstnäme")
        self.failUnless(result1[2].firstname == u"SomeFirstname")
        self.assertEqual(len(result1.all()), 3)

    def test_member_listing_exception(self):
        """
        XXX TODO
        """
        instance = self._makeOne()
        self.session.add(instance)
        instance2 = self._makeAnotherOne()
        self.session.add(instance2)
        myMembershipSigneeClass = self._getTargetClass()

        # self.assertRaises(myMembershipSigneeClass, member_listing, "foo")
        with self.assertRaises(Exception):
            result1 = myMembershipSigneeClass.member_listing("foo")
            if DEBUG:
                print result1
        # self.failUnless(result1[0].firstname == u"SomeFirstnäme")
        # self.failUnless(result1[1].firstname == u"SomeFirstnäme")
        # self.failUnless(result1[2].firstname == u"SomeFirstname")

    def test_nonmember_listing(self):
        """
        Test the nonmember_listing classmethod in models.py
        """
        instance = self._makeOne()
        self.session.add(instance)
        instance2 = self._makeAnotherOne()
        self.session.add(instance2)
        myMembershipSigneeClass = self._getTargetClass()

        # try order_by with faulty expression -- must raise
        with self.assertRaises(Exception):
            result1 = myMembershipSigneeClass.nonmember_listing(
                0, 100, 'schmoo')
        # try order with faulty expression -- must raise
        with self.assertRaises(Exception):
            result1 = myMembershipSigneeClass.nonmember_listing(
                0, 100, 'id', 'schmoo')
        result1 = myMembershipSigneeClass.nonmember_listing(
            0, 100, 'id')
        self.failUnless(result1[0].firstname == u'SomeFirstnäme')
        self.failUnless(result1[1].firstname == u'SomeFirstnäme')
        self.failUnless(result1[2].firstname == u'SomeFirstname')
        for r in result1:
            self.assertTrue(not r.membership_accepted)
        result2 = myMembershipSigneeClass.nonmember_listing(
            0, 100, 'id', 'desc')
        self.failUnless(result2[0].firstname == u'SomeFirstname')
        self.failUnless(result2[1].firstname == u'SomeFirstnäme')
        self.failUnless(result2[2].firstname == u'SomeFirstnäme')
        for r in result2:
            self.assertTrue(not r.membership_accepted)

    def test_nonmember_listing_count(self):
        """
        Test the nonmember_listing_count classmethod in models.py
        """
        instance = self._makeOne()
        self.session.add(instance)
        instance2 = self._makeAnotherOne()
        self.session.add(instance2)
        myMembershipSigneeClass = self._getTargetClass()

        # try order_by with faulty expression -- must raise
        with self.assertRaises(Exception):
            result1 = myMembershipSigneeClass.nonmember_listing(
                "schmoo", 100)
        # try order with faulty expression -- must raise
        with self.assertRaises(Exception):
            result1 = myMembershipSigneeClass.nonmember_listing(
                0, 100, 'id', 'schmoo')
        result1 = myMembershipSigneeClass.nonmember_listing(
            0, 100, 'id')
        self.failUnless(result1[0].firstname == u'SomeFirstnäme')
        self.failUnless(result1[1].firstname == u'SomeFirstnäme')
        self.failUnless(result1[2].firstname == u'SomeFirstname')
        result2 = myMembershipSigneeClass.nonmember_listing(
            0, 100, 'id', 'desc')
        self.failUnless(result2[0].firstname == u'SomeFirstname')
        self.failUnless(result2[1].firstname == u'SomeFirstnäme')
        self.failUnless(result2[2].firstname == u'SomeFirstnäme')

    def test_get_num_members_accepted(self):
        """
        test: get the number of accepted member entries in the database
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        number_from_DB = myMembershipSigneeClass.get_num_members_accepted()
        self.assertEqual(number_from_DB, 0)
        # go again
        instance.membership_accepted = True
        number_from_DB = myMembershipSigneeClass.get_num_members_accepted()
        self.assertEqual(number_from_DB, 1)

    def test_get_num_non_accepted(self):
        """
        test: get the number of non-accepted member entries in the database
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        number_from_DB = myMembershipSigneeClass.get_num_non_accepted()
        self.assertEqual(number_from_DB, 2)
        # go again
        instance.membership_accepted = True
        number_from_DB = myMembershipSigneeClass.get_num_non_accepted()
        self.assertEqual(number_from_DB, 1)

    def test_get_num_mem_nat_acc(self):
        """
        test: get the number of accepted member entries being natural persons
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        number_from_DB = myMembershipSigneeClass.get_num_mem_nat_acc()
        self.assertEqual(number_from_DB, 0)
        # go again
        instance.membership_accepted = True
        number_from_DB = myMembershipSigneeClass.get_num_mem_nat_acc()
        self.assertEqual(number_from_DB, 1)

    def test_get_num_mem_jur_acc(self):
        """
        test: get the number of accepted member entries being legal entities
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        number_from_DB = myMembershipSigneeClass.get_num_mem_jur_acc()
        self.assertEqual(number_from_DB, 0)
        # go again
        instance.membership_accepted = True
        instance.is_legalentity = True
        number_from_DB = myMembershipSigneeClass.get_num_mem_jur_acc()
        self.assertEqual(number_from_DB, 1)

    def test_get_num_mem_norm(self):
        """
        test: get the number of accepted member entries being normal members.
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        number_from_DB = myMembershipSigneeClass.get_num_mem_norm()
        self.assertEqual(number_from_DB, 0)
        # go again
        instance.membership_accepted = True
        self.assertEqual(instance.membership_type, u'normal')
        number_from_DB = myMembershipSigneeClass.get_num_mem_norm()
        self.assertEqual(number_from_DB, 1)

    def test_get_num_mem_invest(self):
        """
        test: get the number of accepted member entries being investing members
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        number_from_DB = myMembershipSigneeClass.get_num_mem_invest()
        self.assertEqual(number_from_DB, 0)
        # go again
        instance.membership_accepted = True
        instance.membership_type = u'investing'
        self.assertEqual(instance.membership_type, u'investing')
        number_from_DB = myMembershipSigneeClass.get_num_mem_invest()
        self.assertEqual(number_from_DB, 1)

    def test_get_num_mem_other_features(self):
        """
        test: get number of accepted member entries with silly membership type
        """
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        number_from_DB = myMembershipSigneeClass.get_num_mem_other_features()
        self.assertEqual(number_from_DB, 0)
        # go again
        instance.membership_accepted = True
        instance.membership_type = u'pondering'
        self.assertEqual(instance.membership_type, u'pondering')
        number_from_DB = myMembershipSigneeClass.get_num_mem_other_features()
        self.assertEqual(number_from_DB, 1)

    def test_is_member(self):
        member = C3sMember(  # german
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

        # not member
        member.membership_accepted = False
        member.membership_loss_date = None
        self.assertEqual(member.is_member(), False)

        # Accepted after check date
        member.membership_accepted = True
        member.membership_date = date(2016, 1, 1)
        member.membership_loss_date = None
        self.assertEqual(member.is_member(date(2015, 12, 31)), False)

        # Accepted in the past
        member.membership_accepted = True
        member.membership_date = date(2016, 1, 1)
        member.membership_loss_date = None
        self.assertEqual(member.is_member(), True)

        # If loss date is today then the member still has membership until the
        # end of the day
        member.membership_accepted = True
        member.membership_date = date(2016, 1, 1)
        member.membership_loss_date = date.today()
        self.assertEqual(member.is_member(), True)

        # If the loss date is in the future then the member still has membership
        member.membership_accepted = True
        member.membership_date = date(2016, 1, 1)
        member.membership_loss_date = date.today() + timedelta(days=1)
        self.assertEqual(member.is_member(), True)

        # If the loss date is in the past then the member no longer has
        # membership
        member.membership_accepted = True
        member.membership_date = date(2016, 1, 1)
        member.membership_loss_date = date.today() - timedelta(days=1)
        self.assertEqual(member.is_member(), False)


class TestMemberListing(C3sMembershipModelTestBase):
    """
    XXX TODO
    """
    def setUp(self):
        super(TestMemberListing, self).setUp()
        instance = self._makeOne(lastname=u"ABC", firstname=u'xyz',
                                 email_confirm_code=u'0987654321')
        self.session.add(instance)
        instance = self._makeAnotherOne(lastname=u"DEF", firstname=u'abc',
                                        email_confirm_code=u'19876543210')
        self.session.add(instance)
        instance = self._makeAnotherOne(lastname=u"GHI", firstname=u'def',
                                        email_confirm_code=u'098765432101')
        self.session.add(instance)
        self.session.flush()
        self.class_under_test = self._getTargetClass()

    def test_orderByLastname_sortedByLastname(self):
        result = self.class_under_test.member_listing(order_by='lastname')
        self.assertIsNotNone(result)
        self.assertIsNotNone(result[0])
        self.assertEqual("ABC", result[0].lastname)
        self.assertEqual("GHI", result[-1].lastname)

    def test_orderByLastnameOrderAsc_sortedByLastname(self):
        result = self.class_under_test.member_listing(
            order_by='lastname', order="asc")
        self.assertIsNotNone(result)
        self.assertIsNotNone(result[0])
        self.assertEqual("ABC", result[0].lastname)
        self.assertEqual("GHI", result[-1].lastname)

    def test_orderByLastnameOrderDesc_sortedByLastname(self):
        result = self.class_under_test.member_listing(
            order_by='lastname', order="desc")
        self.assertIsNotNone(result)
        self.assertIsNotNone(result[0])
        self.assertEqual("GHI", result[0].lastname)
        self.assertEqual("ABC", result[-1].lastname)

    def test_orderByInvalidName_raisesException(self):
        self.assertRaises(self.class_under_test.member_listing,
                          order_by='unknown', order="desc")
        self.assertRaises(self.class_under_test.member_listing,
                          order_by=None, order="desc")
        self.assertRaises(self.class_under_test.member_listing,
                          order_by="", order="desc")

    def test_orderInvalid_raisesException(self):
        self.assertRaises(self.class_under_test.member_listing,
                          order_by='lastname', order="unknown")
        self.assertRaises(self.class_under_test.member_listing,
                          order_by='lastname', order="")
        self.assertRaises(self.class_under_test.member_listing,
                          order_by='lastname', order=None)

# class MembershipNumberModelTestBase(C3sMembershipModelTestBase):
# XXX TODO


class GroupTests(unittest.TestCase):
    """
    test the groups
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
        except:
            pass
        # engine = create_engine('sqlite:///test_model_groups.db')
        engine = create_engine('sqlite://')
        self.session = DBSession
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

        with transaction.manager:
            group1 = Group(name=u'staff')
            DBSession.add(group1)
            DBSession.flush()
            self.assertEquals(group1.__str__(), 'group:staff')

    def tearDown(self):
        self.session.close()
        self.session.remove()
        # os.remove('test_model_groups.db')

    def test_group(self):
        result = Group.get_staffers_group()
        self.assertEquals(result.__str__(), 'group:staff')

    def test__str__(self):
        g1 = Group.get_staffers_group()
        res = g1.__str__()
        self.assertEquals(res, 'group:staff')


class C3sStaffTests(unittest.TestCase):
    """
    test the staff and cashiers accounts
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
        except:
            pass
        # engine = create_engine('sqlite:///test_model_staff.db')
        engine = create_engine('sqlite://')
        self.session = DBSession
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

        with transaction.manager:
            group1 = Group(name=u'staff')
            group2 = Group(name=u'staff2')
            DBSession.add(group1, group2)
            DBSession.flush()

    def tearDown(self):
        self.session.close()
        self.session.remove()
        # os.remove('test_model_staff.db')

    def test_staff(self):
        staffer1 = C3sStaff(
            login=u'staffer1',
            password=u'stafferspassword'
        )
        staffer1.group = ['staff']
        staffer2 = C3sStaff(
            login=u'staffer2',
            password=u'staffer2spassword',
        )
        staffer2.group = ['staff2']

        self.session.add(staffer1)
        self.session.add(staffer2)
        self.session.flush()

        _staffer2_id = staffer2.id
        _staffer1_id = staffer1.id

        self.assertTrue(staffer2.password is not '')

        # print('by id: %s' % C3sStaff.get_by_id(_staffer1_id))
        # print('by id: %s' % C3sStaff.get_by_id(_cashier1_id))
        # print('by login: %s' % C3sStaff.get_by_login(u'staffer1'))
        # print('by login: %s' % C3sStaff.get_by_login(u'cashier1'))
        self.assertEqual(
            C3sStaff.get_by_id(_staffer1_id),
            C3sStaff.get_by_login(u'staffer1')
        )
        self.assertEqual(
            C3sStaff.get_by_id(_staffer2_id),
            C3sStaff.get_by_login(u'staffer2')
        )

        '''test get_all'''
        res = C3sStaff.get_all()
        self.assertEqual(len(res), 2)

        '''test delete_by_id'''
        C3sStaff.delete_by_id(1)
        res = C3sStaff.get_all()
        self.assertEqual(len(res), 1)

        '''test check_user_or_none'''
        res1 = C3sStaff.check_user_or_none(u'staffer2')
        res2 = C3sStaff.check_user_or_none(u'staffer1')
        # print res1
        # print res2
        self.assertTrue(res1 is not None)
        self.assertTrue(res2 is None)

        '''test check_password'''
        # print(C3sStaff.check_password(cashier1, 'cashierspassword'))
        C3sStaff.check_password(u'staffer2', u'staffer2spassword')
        # self.assert


class Dues15InvoiceModelTests(unittest.TestCase):
    """
    test the dues15 invoice model
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
        except:
            pass
        # engine = create_engine('sqlite:///test_model_staff.db')
        engine = create_engine('sqlite://')
        self.session = DBSession
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

        with transaction.manager:
            member1 = C3sMember(
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
            DBSession.add(member1)

            member2 = C3sMember(
                firstname=u'Franziska',
                lastname=u'Musterfrau',
                email=u'some@shri.de',
                address1=u"addr one",
                address2=u"addr two",
                postcode=u"12345",
                city=u"Footown Mäh",
                country=u"Foocountry",
                locale=u"DE",
                date_of_birth=date.today(),
                email_is_confirmed=False,
                email_confirm_code=u'ABCDEFGFO1',
                password=u'arandompassword',
                date_of_submission=date.today(),
                membership_type=u'normal',
                member_of_colsoc=False,
                name_of_colsoc=u'',
                num_shares=u'23',
            )
            DBSession.add(member2)

            member3 = C3sMember(
                firstname=u'Jane',
                lastname=u'Somebody',
                email=u'some@shri.de',
                address1=u"addr one",
                address2=u"addr two",
                postcode=u"12345",
                city=u"Footown Mäh",
                country=u"Foocountry",
                locale=u"DE",
                date_of_birth=date.today(),
                email_is_confirmed=False,
                email_confirm_code=u'ABCDEFGFO2',
                password=u'arandompassword',
                date_of_submission=date.today(),
                membership_type=u'normal',
                member_of_colsoc=False,
                name_of_colsoc=u'',
                num_shares=u'23',
            )
            DBSession.add(member3)

            dues1 = Dues15Invoice(
                invoice_no=1,
                invoice_no_string=u'C3S-dues15-0001',
                invoice_date=date(2015, 10, 01),
                invoice_amount=D('-37.50'),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues1)

            dues2 = Dues15Invoice(
                invoice_no=2,
                invoice_no_string=u'C3S-dues15-0002-S',
                invoice_date=date(2015, 10, 02),
                invoice_amount=D('17.25'),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'fa4wfjlasjfd',
            )
            dues2.is_reversal = True
            DBSession.add(dues2)

            dues3 = Dues15Invoice(
                invoice_no=3,
                invoice_no_string=u'C3S-dues15-0003',
                invoice_date=date(2015, 11, 25),
                invoice_amount=D('74.58'),
                member_id=1,
                membership_no=2,
                email=u'uat.yes@c3s.cc',
                token=u'Jleifjsw9e',
            )
            DBSession.add(dues3)

            dues4 = Dues15Invoice(
                invoice_no=4,
                invoice_no_string=u'C3S-dues15-0004-S',
                invoice_date=date(2015, 11, 27),
                invoice_amount=D('23.85'),
                member_id=1,
                membership_no=2,
                email=u'uat.yes@c3s.cc',
                token=u'f348h98sdf',
            )
            dues4.is_reversal = True
            DBSession.add(dues4)

            dues5 = Dues15Invoice(
                invoice_no=5,
                invoice_no_string=u'C3S-dues15-0005',
                invoice_date=date(2015, 11, 29),
                invoice_amount=D('12.89'),
                member_id=1,
                membership_no=3,
                email=u'uat.yes@c3s.cc',
                token=u'sgdfoiddfg',
            )
            DBSession.add(dues5)

            dues6 = Dues15Invoice(
                invoice_no=6,
                invoice_no_string=u'C3S-dues15-0006-S',
                invoice_date=date(2015, 11, 30),
                invoice_amount=D('77.79'),
                member_id=1,
                membership_no=3,
                email=u'uat.yes@c3s.cc',
                token=u'3o948n',
            )
            dues6.is_reversal = True
            DBSession.add(dues6)
            DBSession.flush()

            member1.set_dues15_payment(D('12.34'), date(2015, 10, 31))
            member2.set_dues15_payment(D('95.65'), date(2015, 11, 5))
            member3.set_dues15_payment(D('-85.12'), date(2015, 11, 30))

    def tearDown(self):
        self.session.close()
        self.session.remove()
        # os.remove('test_model_staff.db')

    def test_get_all(self):
        '''
        test get_all
        '''
        res = Dues15Invoice.get_all()
        self.assertEqual(len(res), 6)

    def test_get_by_invoice_no(self):
        '''
        test get_by_invoice_no
        '''
        res = Dues15Invoice.get_by_invoice_no(1)
        self.assertEqual(res.id, 1)

    def test_get_by_membership_no(self):
        '''
        test get_by_invoice_no
        '''
        res = Dues15Invoice.get_by_membership_no(1)
        self.assertEqual(res[0].id, 1)  # is a list

    def test_get_max_invoice_no(self):
        '''
        test get_max_invoice_no
        '''
        res = Dues15Invoice.get_max_invoice_no()
        self.assertEqual(res, 6)

    def test_check_for_existing_dues15_token(self):
        """
        test check_for_existing_dues15_token
        """
        res = Dues15Invoice.check_for_existing_dues15_token(
            u'ABCDEFGH')
        self.assertEqual(res, True)
        res2 = Dues15Invoice.check_for_existing_dues15_token(
            u'ABCDEFGHIK0000000000')
        self.assertEqual(res2, False)

    def test_get_monthly_stats(self):
        """
        Test get_monthly_stats.
        """
        stats = Dues15Invoice.get_monthly_stats()
        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]['month'], datetime(2015, 10, 1))
        self.assertAlmostEqual(stats[0]['amount_invoiced_normal'], D('-37.50'))
        self.assertAlmostEqual(
            stats[0]['amount_invoiced_reversal'], D('17.25'))
        self.assertAlmostEqual(stats[0]['amount_paid'], D('12.34'))
        self.assertEqual(stats[1]['month'], datetime(2015, 11, 1))
        self.assertAlmostEqual(stats[1]['amount_invoiced_normal'], D('87.47'))
        self.assertAlmostEqual(
            stats[1]['amount_invoiced_reversal'], D('101.64'))
        self.assertAlmostEqual(stats[1]['amount_paid'], D('10.53'))

    def test_decimality(self):
        """
        test the features of the 'amounts', esp. the format and persistence
        """

        # try to make another invoice with the same number
        def trigger_IntegrityError1():
            dues2 = Dues15Invoice(
                invoice_no=1,
                invoice_no_string=u'C3S-dues15-0001',
                invoice_date=date.today(),
                invoice_amount=unicode(D('-37.50').to_eng_string()),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues2)
            DBSession.flush()

        self.assertTrue(True)
        self.assertRaises(IntegrityError, trigger_IntegrityError1)
        self.session.rollback()

        res = Dues15Invoice.get_all()
        self.assertEqual(len(res), 6)

        # try to make another invoice with the same string
        def trigger_IntegrityError2():
            dues2 = Dues15Invoice(
                invoice_no=2,
                invoice_no_string=u'C3S-dues15-0001',
                invoice_date=date.today(),
                invoice_amount=unicode(D('-37.50').to_eng_string()),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues2)
            DBSession.flush()

        self.assertTrue(True)
        self.assertRaises(IntegrityError, trigger_IntegrityError2)
        self.session.rollback()

        res = Dues15Invoice.get_all()
        self.assertEqual(len(res), 6)

        # try to make another invoice with a non-decimal amount
        # InvalidOperation: Invalid literal for Decimal: '-37.50.20'
        def trigger_InvalidOperation():
            dues2 = Dues15Invoice(
                invoice_no=5,
                invoice_no_string=u'C3S-dues15-0002',
                invoice_date=date.today(),
                invoice_amount=unicode(D('-37.50.20').to_eng_string()),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues2)
            DBSession.flush()

        self.assertTrue(True)
        self.assertRaises(InvalidOperation, trigger_InvalidOperation)
        # trigger_InvalidOperation()
        self.session.rollback()

        res = Dues15Invoice.get_all()
        self.assertEqual(len(res), 6)

        # now really store a new Dues15Invoice
        dues3 = Dues15Invoice(
            invoice_no=7,
            invoice_no_string=u'C3S-dues15-0002',
            invoice_date=date.today(),
            # invoice_amount=unicode(D('-37.50').to_eng_string()),
            invoice_amount=D('-37.50').to_eng_string(),
            member_id=1,
            membership_no=1,
            email=u'uat.yes@c3s.cc',
            token=u'ABCDEFGH',
        )
        DBSession.add(dues3)
        DBSession.flush()

        res = Dues15Invoice.get_all()
        self.assertEqual(len(res), 7)
        self.assertEqual(dues3.id, 7)
        # print(type(dues3.invoice_amount))

class Dues16InvoiceModelTests(unittest.TestCase):
    """
    test the dues16 invoice model
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
        except:
            pass
        # engine = create_engine('sqlite:///test_model_staff.db')
        engine = create_engine('sqlite://')
        self.session = DBSession
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

        with transaction.manager:
            member1 = C3sMember(
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
            DBSession.add(member1)

            member2 = C3sMember(
                firstname=u'Franziska',
                lastname=u'Musterfrau',
                email=u'some@shri.de',
                address1=u"addr one",
                address2=u"addr two",
                postcode=u"12345",
                city=u"Footown Mäh",
                country=u"Foocountry",
                locale=u"DE",
                date_of_birth=date.today(),
                email_is_confirmed=False,
                email_confirm_code=u'ABCDEFGFO1',
                password=u'arandompassword',
                date_of_submission=date.today(),
                membership_type=u'normal',
                member_of_colsoc=False,
                name_of_colsoc=u'',
                num_shares=u'23',
            )
            DBSession.add(member2)

            member3 = C3sMember(
                firstname=u'Jane',
                lastname=u'Somebody',
                email=u'some@shri.de',
                address1=u"addr one",
                address2=u"addr two",
                postcode=u"12345",
                city=u"Footown Mäh",
                country=u"Foocountry",
                locale=u"DE",
                date_of_birth=date.today(),
                email_is_confirmed=False,
                email_confirm_code=u'ABCDEFGFO2',
                password=u'arandompassword',
                date_of_submission=date.today(),
                membership_type=u'normal',
                member_of_colsoc=False,
                name_of_colsoc=u'',
                num_shares=u'23',
            )
            DBSession.add(member3)

            dues1 = Dues16Invoice(
                invoice_no=1,
                invoice_no_string=u'C3S-dues16-0001',
                invoice_date=date(2015, 10, 01),
                invoice_amount=D('-37.50'),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues1)

            dues2 = Dues16Invoice(
                invoice_no=2,
                invoice_no_string=u'C3S-dues16-0002-S',
                invoice_date=date(2015, 10, 02),
                invoice_amount=D('17.25'),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'fa4wfjlasjfd',
            )
            dues2.is_reversal = True
            DBSession.add(dues2)

            dues3 = Dues16Invoice(
                invoice_no=3,
                invoice_no_string=u'C3S-dues16-0003',
                invoice_date=date(2015, 11, 25),
                invoice_amount=D('74.58'),
                member_id=1,
                membership_no=2,
                email=u'uat.yes@c3s.cc',
                token=u'Jleifjsw9e',
            )
            DBSession.add(dues3)

            dues4 = Dues16Invoice(
                invoice_no=4,
                invoice_no_string=u'C3S-dues16-0004-S',
                invoice_date=date(2015, 11, 27),
                invoice_amount=D('23.85'),
                member_id=1,
                membership_no=2,
                email=u'uat.yes@c3s.cc',
                token=u'f348h98sdf',
            )
            dues4.is_reversal = True
            DBSession.add(dues4)

            dues5 = Dues16Invoice(
                invoice_no=5,
                invoice_no_string=u'C3S-dues16-0005',
                invoice_date=date(2015, 11, 29),
                invoice_amount=D('12.89'),
                member_id=1,
                membership_no=3,
                email=u'uat.yes@c3s.cc',
                token=u'sgdfoiddfg',
            )
            DBSession.add(dues5)

            dues6 = Dues16Invoice(
                invoice_no=6,
                invoice_no_string=u'C3S-dues16-0006-S',
                invoice_date=date(2015, 11, 30),
                invoice_amount=D('77.79'),
                member_id=1,
                membership_no=3,
                email=u'uat.yes@c3s.cc',
                token=u'3o948n',
            )
            dues6.is_reversal = True
            DBSession.add(dues6)
            DBSession.flush()

            member1.set_dues16_payment(D('12.34'), date(2015, 10, 31))
            member2.set_dues16_payment(D('95.65'), date(2015, 11, 5))
            member3.set_dues16_payment(D('-85.12'), date(2015, 11, 30))

    def tearDown(self):
        self.session.close()
        self.session.remove()
        # os.remove('test_model_staff.db')

    def test_get_all(self):
        '''
        test get_all
        '''
        res = Dues16Invoice.get_all()
        self.assertEqual(len(res), 6)

    def test_get_by_invoice_no(self):
        '''
        test get_by_invoice_no
        '''
        res = Dues16Invoice.get_by_invoice_no(1)
        self.assertEqual(res.id, 1)

    def test_get_by_membership_no(self):
        '''
        test get_by_invoice_no
        '''
        res = Dues16Invoice.get_by_membership_no(1)
        self.assertEqual(res[0].id, 1)  # is a list

    def test_get_max_invoice_no(self):
        '''
        test get_max_invoice_no
        '''
        res = Dues16Invoice.get_max_invoice_no()
        self.assertEqual(res, 6)

    def test_check_for_existing_dues16_token(self):
        """
        test check_for_existing_dues16_token
        """
        res = Dues16Invoice.check_for_existing_dues16_token(
            u'ABCDEFGH')
        self.assertEqual(res, True)
        res2 = Dues16Invoice.check_for_existing_dues16_token(
            u'ABCDEFGHIK0000000000')
        self.assertEqual(res2, False)

    def test_get_monthly_stats(self):
        """
        Test get_monthly_stats.
        """
        stats = Dues16Invoice.get_monthly_stats()
        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]['month'], datetime(2015, 10, 1))
        self.assertAlmostEqual(stats[0]['amount_invoiced_normal'], D('-37.50'))
        self.assertAlmostEqual(
            stats[0]['amount_invoiced_reversal'], D('17.25'))
        self.assertAlmostEqual(stats[0]['amount_paid'], D('12.34'))
        self.assertEqual(stats[1]['month'], datetime(2015, 11, 1))
        self.assertAlmostEqual(stats[1]['amount_invoiced_normal'], D('87.47'))
        self.assertAlmostEqual(
            stats[1]['amount_invoiced_reversal'], D('101.64'))
        self.assertAlmostEqual(stats[1]['amount_paid'], D('10.53'))

    def test_decimality(self):
        """
        test the features of the 'amounts', esp. the format and persistence
        """

        # try to make another invoice with the same number
        def trigger_IntegrityError1():
            dues2 = Dues16Invoice(
                invoice_no=1,
                invoice_no_string=u'C3S-dues16-0001',
                invoice_date=date.today(),
                invoice_amount=unicode(D('-37.50').to_eng_string()),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues2)
            DBSession.flush()

        self.assertTrue(True)
        self.assertRaises(IntegrityError, trigger_IntegrityError1)
        self.session.rollback()

        res = Dues16Invoice.get_all()
        self.assertEqual(len(res), 6)

        # try to make another invoice with the same string
        def trigger_IntegrityError2():
            dues2 = Dues16Invoice(
                invoice_no=2,
                invoice_no_string=u'C3S-dues16-0001',
                invoice_date=date.today(),
                invoice_amount=unicode(D('-37.50').to_eng_string()),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues2)
            DBSession.flush()

        self.assertTrue(True)
        self.assertRaises(IntegrityError, trigger_IntegrityError2)
        self.session.rollback()

        res = Dues16Invoice.get_all()
        self.assertEqual(len(res), 6)

        # try to make another invoice with a non-decimal amount
        # InvalidOperation: Invalid literal for Decimal: '-37.50.20'
        def trigger_InvalidOperation():
            dues2 = Dues16Invoice(
                invoice_no=5,
                invoice_no_string=u'C3S-dues16-0002',
                invoice_date=date.today(),
                invoice_amount=unicode(D('-37.50.20').to_eng_string()),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues2)
            DBSession.flush()

        self.assertTrue(True)
        self.assertRaises(InvalidOperation, trigger_InvalidOperation)
        # trigger_InvalidOperation()
        self.session.rollback()

        res = Dues16Invoice.get_all()
        self.assertEqual(len(res), 6)

        # now really store a new Dues16Invoice
        dues3 = Dues16Invoice(
            invoice_no=7,
            invoice_no_string=u'C3S-dues16-0002',
            invoice_date=date.today(),
            # invoice_amount=unicode(D('-37.50').to_eng_string()),
            invoice_amount=D('-37.50').to_eng_string(),
            member_id=1,
            membership_no=1,
            email=u'uat.yes@c3s.cc',
            token=u'ABCDEFGH',
        )
        DBSession.add(dues3)
        DBSession.flush()

        res = Dues16Invoice.get_all()
        self.assertEqual(len(res), 7)
        self.assertEqual(dues3.id, 7)
        # print(type(dues3.invoice_amount))


class Dues17InvoiceModelTests(unittest.TestCase):
    """
    test the dues17 invoice model
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
        except:
            pass
        # engine = create_engine('sqlite:///test_model_staff.db')
        engine = create_engine('sqlite://')
        self.session = DBSession
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

        with transaction.manager:
            member1 = C3sMember(
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
            DBSession.add(member1)

            member2 = C3sMember(
                firstname=u'Franziska',
                lastname=u'Musterfrau',
                email=u'some@shri.de',
                address1=u"addr one",
                address2=u"addr two",
                postcode=u"12345",
                city=u"Footown Mäh",
                country=u"Foocountry",
                locale=u"DE",
                date_of_birth=date.today(),
                email_is_confirmed=False,
                email_confirm_code=u'ABCDEFGFO1',
                password=u'arandompassword',
                date_of_submission=date.today(),
                membership_type=u'normal',
                member_of_colsoc=False,
                name_of_colsoc=u'',
                num_shares=u'23',
            )
            DBSession.add(member2)

            member3 = C3sMember(
                firstname=u'Jane',
                lastname=u'Somebody',
                email=u'some@shri.de',
                address1=u"addr one",
                address2=u"addr two",
                postcode=u"12345",
                city=u"Footown Mäh",
                country=u"Foocountry",
                locale=u"DE",
                date_of_birth=date.today(),
                email_is_confirmed=False,
                email_confirm_code=u'ABCDEFGFO2',
                password=u'arandompassword',
                date_of_submission=date.today(),
                membership_type=u'normal',
                member_of_colsoc=False,
                name_of_colsoc=u'',
                num_shares=u'23',
            )
            DBSession.add(member3)

            dues1 = Dues17Invoice(
                invoice_no=1,
                invoice_no_string=u'C3S-dues17-0001',
                invoice_date=date(2015, 10, 01),
                invoice_amount=D('-37.50'),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues1)

            dues2 = Dues17Invoice(
                invoice_no=2,
                invoice_no_string=u'C3S-dues17-0002-S',
                invoice_date=date(2015, 10, 02),
                invoice_amount=D('16.25'),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'fa4wfjlasjfd',
            )
            dues2.is_reversal = True
            DBSession.add(dues2)

            dues3 = Dues17Invoice(
                invoice_no=3,
                invoice_no_string=u'C3S-dues17-0003',
                invoice_date=date(2015, 11, 25),
                invoice_amount=D('74.58'),
                member_id=1,
                membership_no=2,
                email=u'uat.yes@c3s.cc',
                token=u'Jleifjsw9e',
            )
            DBSession.add(dues3)

            dues4 = Dues17Invoice(
                invoice_no=4,
                invoice_no_string=u'C3S-dues17-0004-S',
                invoice_date=date(2015, 11, 27),
                invoice_amount=D('23.85'),
                member_id=1,
                membership_no=2,
                email=u'uat.yes@c3s.cc',
                token=u'f348h98sdf',
            )
            dues4.is_reversal = True
            DBSession.add(dues4)

            dues5 = Dues17Invoice(
                invoice_no=5,
                invoice_no_string=u'C3S-dues17-0005',
                invoice_date=date(2015, 11, 29),
                invoice_amount=D('12.89'),
                member_id=1,
                membership_no=3,
                email=u'uat.yes@c3s.cc',
                token=u'sgdfoiddfg',
            )
            DBSession.add(dues5)

            dues6 = Dues17Invoice(
                invoice_no=6,
                invoice_no_string=u'C3S-dues17-0006-S',
                invoice_date=date(2015, 11, 30),
                invoice_amount=D('77.79'),
                member_id=1,
                membership_no=3,
                email=u'uat.yes@c3s.cc',
                token=u'3o948n',
            )
            dues6.is_reversal = True
            DBSession.add(dues6)
            DBSession.flush()

            member1.set_dues17_payment(D('12.34'), date(2015, 10, 31))
            member2.set_dues17_payment(D('95.65'), date(2015, 11, 5))
            member3.set_dues17_payment(D('-85.12'), date(2015, 11, 30))

    def tearDown(self):
        self.session.close()
        self.session.remove()
        # os.remove('test_model_staff.db')

    def test_get_all(self):
        '''
        test get_all
        '''
        res = Dues17Invoice.get_all()
        self.assertEqual(len(res), 6)

    def test_get_by_invoice_no(self):
        '''
        test get_by_invoice_no
        '''
        res = Dues17Invoice.get_by_invoice_no(1)
        self.assertEqual(res.id, 1)

    def test_get_by_membership_no(self):
        '''
        test get_by_invoice_no
        '''
        res = Dues17Invoice.get_by_membership_no(1)
        self.assertEqual(res[0].id, 1)  # is a list

    def test_get_max_invoice_no(self):
        '''
        test get_max_invoice_no
        '''
        res = Dues17Invoice.get_max_invoice_no()
        self.assertEqual(res, 6)

    def test_check_for_existing_dues17_token(self):
        """
        test check_for_existing_dues17_token
        """
        res = Dues17Invoice.check_for_existing_dues17_token(
            u'ABCDEFGH')
        self.assertEqual(res, True)
        res2 = Dues17Invoice.check_for_existing_dues17_token(
            u'ABCDEFGHIK0000000000')
        self.assertEqual(res2, False)

    def test_get_monthly_stats(self):
        """
        Test get_monthly_stats.
        """
        stats = Dues17Invoice.get_monthly_stats()
        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]['month'], datetime(2015, 10, 1))
        self.assertAlmostEqual(stats[0]['amount_invoiced_normal'], D('-37.50'))
        self.assertAlmostEqual(
            stats[0]['amount_invoiced_reversal'], D('16.25'))
        self.assertAlmostEqual(stats[0]['amount_paid'], D('12.34'))
        self.assertEqual(stats[1]['month'], datetime(2015, 11, 1))
        self.assertAlmostEqual(stats[1]['amount_invoiced_normal'], D('87.47'))
        self.assertAlmostEqual(
            stats[1]['amount_invoiced_reversal'], D('101.64'))
        self.assertAlmostEqual(stats[1]['amount_paid'], D('10.53'))

    def test_decimality(self):
        """
        test the features of the 'amounts', esp. the format and persistence
        """

        # try to make another invoice with the same number
        def trigger_IntegrityError1():
            dues2 = Dues17Invoice(
                invoice_no=1,
                invoice_no_string=u'C3S-dues17-0001',
                invoice_date=date.today(),
                invoice_amount=unicode(D('-37.50').to_eng_string()),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues2)
            DBSession.flush()

        self.assertTrue(True)
        self.assertRaises(IntegrityError, trigger_IntegrityError1)
        self.session.rollback()

        res = Dues17Invoice.get_all()
        self.assertEqual(len(res), 6)

        # try to make another invoice with the same string
        def trigger_IntegrityError2():
            dues2 = Dues17Invoice(
                invoice_no=2,
                invoice_no_string=u'C3S-dues17-0001',
                invoice_date=date.today(),
                invoice_amount=unicode(D('-37.50').to_eng_string()),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues2)
            DBSession.flush()

        self.assertTrue(True)
        self.assertRaises(IntegrityError, trigger_IntegrityError2)
        self.session.rollback()

        res = Dues17Invoice.get_all()
        self.assertEqual(len(res), 6)

        # try to make another invoice with a non-decimal amount
        # InvalidOperation: Invalid literal for Decimal: '-37.50.20'
        def trigger_InvalidOperation():
            dues2 = Dues17Invoice(
                invoice_no=5,
                invoice_no_string=u'C3S-dues17-0002',
                invoice_date=date.today(),
                invoice_amount=unicode(D('-37.50.20').to_eng_string()),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues2)
            DBSession.flush()

        self.assertTrue(True)
        self.assertRaises(InvalidOperation, trigger_InvalidOperation)
        # trigger_InvalidOperation()
        self.session.rollback()

        res = Dues17Invoice.get_all()
        self.assertEqual(len(res), 6)

        # now really store a new Dues17Invoice
        dues3 = Dues17Invoice(
            invoice_no=7,
            invoice_no_string=u'C3S-dues17-0002',
            invoice_date=date.today(),
            # invoice_amount=unicode(D('-37.50').to_eng_string()),
            invoice_amount=D('-37.50').to_eng_string(),
            member_id=1,
            membership_no=1,
            email=u'uat.yes@c3s.cc',
            token=u'ABCDEFGH',
        )
        DBSession.add(dues3)
        DBSession.flush()

        res = Dues17Invoice.get_all()
        self.assertEqual(len(res), 7)
        self.assertEqual(dues3.id, 7)
        # print(type(dues3.invoice_amount))
