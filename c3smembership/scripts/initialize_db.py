# -*- coding: utf-8 -*-

import os
import sys
import transaction
from datetime import datetime, date

from sqlalchemy import engine_from_config
# from sqlalchemy.exc import IntegrityError
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from c3smembership.models import (
    DBSession,
    Group,
    C3sStaff,
    C3sMember,
    Base,
)

"""
this module holds database initialization code

when the webapp is installed, a database has to be initialized in order to
store form input (new members), but also to authenticate staff when loging in.

in setup.py there is a section 'console_scripts' under 'entry_points'.
thus a console script is created when the app is set up:

  env/bin/initialize_c3sMembership_db

the main function below is called...

we have different use cases:
(1) production:
        for production we need a clean database (initially no members)
        with accounts for staffers/accountants to auth their login.
        those credentials should not go into version control.
(2) testing
        for tests and demo purposes we need prepopulated databases:
        example users to check if the app works, and enough of them
        so staffers can check out pagination
"""

how_many = 7


def usage(argv):
    """
    print usage information if the script was called with bad arguments
    """
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    """
    initialize the database
    """
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    # add some content
    with transaction.manager:
        # a group for accountants/staff
        accountants_group = Group(name=u"staff")
        try:
            DBSession.add(accountants_group)
            DBSession.flush()
            # print("adding group staff")
        except:
            print("could not add group staff.")
            # pass
    with transaction.manager:
        # staff personnel
        staffer1 = C3sStaff(
            login=u"rut",
            password=u"berries",
            email=u"noreply@c3s.cc",
        )
        staffer1.groups = [accountants_group]
        try:
            DBSession.add(staffer1)
            # print("adding staff rut")
            DBSession.flush()
        except:
            print("it borked! (rut)")
            # pass
    # one more staffer
    with transaction.manager:
        staffer2 = C3sStaff(
            login=u"reel",
            password=u"boo",
            email=u"noreply@c3s.cc",
        )
        staffer2.groups = [accountants_group]
        try:
            DBSession.add(staffer2)
            # print("adding staff reel")
            DBSession.flush()
        except:
            print("it borked! (reel)")
            # pass
    # a member, actually a membership form submission
    with transaction.manager:
        member1 = C3sMember(
            firstname=u"Firstnäme",  # includes umlaut
            lastname=u"Lastname",
            email=u"foo@shri.de",
            password=u"berries",
            address1=u"address one",
            address2=u"address two",
            postcode=u"12345 foo",
            city=u"Footown Mäh",
            country=u"Foocountry",
            locale=u"en",
            date_of_birth=date(1971, 02, 03),
            email_is_confirmed=False,
            email_confirm_code=u"ABCDEFGHIJ",
            num_shares=u'10',
            date_of_submission=datetime.now(),
            membership_type=u'normal',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
        )
        try:
            DBSession.add(member1)
            # print("adding Firstnäme")
        except:
            pass

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
            date_of_birth=date(1971, 3, 4),
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
            date_of_birth=date(1972, 4, 5),
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
            date_of_birth=date(1974, 9, 8),
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
            date_of_birth=date(1978, 4, 1),
            email_is_confirmed=False,
            email_confirm_code=u'INVESTING_EN',
            password=u'arandompasswor5',
            date_of_submission=date.today(),
            membership_type=u'investing',
            member_of_colsoc=True,
            name_of_colsoc=u"GEMA",
            num_shares=u'60',
        )
        legal_entity_de = C3sMember(  # german investing legal entity
            firstname=u'Deutscher',
            lastname=u'Musikverlag',
            email=u'verlag@compa.ny',
            address1=u"foo bulevard",
            address2=u"123-345",
            postcode=u"98765",
            city=u"Foo",
            country=u"Bar",
            locale=u"de",
            date_of_birth=date(1987, 3, 6),
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
            date_of_birth=date(1982, 4, 2),
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
        legal_entity_de.is_legalentity = True
        DBSession.add(legal_entity_de)
        legal_entity_en.is_legalentity = True
        DBSession.add(legal_entity_en)


        # even more members
        # import random
        # import string

        # print("about to add %s members..." % how_many)
        # for i in range(how_many):  # create 50 members with semi-random dates
        #     # print i
        #     member = C3sMember(
        #         firstname=u"Firstnäme%s" % i,  # includes umlaut
        #         lastname=u"Lastname",
        #         email=u"foo_n" + str(i) + u"@shri.de",
        #         password=u"berries",
        #         address1=u"address one",
        #         address2=u"address two",
        #         postcode=u"12345 foo",
        #         city=u"Footown Mäh",
        #         country=u"Foocountry",
        #         locale=u"de",
        #         date_of_birth=date.today(),
        #         email_is_confirmed=False,
        #         email_confirm_code=str(i) + u''.join(
        #             random.choice(
        #                 string.ascii_uppercase + string.digits
        #             ) for x in range(8)),
        #         num_shares=random.randint(1, 60),
        #         date_of_submission=datetime.now(),
        #         membership_type=random.choice((u'normal', u'investing')),
        #         member_of_colsoc=random.choice((True, False)),
        #         name_of_colsoc=u"GEMA",
        #     )
        #     try:
        #         DBSession.add(member)
        #     except IntegrityError:
        #         print("exception!!!!!!!!!!!!!!!!!!!!1")
        #         # DBSession.remove(member)


def init():
    # config_uri = 'development.ini'
    # setup_logging(config_uri)
    # settings = get_appsettings(config_uri)
    # engine = engine_from_config('sqlite://')
    engine = engine_from_config({'sqlalchemy.url': 'sqlite://'})
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    # with transaction.manager:
    #     accountants_group = Group(name=u"staff")
    #     staffer1 = C3sStaff(
    #         login=u"rut",
    #         password=u"berries",
    #         email=u"noreply@c3s.cc",
    #     )
    #     staffer1.groups = [accountants_group]

    #     member1 = C3sMember(
    #         firstname=u"Firstnäme",  # includes umlaut
    #         lastname=u"Lastname",
    #         email=u"foo@shri.de",
    #         password=u"berries",
    #         address1=u"address one",
    #         address2=u"address two",
    #         postcode=u"12345 foo",
    #         city=u"Footown Mäh",
    #         country=u"Foocountry",
    #         locale=u"DE",
    #         date_of_birth=date.today(),
    #         email_is_confirmed=False,
    #         email_confirm_code=u"ABCDEFGHIJ",
    #         num_shares=u'10',
    #         date_of_submission=datetime.now(),
    #         #invest_member=True,
    #         membership_type=u'normal',
    #         member_of_colsoc=True,
    #         name_of_colsoc=u"GEMA",
    #     )
    #     try:
    #         DBSession.add(accountants_group)
    #     except IntegrityError:
    #         DBSession.delete(accountants_group)

    #     try:
    #         DBSession.add(staffer1)
    #     except IntegrityError:
    #         pass
    #         #import pdb
    #         #pdb.set_trace()

    #     if (C3sMember.get_by_code(member1.email_confirm_code) is None):
    #         # there is no member in the DB with that same email_confirm_code
    #         print(
    #             "C3sMember.get_by_code(member1.email_confirm_code) is None")
    #         try:
    #             DBSession.add(member1)
    #         except IntegrityError:
    #             pass


# def init_50():
#     """
#     this function creates 50 dummy users to fill the database
#     so we get the staff dashboard filled with test entries
#     """
#     #config_uri = 'development.ini'
#     #setup_logging(config_uri)
#     #settings = get_appsettings(config_uri)
#     #engine = engine_from_config('sqlite://')
#     engine = engine_from_config({'sqlalchemy.url': 'sqlite://'})
#     DBSession.configure(bind=engine)
#     Base.metadata.create_all(engine)
#     import random
#     import string
#     with transaction.manager:
#         for i in range(50):
#             member = C3sMember(
#                 firstname=u"Firstnäme",  # includes umlaut
#                 lastname=u"Lastname",
#                 email=u"foo@shri.de",
#                 password=u"berries",
#                 address1=u"address one",
#                 address2=u"address two",
#                 postcode=u"12345 foo",
#                 city=u"Footown Mäh",
#                 country=u"Foocountry",
#                 locale=u"DE",
#                 date_of_birth=date.today(),
#                 email_is_confirmed=False,
#                 email_confirm_code=''.join(
#                     random.choice(
#                         string.ascii_uppercase + string.digits
#                     ) for x in range(8)),
#                 num_shares=u'10',
#                 date_of_submission=datetime.now(),
#                 #invest_member=True,
#                 membership_type=random.choice((u'normal', u'investing')),
#                 member_of_colsoc=True,
#                 name_of_colsoc=u"GEMA",
#             )
#             print member.membership_type
#             try:
#                 DBSession.add(member)
#             except IntegrityError:
#                 pass
