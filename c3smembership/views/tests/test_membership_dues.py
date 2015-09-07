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
        normal_de = C3sMember(  # german normal
            firstname=u'Ada Musiziert',
            lastname=u'Traumhaft ÄÖÜ',
            email=u'devNull@c3s.cc',
            address1=u"ada addr one",
            address2=u"ada addr two",
            postcode=u"12345",
            city=u"Foostadt Ada",
            country=u"Foocountry",
            locale=u"de",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'NORMAL_DE1',
            password=u'adasrandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'23',
        )
        normal_en = C3sMember(  # english normal
            firstname=u'James',
            lastname=u'Musician',
            email=u'dummy@c3s.cc',
            address1=u"james addr 1",
            address2=u"james appartment 2",
            postcode=u"12345",
            city=u"Jamestown",
            country=u"Jamescountry",
            locale=u"en",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'NORMAL_DE',
            password=u'jamesrandompassword',
            date_of_submission=date.today(),
            membership_type=u'normal',
            member_of_colsoc=True,
            name_of_colsoc=u"",
            num_shares=u'2',
        )
        investing_de = C3sMember(  # german investing
            firstname=u'Herman',
            lastname=u'Investorius',
            email=u'dummy@c3s.cc',
            address1=u"addr one4",
            address2=u"addr two4",
            postcode=u"12344",
            city=u"Footown M44",
            country=u"Foocountr4",
            locale=u"de",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'INVESTING_DE',
            password=u'arandompasswor4',
            date_of_submission=date.today(),
            membership_type=u'investing',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'60',
        )
        investing_en = C3sMember(  # english investing
            firstname=u'Britany',
            lastname=u'Investing',
            email=u'dummy@c3s.cc',
            address1=u"aone5",
            address2=u"atwo5",
            postcode=u"12355",
            city=u"Footown M45",
            country=u"Foocountr5",
            locale=u"en",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'INVESTING_EN',
            password=u'arandompasswor5',
            date_of_submission=date.today(),
            membership_type=u'investing',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'60',
        )
        legal_entity_de = C3sMember(  # english investing legal entity
            firstname=u'Deutscher',
            lastname=u'Musikverlag',
            email=u'verlag@compa.ny',
            address1=u"foo bulevard",
            address2=u"123-345",
            postcode=u"98765",
            city=u"Foo",
            country=u"Bar",
            locale=u"en",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'VERLAG_DE',
            password=u'arandompasswor6',
            date_of_submission=date.today(),
            membership_type=u'investing',
            member_of_colsoc=False,
            name_of_colsoc=u"",
            num_shares=u'60',
        )
        legal_entity_en = C3sMember(  # english investing legal entity
            firstname=u'Francoise',
            lastname=u'Company',
            email=u'foo@compa.ny',
            address1=u"foo bulevard",
            address2=u"123-345",
            postcode=u"98765",
            city=u"Foo",
            country=u"Bar",
            locale=u"en",
            date_of_birth=date.today(),
            email_is_confirmed=False,
            email_confirm_code=u'COMPANY_EN',
            password=u'arandompasswor6',
            date_of_submission=date.today(),
            membership_type=u'investing',
            member_of_colsoc=False,
            name_of_colsoc=u"",
            num_shares=u'60',
        )
        DBSession.add(normal_de)
        DBSession.add(normal_en)
        DBSession.add(investing_de)
        DBSession.add(investing_en)
        DBSession.add(legal_entity_en)
        DBSession.add(legal_entity_de)

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

    def test_calculate_partial_dues15(self):
        from c3smembership.views.membership_dues import (
            calculate_partial_dues15)
        member = C3sMember.get_by_id(1)
        res = calculate_partial_dues15(member)
        # print res
        # print member.membership_date
        assert res == (u'q1_2015', '50')

        # english member
        member_en = C3sMember.get_by_id(2)
        res = calculate_partial_dues15(member_en)
        # print res
        assert res == (u'q1_2015', '50')

        member_en.membership_date = datetime(2015, 6, 1)
        res = calculate_partial_dues15(member_en)
        # print res
        assert res == (u'q2_2015', '37,50')

        member_en.membership_date = datetime(2015, 9, 1)
        res = calculate_partial_dues15(member_en)
        # print res
        assert res == (u'q3_2015', '25')

        member_en.membership_date = datetime(2015, 11, 1)
        res = calculate_partial_dues15(member_en)
        # print res
        assert res == (u'q4_2015', '12,50')

    def test_string_start_quarter(self):
        from c3smembership.views.membership_dues import (
            string_start_quarter)
        member = C3sMember.get_by_id(1)

        member.dues15_start = 'q1_2015'
        res = string_start_quarter(member)
        # print res
        assert('Quartal 1' in res)
        member.dues15_start = 'q2_2015'
        res = string_start_quarter(member)
        # print res
        assert('Quartal 2' in res)
        member.dues15_start = 'q3_2015'
        res = string_start_quarter(member)
        # print res
        assert('Quartal 3' in res)
        member.dues15_start = 'q4_2015'
        res = string_start_quarter(member)
        # print res
        assert('Quartal 4' in res)

        member.locale = u'en'
        member.dues15_start = 'q1_2015'
        res = string_start_quarter(member)
        # print res
        assert('1st quarter' in res)
        member.dues15_start = 'q2_2015'
        res = string_start_quarter(member)
        # print res
        assert('2nd quarter' in res)
        member.dues15_start = 'q3_2015'
        res = string_start_quarter(member)
        # print res
        assert('3rd quarter' in res)
        member.dues15_start = 'q4_2015'
        res = string_start_quarter(member)
        # print res
        assert('4th quarter' in res)

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
        self.config.add_route('make_reversal_invoice_pdf', '/')
        self.config.add_route('detail', '/detail/')
        self.config.add_route('error_page', '/error_page')
        self.config.add_route('toolbox', '/toolbox')

        # have to accept their membersip first
        m1 = C3sMember.get_by_id(1)  # normal member
        m1.membership_accepted = True
        m2 = C3sMember.get_by_id(2)  # normal member
        m2.membership_accepted = True
        m3 = C3sMember.get_by_id(3)  # normal member
        m3.membership_accepted = True
        m4 = C3sMember.get_by_id(4)  # investing member
        m4.membership_accepted = True
        m5 = C3sMember.get_by_id(5)  # investing member
        m5.membership_accepted = True

        # check number of invoices: should be 0
        _number_of_invoices_before_batch = len(Dues15Invoice.get_all())
        # print("_number_of_invoices_before_batch: {}".format(
        #    _number_of_invoices_before_batch))
        assert(_number_of_invoices_before_batch == 0)

        req = testing.DummyRequest()
        req.referrer = 'detail'
        res = send_dues_invoice_batch(req)
        # print res

        # check number of invoices: should be 3
        _number_of_invoices_batch = len(Dues15Invoice.get_all())
        # print("number of invoices after batch: {}".format(
        #    _number_of_invoices_batch))
        assert(_number_of_invoices_batch == 2)

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
            'i': u'0001',
        }

        res = make_dues_invoice_no_pdf(req2)

        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        # wrong invoice number: must fail!
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token,
            'i': u'1234',  # must fail
        }
        res = make_dues_invoice_no_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        # wrong invoice token: must fail!
        i2 = Dues15Invoice.get_by_invoice_no(2)
        i2.token = u'not_matching'
        req2.matchdict = {
            'email': m2.email,
            'code': m2.dues15_token,
            'i': u'3',  # must fail
        }
        res = make_dues_invoice_no_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        #######################################################################
        # one more edge case:
        # check _inv.token must match code, or else!!!
        # first, set inv_code to something wrong:
        i1 = Dues15Invoice.get_by_invoice_no(1)
        _old_i1_token = i1.token
        i1.token = u'not_right'
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token,
            'i': u'0001',
        }
        res = make_dues_invoice_no_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error
        # reset it to what was there before
        i1.token = _old_i1_token
        #######################################################################
        # one more edge case:
        # check this invoice is not a reversal, or else no PDF!!!
        # first, set is_reversal to something wrong:
        i1 = Dues15Invoice.get_by_invoice_no(1)
        _old_i1_reversal_status = i1.is_reversal  # False
        i1.is_reversal = True
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token,
            'i': u'0001',
        }
        res = make_dues_invoice_no_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error
        # reset it to what was there before
        i1.is_reversal = _old_i1_reversal_status
        #######################################################################

        # retry with valid token:
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token,
            'i': u'0001',
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
        assert(resp_list['count'] == 2)

        """
        test reduction of dues
        """
        _m1_amount_reduced = m1.dues15_amount_reduced
        _number_of_invoices_before_reduction = len(Dues15Invoice.get_all())
        from c3smembership.views.membership_dues import dues15_reduce

        # try to reduce to the given default amount (edge case coverage)
        req_reduce = testing.DummyRequest(
            post={
                'submit': True,
                'amount': 50,
                # lots of values missing
            },
        )
        req_reduce.matchdict['member_id'] = 1
        res_reduce = dues15_reduce(req_reduce)

        # now try a valid reduction
        req_reduce = testing.DummyRequest(
            post={
                'submit': True,
                'amount': 42,
                # lots of values missing
            },
        )
        req_reduce.matchdict['member_id'] = 1
        res_reduce = dues15_reduce(req_reduce)
        _number_of_invoices_after_reduction = len(Dues15Invoice.get_all())
        assert(  # two new invoices must have been issued
            (_number_of_invoices_before_reduction + 2)
            == _number_of_invoices_after_reduction)
        assert(_number_of_invoices_after_reduction == 4)
        assert('detail' in res_reduce.headers['Location'])  # 302 to detail p.
        assert(_m1_amount_reduced != m1.dues15_amount_reduced)  # changed!
        assert(m1.dues15_amount_reduced == 42)  # changed to 42!

        #############################################################
        # try to reduce to the same amount again (edge case coverage)
        req_reduce = testing.DummyRequest(
            post={
                'submit': True,
                'amount': 42,
                # lots of values missing
            },
        )
        req_reduce.matchdict['member_id'] = 1
        res_reduce = dues15_reduce(req_reduce)
        #############################################################
        # try to reduce to zero (edge case coverage)
        req_reduce = testing.DummyRequest(
            post={
                'submit': True,
                'amount': 0,
                # lots of values missing
            },
        )
        req_reduce.matchdict['member_id'] = 1
        res_reduce = dues15_reduce(req_reduce)
        #############################################################
        # try to reduce to zero with english member (edge case coverage)
        # how to do this if you already reduced to zero? reduce to more first!
        req_reduce = testing.DummyRequest(
            post={
                'submit': True,
                'amount': 1,
                # lots of values missing
            },
        )
        req_reduce.matchdict['member_id'] = 1
        res_reduce = dues15_reduce(req_reduce)
        m1.locale = u'en'
        req_reduce = testing.DummyRequest(
            post={
                'submit': True,
                'amount': 0,
                # lots of values missing
            },
        )
        req_reduce.matchdict['member_id'] = 1
        res_reduce = dues15_reduce(req_reduce)
        #############################################################
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
            'no': u'0006',
        }
        res = make_reversal_invoice_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        # wrong invoice number: must fail!
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token,
            'no': u'1234',  # must fail
        }
        res = make_reversal_invoice_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        # wrong invoice token: must fail!
        i2 = Dues15Invoice.get_by_invoice_no('2')
        i2.token = u'not_matching'
        req2.matchdict = {
            'email': m2.email,
            'code': m2.dues15_token,
            'no': u'2',  # must fail
        }
        res = make_reversal_invoice_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error

        ######################################################################
        # wrong invoice type (not a reversal): must fail! (edge case coverage)
        assert(not i2.is_reversal)  # i2 is not a reversal
        i2.token = m2.dues15_token  # we give it a valid token
        req2.matchdict = {
            'email': m2.email,
            'code': m2.dues15_token,
            'no': u'0002',
        }
        res = make_reversal_invoice_pdf(req2)
        assert('application/pdf' not in res.headers['Content-Type'])  # no PDF
        assert('error_page' in res.headers['Location'])  # but error
        ######################################################################

        # retry with valid token:
        req2.matchdict = {
            'email': m1.email,
            'code': m1.dues15_token,
            'no': u'0003',
        }
        res = make_reversal_invoice_pdf(req2)
        # print("length of the result: {}".format(len(res.body)))
        # print("headers of the result: {}".format((res.headers)))
        assert(60000 < len(res.body) < 80000)
        assert('application/pdf' in res.headers['Content-Type'])
