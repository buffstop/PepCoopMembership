#!/bin/env/python
# -*- coding: utf-8 -*-

import unittest
from pyramid import testing

from c3smembership.models import (
    DBSession,
    Base,
    C3sMember,
    C3sStaff,
    Group,
)
from sqlalchemy import engine_from_config
import transaction
from datetime import date


class NewMemberTests(unittest.TestCase):
    """
    test creation of a new member by staff

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
        # self.session = DBSession()
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
            except:
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

    def test_add_member(self):
        '''
        tests for the new_member view
        '''
        # unauthorized access must be prevented
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/new_member', status=403)
        assert('Access was denied to this resource' in res.body)
        # so login first
        res = self.testapp.get('/login', status=200)
        self.failUnless('login' in res.body)
        # try valid user
        form = res.form
        form['login'] = 'rut'
        form['password'] = 'berries'
        res2 = form.submit('submit', status=302)
        # # being logged in ...
        res3 = res2.follow()  # being redirected to dashboard_only
        self.failUnless(
            'Dashboard' in res3.body)
        # # now that we are logged in,
        # # the login view should redirect us to the dashboard
        # res5 = self.testapp.get('/login', status=302)
        # # so yes: that was a redirect
        # res6 = res5.follow()
        # res6 = res6.follow()
        # # print(res4.body)
        # self.failUnless(
        #     'Dashboard' in res6.body)
        # # choose number of applications shown
        # res6a = self.testapp.get(
        #     '/dashboard',
        #     status=302,
        #     extra_environ={
        #         'num_display': '30',
        #     }
        # )
        # res6a = res6a.follow()

        # no member with id=1 in DB
        res = self.testapp.get('/new_member?id=1', status=200)

        form = res.form
        # print form.fields
        form['firstname'] = u'SomeFirstname'
        form['lastname'] = u'SomeLastname'
        form['email'] = u'some@shri.de'
        form['address1'] = u"addr one"
        form['address2'] = u"addr two"
        form['postcode'] = u"12345"
        form['city'] = u"Footown Meeh"
        form['country'].value__set(u"DE")
        form['_LOCALE_'] = u"DE"
        form['date_of_birth'] = '1014-01-01'  # date.today(),
        # form['email_is_confirmed=False,
        # email_confirm_code=u'ABCDEFGFOO',
        # password=u'arandompassword',
        # date_of_submission=date.today(),
        # form['membership_type'] = u'normal',
        form['entity_type'].value__set(u'person')
        form['membership_type'].value__set(u'normal')
        # form['other_colsoc'] = (u'no',),
        form['other_colsoc'].value__set(u'no')

        form['name_of_colsoc'] = u"GEMA"
        form['num_shares'] = u'23'

        # try to submit the form (knowing that the date is missing)
        res2 = form.submit(u'submit', status=200)
        form2 = res2.form
        # set the date to a usefull/allowed value
        form2['date_of_birth'] = u'1999-09-19'
        res3 = form2.submit(u'submit', status=302)
        res4 = res3.follow()
        # print res4
        self.assertTrue('Details for Member Application #1' in res4.body)

        # more asserts
        self.assertTrue('SomeFirstname' in res4.body)
        self.assertTrue('SomeLastname' in res4.body)
        self.assertTrue('some@shri.de' in res4.body)
        self.assertTrue('addr one' in res4.body)
        self.assertTrue('addr two' in res4.body)
        self.assertTrue('12345' in res4.body)
        self.assertTrue('' in res4.body)
        self.assertTrue('DE' in res4.body)
        self.assertTrue('normal' in res4.body)
        self.assertTrue('23' in res4.body)
        #        self.assertTrue('' in res3.body)
        #        self.assertTrue('' in res3.body)
        #        self.assertTrue('' in res3.body)
        #        self.assertTrue('' in res3.body)

        # now, there is a member with id=1 in DB
        res = self.testapp.get('/new_member?id=1', status=200)

        form = res.form
        # print form.fields
        form['firstname'] = u'SomeFirstname'
        form['lastname'] = u'SomeLastname'
        form['email'] = u'some@shri.de'
        form['address1'] = u"addr one"
        form['address2'] = u"addr two"
        form['postcode'] = u"12345"
        form['city'] = u"Footown Meeh"
        form['country'].value__set(u"DE")
        form['_LOCALE_'] = u"DE"
        form['date_of_birth'] = date.today()
        # form['email_is_confirmed=False,
        # email_confirm_code=u'ABCDEFGFOO',
        # password=u'arandompassword',
        # date_of_submission=date.today(),
        form['entity_type'] = u'person'
        form['membership_type'] = u'normal'
        # form['membership_type'].value__set(u'normal')
        # form['other_colsoc'] = (u'no',),
        form['other_colsoc'].value__set(u'no')

        form['name_of_colsoc'] = u"GEMA"
        form['num_shares'] = u'23'

        # try to submit the form (knowing that the date is missing)
        res2 = form.submit(u'submit', status=200)
        form2 = res2.form
        form2['date_of_birth'] = u'1999-09-19'
        res3 = form2.submit(u'submit', status=302)
        res4 = res3.follow()
        # print res4
        self.assertTrue('Details for Member Application #2' in res4.body)

        # more asserts
        self.assertTrue('SomeFirstname' in res4.body)
        self.assertTrue('SomeLastname' in res4.body)
        self.assertTrue('some@shri.de' in res4.body)
        self.assertTrue('addr one' in res4.body)
        self.assertTrue('addr two' in res4.body)
        self.assertTrue('12345' in res4.body)
        self.assertTrue('' in res4.body)
        self.assertTrue('DE' in res4.body)
        self.assertTrue('normal' in res4.body)
        self.assertTrue('23' in res4.body)

        # no member with id=1 in DB
        res = self.testapp.get('/new_member', status=200)

        form = res.form
        # print form.fields
        form['firstname'] = u'SomeFirstname'
        form['lastname'] = u'SomeLastname'
        form['email'] = u'some@shri.de'
        form['address1'] = u"addr one"
        form['address2'] = u"addr two"
        form['postcode'] = u"12345"
        form['city'] = u"Footown Meeh"
        form['country'].value__set(u"DE")
        form['_LOCALE_'] = u"DE"
        form['date_of_birth'] = date.today()
        # form['email_is_confirmed=False,
        # email_confirm_code=u'ABCDEFGFOO',
        # password=u'arandompassword',
        # date_of_submission=date.today(),
        form['entity_type'] = u'person'
        form['membership_type'] = u'normal'
        # form['deformField14'].value__set(u'normal')
        # form['other_colsoc'] = (u'no',),
        form['other_colsoc'].value__set(u'no')

        form['name_of_colsoc'] = u"GEMA"
        form['num_shares'] = u'23'

        # try to submit the form (knowing that the date is missing)
        res2 = form.submit(u'submit', status=200)
        form2 = res2.form
        form2['date_of_birth'] = u'1999-09-19'

        res3 = form2.submit(u'submit', status=302)
        res4 = res3.follow()
        # print res4
        self.assertTrue('Details for Member Application #3' in res4.body)

        # more asserts
        self.assertTrue('SomeFirstname' in res4.body)
        self.assertTrue('SomeLastname' in res4.body)
        self.assertTrue('some@shri.de' in res4.body)
        self.assertTrue('addr one' in res4.body)
        self.assertTrue('addr two' in res4.body)
        self.assertTrue('12345' in res4.body)
        self.assertTrue('' in res4.body)
        self.assertTrue('DE' in res4.body)
        self.assertTrue('normal' in res4.body)
        self.assertTrue('23' in res4.body)

        # check the number of entries in the DB
        num = C3sMember.get_number()
        # print num
        self.assertTrue(num == 3)

        '''
        now add a legal entity / aka Körperschaft
        '''
        res = self.testapp.get('/new_member', status=200)

        form = res.form
        # print form.fields
        form['firstname'] = u'SomeLegalentity'
        form['lastname'] = u'SomeLegalName'
        form['email'] = u'some@shri.de'
        form['address1'] = u"addr one"
        form['address2'] = u"addr two"
        form['postcode'] = u"12345"
        form['city'] = u"Footown Meeh"
        form['country'].value__set(u"DE")
        form['_LOCALE_'] = u"DE"
        form['date_of_birth'] = date.today()
        # form['email_is_confirmed=False,
        # email_confirm_code=u'ABCDEFGFOO',
        # password=u'arandompassword',
        # date_of_submission=date.today(),
        form['entity_type'] = u'legalentity'
        form['membership_type'] = u'investing'
        # form['deformField14'].value__set(u'normal')
        # form['other_colsoc'] = (u'no',),
        form['other_colsoc'].value__set(u'no')

        form['name_of_colsoc'] = u""
        form['num_shares'] = u'42'

        # try to submit the form (knowing that the date is missing)
        res2 = form.submit(u'submit', status=200)
        form2 = res2.form
        form2['date_of_birth'] = u'1999-09-19'

        res3 = form2.submit(u'submit', status=302)
        res4 = res3.follow()
        # print res4
        self.assertTrue('Details for Member Application #4' in res4.body)

        # more asserts
        self.assertTrue('SomeLegalentity' in res4.body)
        self.assertTrue('SomeLegalName' in res4.body)
        self.assertTrue('some@shri.de' in res4.body)
        self.assertTrue('addr one' in res4.body)
        self.assertTrue('addr two' in res4.body)
        self.assertTrue('12345' in res4.body)
        self.assertTrue('' in res4.body)
        self.assertTrue('DE' in res4.body)
        self.assertTrue('investing' in res4.body)
        self.assertTrue('23' in res4.body)

        # check the number of entries in the DB
        num = C3sMember.get_number()
        # print num
        self.assertTrue(num == 4)
