#!/bin/env/python
# -*- coding: utf-8 -*-
"""
Tests for c3smembership.edit_member
"""

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
from c3smembership import main
from webtest import TestApp

DEBUG = False


class EditMemberTests(unittest.TestCase):
    """
    these tests are functional tests to check functionality of the whole app
    (i.e. integration tests)
    they also serve to get coverage for 'main'
    """
    def setUp(self):
        """
        Setup test cases
        """
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.close()
            DBSession.remove()
        except:
            pass
        my_settings = {
            'sqlalchemy.url': 'sqlite:///:memory:',
            'available_languages': 'da de en es fr',
            'c3smembership.dashboard_number': '30'}
        engine = engine_from_config(my_settings)
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

        #self._insert_members()

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
                pass

        app = main({}, **my_settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        """
        Tear down all test cases
        """
        DBSession.close()
        DBSession.remove()
        testing.tearDown()

    def create_membership_applicant(self):
        """
        Create and return a membership applicant
        """
        member = None
        with transaction.manager:
            member = C3sMember(  # german
                firstname=u'SomeFirstnäme',
                lastname=u'Membership Applicant',
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
        return member

    def test_edit_members(self):
        '''
        tests for the edit_member view
        '''
        # unauthorized access must be prevented
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/edit/1', status=403)
        self.failUnless('Access was denied to this resource' in res.body)

        self.login()

        # no member in DB, so redirecting to dashboard
        res = self.testapp.get('/edit/1', status=302)
        self.validate_dashboard_redirect(res)

        DBSession.add(self.create_membership_applicant())
        DBSession.flush()

        # now there is a member in the DB
        # let's try invalid input
        res = self.testapp.get('/edit/foo', status=302)
        self.validate_dashboard_redirect(res)

        # now try valid id
        res = self.testapp.get('/edit/1', status=200)
        self.failUnless('Mitglied bearbeiten' in res.body)

        # now we change details, really editing that member
        form = res.form

        if DEBUG:
            print "form.fields: {}".format(form.fields)

        self.assertTrue(u'SomeFirstn\xe4me' in form['firstname'].value)

        form['firstname'] = 'EinVorname'
        form['lastname'] = 'EinNachname'
        form['email'] = 'info@c3s.cc'
        form['address1'] = 'adressteil 1'
        form['address2'] = 'adressteil 2'
        form['postcode'] = '12346'
        form['city'] = 'die city'
        form['country'] = 'FI'
        form['membership_type'] = 'investing'
        form['other_colsoc'] = 'no'
        form['name_of_colsoc'] = ''
        form['num_shares'] = 42

        # try to submit now. this must fail, because the date of birth is
        # wrong ... and other dates are missing
        res2 = form.submit('submit', status=200)
        self.assertTrue('is later than latest date 2000-01-01' in res2.body)
        self.assertTrue('EinVorname' in res2.body)

        # set the date correctly
        form2 = res2.form
        form2['date_of_birth'] = '1999-12-30'
        form2['membership_date'] = '2013-09-24'
        form2['signature_received_date'] = '2013-09-24'
        form2['payment_received_date'] = '2013-09-24'

        # submit again
        res2 = form2.submit('submit', status=302)
        res3 = res2.follow()
        self.validate_details_page(res3)
        self.assertTrue('EinNachname' in res3.body)
        self.assertTrue('info@c3s.cc' in res3.body)
        self.assertTrue('adressteil 1' in res3.body)
        self.assertTrue('adressteil 2' in res3.body)
        self.assertTrue('12346' in res3.body)
        self.assertTrue('die city' in res3.body)
        self.assertTrue('FI' in res3.body)
        self.assertTrue('investing' in res3.body)
        self.assertTrue('42' in res3.body)

        # edit again ... changing membership acceptance status
        res = self.testapp.get('/edit/1', status=200)
        self.failUnless('Mitglied bearbeiten' in res.body)

        # now we change details, really editing that member
        form = res.form
        if DEBUG:
            print "form.fields: {}".format(form.fields)

        form2['membership_accepted'] = True
        res2 = form2.submit('submit', status=302)
        res2.follow()

    def validate_details_page(self, res):
        """
        Validate that the resource in res is the details page
        """
        self.assertTrue('<h1>Details for' in res.body)

    def login(self):
        """
        Log into the membership backend
        """
        res = self.testapp.get('/login', status=200)
        self.failUnless('login' in res.body)
        form = res.form
        form['login'] = 'rut'
        form['password'] = 'berries'
        res = form.submit('submit', status=302)
        # being logged in ...
        self.validate_dashboard_redirect(res)

    def validate_dashboard_redirect(self, res):
        """
        Validate that res is redirecting to the dashboard
        """
        res = res.follow()  # being redirected to dashboard_only
        res = res.follow()  # being redirected to dashboard with parameters
        self.validate_dashboard(res)

    def validate_dashboard(self, res):
        """
        Validate that res is the dashboard
        """
        self.failUnless('Dashboard' in res.body)
