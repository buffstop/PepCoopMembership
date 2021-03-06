#!/bin/env/python
# -*- coding: utf-8 -*-

from datetime import (datetime, date)

import unittest
from pyramid import testing
from sqlalchemy import engine_from_config
import transaction

from c3smembership.data.model.base import (
    DBSession,
    Base,
)
from c3smembership.models import (
    C3sMember,
    C3sStaff,
    Group,
    Shares,
)

DEBUG = False


class SharesTests(unittest.TestCase):
    """
    these tests are functional tests to check functionality of the whole app
    (i.e. integration tests)
    they also serve to get coverage for 'main'
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.close()
            DBSession.remove()
            # print "closed and removed DBSession"
        except:
            pass
            # print "no session to close"
        my_settings = {
            'sqlalchemy.url': 'sqlite:///:memory:',
            'available_languages': 'da de en es fr',
            'c3smembership.dashboard_number': '30'}
        engine = engine_from_config(my_settings)
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

        with transaction.manager:
            # a group for accountants/staff
            accountants_group = Group(name=u"staff")
            try:
                DBSession.add(accountants_group)
                DBSession.flush()
                # print("adding group staff")
            except:
                # print("could not add group staff.")
                pass
            # staff personnel
            staffer1 = C3sStaff(
                login=u"rut",
                password=u"berries",
                email=u"noreply@c3s.cc",
            )
            staffer1.groups = [accountants_group]
            try:
                DBSession.add(accountants_group)
                DBSession.add(staffer1)
                DBSession.flush()
            except:
                # print("it borked! (rut)")
                pass

        from c3smembership import main
        app = main({}, **my_settings)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        DBSession.close()
        DBSession.remove()
        testing.tearDown()

    def make_member_with_shares(self):
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
            shares1 = Shares(
                number=2,
                date_of_acquisition=date.today(),
                reference_code=u'ABCDEFGH',
                signature_received=True,
                signature_received_date=date(2014, 6, 7),
                payment_received=True,
                payment_received_date=date(2014, 6, 8),
                signature_confirmed=True,
                signature_confirmed_date=date(2014, 6, 8),
                payment_confirmed=True,
                payment_confirmed_date=date(2014, 6, 9),
                accountant_comment=u'no comment',
            )
            member1.shares = [shares1]
            shares2 = Shares(
                number=23,
                date_of_acquisition=date.today(),
                reference_code=u'IJKLMNO',
                signature_received=True,
                signature_received_date=date(2014, 1, 7),
                payment_received=True,
                payment_received_date=date(2014, 1, 8),
                signature_confirmed=True,
                signature_confirmed_date=date(2014, 1, 8),
                payment_confirmed=True,
                payment_confirmed_date=date(2014, 1, 9),
                accountant_comment=u'not connected',
            )

        DBSession.add(member1)
        DBSession.add(shares1)
        DBSession.add(shares2)

    def make_member_with_shares2(self):
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
            shares1 = Shares(
                number=2,
                date_of_acquisition=date.today(),
                reference_code=u'ABCDEFGH',
                signature_received=True,
                signature_received_date=date(2014, 6, 7),
                payment_received=True,
                payment_received_date=date(2014, 6, 8),
                signature_confirmed=True,
                signature_confirmed_date=date(2014, 6, 8),
                payment_confirmed=True,
                payment_confirmed_date=date(2014, 6, 9),
                accountant_comment=u'no comment',
            )
            member1.shares = [shares1]
        DBSession.add(member1)
        DBSession.add(shares1)

    def make_unconnected_shares(self):
        with transaction.manager:
            shares2 = Shares(
                number=23,
                date_of_acquisition=date.today(),
                reference_code=u'IJKLMNO',
                signature_received=True,
                signature_received_date=date(2014, 1, 7),
                payment_received=True,
                payment_received_date=date(2014, 1, 8),
                signature_confirmed=True,
                signature_confirmed_date=date(2014, 1, 8),
                payment_confirmed=True,
                payment_confirmed_date=date(2014, 1, 9),
                accountant_comment=u'not connected',
            )
        DBSession.add(shares2)

    def test_shares_detail(self):
        '''
        tests for the shares_detail view
        '''
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/shares_edit/1', status=403)
        assert('Access was denied to this resource' in res.body)
        res = self.testapp.get('/login', status=200)
        self.failUnless('login' in res.body)
        # try valid user
        form = res.form
        form['login'] = 'rut'
        form['password'] = 'berries'
        res2 = form.submit('submit', status=302)
        # # being logged in ...
        # print('>'*20)
        # print(res3.body)
        # print('<'*20)
        res3 = res2.follow()  # being redirected to dashboard with parameters
        self.failUnless(
            'Dashboard' in res3.body)
        # now look at a shares package
        res = self.testapp.get('/shares_detail/1', status=302)
        res2 = res.follow()
        # we were redirected to the menberships list
        # because the shares package did not exist
        self.assertTrue(
            'This shares id was not found in the database!' in res2.body)
        self.assertTrue('Toolbox' in res2.body)

        self.make_member_with_shares()

        # now look at a shares package
        res = self.testapp.get('/shares_detail/1', status=200)
        self.assertTrue('<h1>Details for Shares #1</h1>' in res.body)
        self.assertTrue('1: SomeFirstnäme SomeLastnäme' in res.body)
        self.assertTrue('ABCDEFGH' in res.body)

    def test_shares_edit(self):
        '''
        tests for the shares_edit view
        '''
        # unauthorized access must be prevented
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/shares_edit/1', status=403)
        assert('Access was denied to this resource' in res.body)
        res = self.testapp.get('/login', status=200)
        self.failUnless('login' in res.body)
        # try valid user
        form = res.form
        form['login'] = u'rut'
        form['password'] = u'berries'
        res2 = form.submit('submit', status=302)
        # # being logged in ...
        res3 = res2.follow()  # being redirected to dashboard with parameters
        self.failUnless('Dashboard' in res3.body)

        # no member in DB, so redirecting to dashboard
        res = self.testapp.get('/shares_edit/1', status=302)
        res2 = res.follow()

        self.make_member_with_shares()

        # now there is a member with shares in the DB
        #
        # lets try invalid input
        res = self.testapp.get('/shares_edit/foo', status=302)
        res2 = res.follow()
        self.failUnless('Dashboard' in res2.body)

        # now try valid id
        res = self.testapp.get('/shares_edit/1', status=200)
        self.failUnless('Edit Details for Shares' in res.body)

        # now we change details, really editing that member
        form = res.form

        if DEBUG:
            print "form.fields: {}".format(form.fields)

        self.assertTrue('2' in form['number'].value)
        self.assertTrue(datetime.today().strftime(
            '%Y-%m-%d') in form['date_of_acquisition'].value)
        # print(form['date_of_acquisition'].value)
        form['number'] = u'3'
        form['date_of_acquisition'] = u'2015-01-02'

        # try to submit now. this must fail,
        # because the date of birth is wrong
        # ... and other dates are missing
        res2 = form.submit('submit', status=200)

        # check data in DB
        _m1 = C3sMember.get_by_id(1)
        self.assertTrue(_m1.shares[0].number is 3)
        self.assertTrue(str(
            _m1.shares[0].date_of_acquisition) in str(datetime(2015, 1, 2)))

    def test_shares_delete(self):
        '''
        tests for the shares_delete view
        '''
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/shares_edit/1', status=403)
        assert('Access was denied to this resource' in res.body)
        res = self.testapp.get('/login', status=200)
        self.failUnless('login' in res.body)
        # try valid user
        form = res.form
        form['login'] = 'rut'
        form['password'] = 'berries'
        res2 = form.submit('submit', status=302)
        # # being logged in ...
        # print('>'*20)
        # print(res3.body)
        # print('<'*20)
        res3 = res2.follow()  # being redirected to dashboard with parameters
        self.failUnless(
            'Dashboard' in res3.body)

        self.make_member_with_shares()

        # now look at a shares package
        res = self.testapp.get('/shares_detail/1', status=200)
        self.assertTrue('<h1>Details for Shares #1</h1>' in res.body)
        self.assertTrue('1: SomeFirstnäme SomeLastnäme' in res.body)
        self.assertTrue('ABCDEFGH' in res.body)

        # try to delete a non-existing package
        res = self.testapp.get('/shares_delete/123', status=302)
        res2 = res.follow()
        self.assertTrue(
            'This shares package 123 was not found in the DB.' in res2.body)

        # try to delete an existing package
        res = self.testapp.get('/shares_delete/1', status=302)
        res2 = res.follow()
        self.assertTrue(
            'This shares package 1 still has a member owning it.' in res2.body)
        res = self.testapp.get('/delete/1', status=302)
        res2 = res.follow()

        res = self.testapp.get('/shares_detail/1', status=200)
        self.assertTrue('<h1>Details for Shares #1</h1>' in res.body)
        # self.assertTrue('1: Not Found' in res.body)
        self.assertTrue('ABCDEFGH' in res.body)
