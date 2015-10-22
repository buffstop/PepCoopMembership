# -*- coding: utf-8  -*-
# import os
from datetime import date
from decimal import Decimal as D
from decimal import InvalidOperation
from pyramid import testing
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import transaction
import unittest

from c3smembership.models import (
    Base,
    C3sMember,
    C3sStaff,
    DBSession,
    Dues15Invoice,
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

    def test_get_number(self):
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        number_from_DB = myMembershipSigneeClass.get_number()
        # print number_from_DB
        self.assertEqual(number_from_DB, 2)

    def test_get_by_code(self):
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

    def test_get_by_dues15_token(self):
        instance = self._makeOne()
        self.session.add(instance)
        instance.dues15_token = u'THIS_ONE'
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_dues15_token(
            u'THIS_ONE')
        self.assertEqual(instance_from_DB.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.email, u'some@shri.de')

    def test_get_by_email(self):
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        list_from_DB = myMembershipSigneeClass.get_by_email(
            u'some@shri.de')
        self.assertEqual(list_from_DB[0].firstname, u'SomeFirstnäme')
        self.assertEqual(list_from_DB[0].email, u'some@shri.de')

    def test_get_by_id(self):
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
        instance = self._makeOne()
        instance2 = self._makeAnotherOne()
        self.session.add(instance, instance2)
        self.session.flush()
        myMembershipSigneeClass = self._getTargetClass()
        all = myMembershipSigneeClass.get_all()
        self.assertEquals(len(all), 2)

    def test_get_dues_invoicees(self):
        instance = self._makeOne()
        instance2 = self._makeAnotherOne()
        self.session.add(instance, instance2)
        self.session.flush()
        myMembershipSigneeClass = self._getTargetClass()
        invoicees = myMembershipSigneeClass.get_dues_invoicees(27)
        self.assertEquals(len(invoicees), 0)
        # change details so they be found
        instance.membership_accepted = True
        instance2.membership_accepted = True
        invoicees = myMembershipSigneeClass.get_dues_invoicees(27)
        self.assertEquals(len(invoicees), 1)
        
    def test_delete_by_id(self):
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_id('1')
        del_instance_from_DB = myMembershipSigneeClass.delete_by_id('1')
        del_instance_from_DB
        instance_from_DB = myMembershipSigneeClass.get_by_id('1')
        self.assertEqual(None, instance_from_DB)

    def test_check_user_or_None(self):
        instance = self._makeOne()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        # get first dataset (id = 1)
        result1 = myMembershipSigneeClass.check_user_or_None('1')
        self.assertEqual(1, result1.id)
        # get invalid dataset
        result2 = myMembershipSigneeClass.check_user_or_None('1234567')
        self.assertEqual(None, result2)

    def test_check_for_existing_confirm_code(self):
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
        instance = self._makeOne()
        self.session.add(instance)
        instance2 = self._makeAnotherOne()
        self.session.add(instance2)
        myMembershipSigneeClass = self._getTargetClass()

        result1 = myMembershipSigneeClass.member_listing("id")
        self.failUnless(result1[0].firstname == u"SomeFirstnäme")
        self.failUnless(result1[1].firstname == u"SomeFirstnäme")
        self.failUnless(result1[2].firstname == u"SomeFirstname")

    def test_member_listing_exception(self):
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


class TestMemberListing(C3sMembershipModelTestBase):
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

        '''test check_user_or_None'''
        res1 = C3sStaff.check_user_or_None(u'staffer2')
        res2 = C3sStaff.check_user_or_None(u'staffer1')
        # print res1
        # print res2
        self.assertTrue(res1 is not None)
        self.assertTrue(res2 is None)

        '''test check_password'''
        # print(C3sStaff.check_password(cashier1, 'cashierspassword'))
        C3sStaff.check_password(u'staffer2', u'staffer2spassword')
        # self.assert


class SharesModelTests(unittest.TestCase):
    """
    test the shares model
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
            shares1 = Shares(
                number=10,
                date_of_acquisition=date.today(),
                reference_code=u'ABCDEFGH',
                signature_received=True,
                signature_received_date=date.today(),
                payment_received=True,
                payment_received_date=date.today()
            )
            DBSession.add(shares1)
            DBSession.flush()

    def tearDown(self):
        self.session.close()
        self.session.remove()
        # os.remove('test_model_staff.db')

    def test_get_all(self):
        '''
        test get_all
        '''
        res = Shares.get_all()
        self.assertEqual(len(res), 1)

    def test_get_number(self):
        '''
        test get_number
        '''
        res = Shares.get_number()
        self.assertEqual(res, 1)

    def test_get_max_id(self):
        '''
        test get_max_id
        '''
        res = Shares.get_max_id()
        self.assertEqual(res, 1)

    def test_get_by_id(self):
        '''
        test get_by_id
        '''
        res = Shares.get_by_id(1)
        self.assertEqual(res.id, 1)

    def test_get_total_shares(self):
        '''
        test get_total shares
        '''
        res = Shares.get_total_shares()
        self.assertEqual(res, 10)

    def test_delete_by_id(self):
        '''test delete_by_id'''
        self.assertEqual(len(Shares.get_all()), 1)
        # returns 0 if no shares found to delete
        res = Shares.delete_by_id(10)
        self.assertEqual(res, 0)

        # returns 1 if shares found and deleted
        res = Shares.delete_by_id(1)
        self.assertEqual(res, 1)
        res2 = Shares.get_all()
        self.assertEqual(len(res2), 0)


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
            dues1 = Dues15Invoice(
                invoice_no=1,
                invoice_no_string=u'C3S-dues15-0001',
                invoice_date=date.today(),
                invoice_amount=unicode(D('-37.50').to_eng_string()),
                member_id=1,
                membership_no=1,
                email=u'uat.yes@c3s.cc',
                token=u'ABCDEFGH',
            )
            DBSession.add(dues1)
            DBSession.flush()

    def tearDown(self):
        self.session.close()
        self.session.remove()
        # os.remove('test_model_staff.db')

    def test_get_all(self):
        '''
        test get_all
        '''
        res = Dues15Invoice.get_all()
        self.assertEqual(len(res), 1)

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
        self.assertEqual(res, 1)

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
        self.assertEqual(len(res), 1)

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
        self.assertEqual(len(res), 1)

        # try to make another invoice with a non-decimal amount
        # InvalidOperation: Invalid literal for Decimal: '-37.50.20'
        def trigger_InvalidOperation():
            dues2 = Dues15Invoice(
                invoice_no=2,
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
        self.assertEqual(len(res), 1)

        # now really store a new Dues15Invoice
        dues3 = Dues15Invoice(
            invoice_no=2,
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
        self.assertEqual(len(res), 2)
        self.assertEqual(dues3.id, 2)
        # print(type(dues3.invoice_amount))
