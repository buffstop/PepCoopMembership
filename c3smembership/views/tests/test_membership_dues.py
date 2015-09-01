# -*- coding: utf-8 -*-

from datetime import (
    date,
    datetime)
# from pyramid.config import Configurator
from pyramid import testing
from sqlalchemy import engine_from_config
import transaction
import unittest

from c3smembership.models import (
    Base,
    C3sMember,
    DBSession,
    Dues15Invoice,
)


def _initTestingDB():
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
            locale=u"de",
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
        member2 = C3sMember(  # english
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
            email_confirm_code=u'ABCDEFGBAR',
            password=u'arandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'2',
        )
        founding_member3 = C3sMember(  # english
            firstname=u'BBBSomeFirstnäme',
            lastname=u'YYYSomeLastnäme',
            email=u'some3@shri.de',
            address1=u"addr one",
            address2=u"addr two",
            postcode=u"12345",
            city=u"Footown Mäh",
            country=u"Foocountry",
            locale=u"en",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'ABCBARdungHH_',
            password=u'anotherrandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'2',
        )
        member4 = C3sMember(  # german investing
            firstname=u'AAASomeFirstnäme4',
            lastname=u'XXXSomeLastnäme4',
            email=u'some4@shri.de',
            address1=u"addr one4",
            address2=u"addr two4",
            postcode=u"12344",
            city=u"Footown M44",
            country=u"Foocountr4",
            locale=u"de",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'ABCDEFGBA4',
            password=u'arandompasswor4',
            date_of_submission=date.today(),
            membership_type=u'investing',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'60',
        )
        member5 = C3sMember(  # english investing
            firstname=u'AAASomeFirstnäme5',
            lastname=u'XXXSomeLastnäme5',
            email=u'some5@shri.de',
            address1=u"aone5",
            address2=u"atwo5",
            postcode=u"12355",
            city=u"Footown M45",
            country=u"Foocountr5",
            locale=u"en",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'ABCDEFGBA5',
            password=u'arandompasswor5',
            date_of_submission=date.today(),
            membership_type=u'investing',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'60',
        )
        DBSession.add(member1)
        DBSession.add(member2)
        DBSession.add(founding_member3)
        DBSession.add(member4)
        DBSession.add(member5)

    return DBSession


class TestViews(unittest.TestCase):
    """
    very basic tests for the main views
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        self.config.registry.settings[
            'c3smembership.url'] = 'https://yes.c3s.cc'
        self.config.registry.settings['c3smembership.mailaddr'] = 'c@c3s.cc'
        self.config.registry.settings['testing.mail_to_console'] = 'false'

        DBSession.remove()
        self.session = _initTestingDB()

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_random_string(self):
        from c3smembership.views.membership_dues import make_random_string
        res = make_random_string()
        assert len(res) == 10

    def test_calculate_partial_dues(self):
        from c3smembership.views.membership_dues import calculate_partial_dues
        member = C3sMember.get_by_id(1)
        res = calculate_partial_dues(member)
        # print res
        # print member.membership_date
        assert res == (u'ganzes Jahr', '50')

        # english member
        member_en = C3sMember.get_by_id(2)
        res = calculate_partial_dues(member_en)
        # print res
        assert res == (u'whole year', '50')

        member_en.membership_date = datetime(2015, 6, 1)
        res = calculate_partial_dues(member_en)
        # print res
        assert res == (u'from 2nd quarter', '37,50')

        member_en.membership_date = datetime(2015, 9, 1)
        res = calculate_partial_dues(member_en)
        # print res
        assert res == (u'from 3rd quarter', '25')

        member_en.membership_date = datetime(2015, 11, 1)
        res = calculate_partial_dues(member_en)
        # print res
        assert res == (u'from 4th quarter', '12,50')

    def test_send_dues_invoice_email_via_HTTP(self):
        """
        test the send_dues_invoice_email view
        """
        from pyramid_mailer import get_mailer
        from c3smembership.views.membership_dues import send_dues_invoice_email
        from c3smembership.models import Dues15Invoice

        _number_of_invoices = len(Dues15Invoice.get_all())

        self.config.add_route('toolbox', '/')
        self.config.add_route('detail', '/')
        self.config.add_route('make_dues_invoice_no_pdf', '/')

        req = testing.DummyRequest()
        req.matchdict = {
            'member_id': '1',
        }
        req.referrer = 'detail'
        res = send_dues_invoice_email(req)
        self.assertTrue(res.status_code == 302)
        self.assertTrue('http://example.com/' in res.headers['Location'])
        # member 1 not accepted by the board. problem!

        _number_of_invoices_2 = len(Dues15Invoice.get_all())
        assert(_number_of_invoices == _number_of_invoices_2)
        # print("_number_of_invoices: {}".format(_number_of_invoices))

        m1 = C3sMember.get_by_id(1)
        m1.membership_accepted = True

        res = send_dues_invoice_email(req)
        # print('#'*60)
        # print res
        # print('#'*60)

        _number_of_invoices_3 = len(Dues15Invoice.get_all())
        # print("_number_of_invoices 3: {}".format(_number_of_invoices_3))
        assert(_number_of_invoices_3 == 1)

        # check for outgoing email
        mailer = get_mailer(req)
        # print mailer
        # print mailer.outbox
        self.assertEqual(len(mailer.outbox), 1)
        # print mailer.outbox[0].body
        self.assertTrue(
            'Verwendungszweck: C3S-dues2015-0001' in mailer.outbox[0].body)

        """
        now we try to get an id that does not exist
        """
        req2 = testing.DummyRequest()
        req2.matchdict = {
            'member_id': '1234',
        }
        req2.referrer = 'detail'
        res2 = send_dues_invoice_email(req2)
        self.assertTrue(res2.status_code == 302)
        self.assertTrue('http://example.com/' in res2.headers['Location'])

        """
        what if we call that function (and send email) twice?
        can we test that no second invoice is created in DB?
        """
        req3 = testing.DummyRequest()
        req3.matchdict = {
            'member_id': '1',
        }
        req3.referrer = 'detail'
        res3 = send_dues_invoice_email(req3)
        self.assertTrue(res3.status_code == 302)
        self.assertTrue('http://example.com/' in res3.headers['Location'])

    def test_send_dues_invoice_email_via_BATCH(self):
        """
        test the send_dues_invoice_batch function
        for batch processing
        """
        # from pyramid_mailer import get_mailer
        from c3smembership.views.membership_dues import send_dues_invoice_batch
        self.config.add_route('make_dues_invoice_no_pdf', '/')
        self.config.add_route('detail', '/detail/')
        self.config.add_route('error_page', '/error_page')
        self.config.add_route('toolbox', '/toolbox')

        # have to accept their membersip first
        m1 = C3sMember.get_by_id(1)
        m1.membership_accepted = True
        m2 = C3sMember.get_by_id(2)
        m2.membership_accepted = True
        m3 = C3sMember.get_by_id(3)
        m3.membership_accepted = True
        m4 = C3sMember.get_by_id(4)
        m4.membership_accepted = True
        m5 = C3sMember.get_by_id(5)
        m5.membership_accepted = True

        req = testing.DummyRequest()
        req.referrer = 'detail'
        res = send_dues_invoice_batch(req)
        # print res

        # check number of invoices
        _number_of_invoices_4 = len(Dues15Invoice.get_all())
        # print("_number_of_invoices_4: {}".format(_number_of_invoices_4))
        assert(_number_of_invoices_4 == 5)

        # try to post a number for batch processing
        req_post = testing.DummyRequest(
            post={
                'submit': True,
                'number': 24
                # lots of values missing
            },
        )

        res = send_dues_invoice_batch(req_post)
        assert(
            'sent out 5 mails (to members with ids [1, 2, 3, 4, 5])' in
            req.session.pop_flash('message_to_staff'))

        """
        and now some tests for make_dues_invoice_no_pdf
        """
        from c3smembership.views.membership_dues import (
            make_dues_invoice_no_pdf)
        req2 = testing.DummyRequest()

        # wrong token: must fail!
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token + 'false!!!',  # must fail
            'i': '0001',
        }
        res = make_dues_invoice_no_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        # wrong invoice number: must fail!
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token,
            'i': '1234',  # must fail
        }
        res = make_dues_invoice_no_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        # wrong invoice token: must fail!
        i3 = Dues15Invoice.get_by_invoice_no(3)
        i3.token = 'not_matching'
        req2.matchdict = {
            'email': m3.email,
            'code': m3.dues15_token,
            'i': '3',  # must fail
        }
        res = make_dues_invoice_no_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        # retry with valid token:
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token,
            'i': '0001',
        }
        res = make_dues_invoice_no_pdf(req2)
        # m1.
        # print("length of the result: {}".format(len(res.body)))
        # print("headers of the result: {}".format((res.headers)))
        assert(60000 < len(res.body) < 80000)
        assert('application/pdf' in res.headers['Content-Type'])

        """
        test dues listing
        """
        from c3smembership.views.membership_dues import dues15_listing
        req_list = testing.DummyRequest()
        resp_list = dues15_listing(req_list)
        # print resp_list
        # {'count': 5,
        #   'invoices': [
        #       <c3smembership.models.Dues15Invoice object at 0x7f95df761a50>,
        #       <c3smembership.models.Dues15Invoice object at 0x7f95df761690>,
        #       <c3smembership.models.Dues15Invoice object at 0x7f95df815a50>,
        #       <c3smembership.models.Dues15Invoice object at 0x7f95df761c90>,
        #       <c3smembership.models.Dues15Invoice object at 0x7f95df761c10>],
        #   '_today': datetime.date(2015, 9, 1)}
        assert(resp_list['count'] == 5)

        """
        test reduction of dues
        """
        # req_detail1 = testing.DummyRequest()
        # req_detail1.matchdict['memberid'] = 1
        # from c3smembership.accountants_views import member_detail
        # resp_detail1 = member_detail(req_detail1)
        # print('#'*60)
        # print resp_detail1
        # print('#'*60)

        _m1_amount_reduced = m1.dues15_amount_reduced
        _number_of_invoices_before_reduction = len(Dues15Invoice.get_all())
        from c3smembership.views.membership_dues import dues15_reduce
        req_reduce = testing.DummyRequest(
            post={
                'submit': True,
                'amount': 42
                # lots of values missing
            },
        )
        req_reduce.matchdict['member_id'] = 1
        res_reduce = dues15_reduce(req_reduce)
        _number_of_invoices_after_reduction = len(Dues15Invoice.get_all())
        assert(  # two new invoices must have been issued
            (_number_of_invoices_before_reduction + 2)
            == _number_of_invoices_after_reduction)
        assert(_number_of_invoices_after_reduction == 7)
        assert('detail' in res_reduce.headers['Location'])  # 302 to detail p.
        assert(_m1_amount_reduced != m1.dues15_amount_reduced)  # changed!
        assert(m1.dues15_amount_reduced == 42)  # changed to 42!

        """
        test reversal invoice PDF generation
        """

        from c3smembership.views.membership_dues import (
            make_reversal_invoice_pdf)
        req2 = testing.DummyRequest()

        # wrong token: must fail!
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token + 'false!!!',  # must fail
            'no': '0006',
        }
        res = make_reversal_invoice_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        # wrong invoice number: must fail!
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token,
            'no': '1234',  # must fail
        }
        res = make_reversal_invoice_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        # wrong invoice token: must fail!
        i3 = Dues15Invoice.get_by_invoice_no(3)
        i3.token = 'not_matching'
        req2.matchdict = {
            'email': m3.email,
            'code': m3.dues15_token,
            'no': '3',  # must fail
        }
        res = make_reversal_invoice_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        # retry with valid token:
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token,
            'no': '0001',
        }
        res = make_reversal_invoice_pdf(req2)
        # m1.
        # print("length of the result: {}".format(len(res.body)))
        # print("headers of the result: {}".format((res.headers)))
        assert(60000 < len(res.body) < 80000)
        assert('application/pdf' in res.headers['Content-Type'])
