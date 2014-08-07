# -*- coding: utf-8 -*-

from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.view import view_config
from sqlalchemy.exc import (
    IntegrityError,
    ResourceClosedError,
)
import tempfile
import unicodecsv

from c3smembership.models import (
    DBSession,
    C3sMember,
)

DEBUG = False
LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    log = logging.getLogger(__name__)


@view_config(renderer='templates/import.pt',
             permission='manage',
             route_name='import_all')
def import_db(request):
    """
    import the contents of import.csv to the database
    """
    try:  # check if the file exists
        with open('import/import.csv', 'r') as f:
            # store contents in tempfile
            content = tempfile.NamedTemporaryFile()
            content.write(f.read())
            content.seek(0)  # rewind to beginning

    except IOError, ioe:  # pragma: no cover
        print ioe
        return {'message': "file not found.",
                #        'codes': ''
                }
    # reader for CSV files
    r = unicodecsv.reader(content.file, delimiter=';',
                          encoding='utf-8',
                          quoting=unicodecsv.QUOTE_ALL
                          )
    header = r.next()  # first line is the header.
    #print("the header: %s" % header)
    # check it for compatibility
    try:
        assert header == [
            u'firstname', u'lastname', u'email',  # 0, 1, 2
            u'password', u'last_password_change',  # 3, 4
            u'address1', u'address2', u'postcode', u'city', u'country',  # 5-9
            u'locale', u'date_of_birth',  # 10, 11
            u'email_is_confirmed', u'email_confirm_code',  # 12, 13
            u'num_shares', u'date_of_submission',  # 14, 15
            u'membership_type',  # 16
            u'member_of_colsoc', u'name_of_colsoc',  # 17, 18
            u'signature_received', u'signature_received_date',  # 19, 20
            u'payment_received', u'payment_received_date',  # 21, 22
            u'signature_confirmed', u'signature_confirmed_date',  # 23, 24
            u'payment_confirmed', u'payment_confirmed_date',  # 25, 26
            u'accountant_comment'  # 27
        ]
    except AssertionError, ae:  # pragma: no cover
        print ae
        print "the header of the CSV does not match what we expect"
        return {'message': "header fields mismatch. NOT importing",
                #'codes': _codes,
                }

    # remember the codes imported
    # _codes = []

    # count the datasets
    counter = 0

    while True:
        # import pdb
        # pdb.set_trace()
        try:
            row = r.next()
        except:
            break
        counter += 1
        #print("=== row %s: %s" % (counter, row))
        #print("=== DEBUG: row[12] is: %s " % row[12])
        #print("=== DEBUG: row[15] is: %s " % row[15])
        # DEBUGGING (show datasets):
        #for i in range(row.__len__()):
        #    print('%s header: %s row: %s' % (i, header[i], row[i]))
#
#
# (Pdb) for i in range(row.__len__()): print('%s header: %s row: %s' % (i, header[i], row[i]))
# 0 header: firstname row: Firstnäme
# 1 header: lastname row: Lastname
# 2 header: email row: foo@shri.de
# 3 header: password row: $2a$10$gv8NJbKfuPuOt9GYn1/bxeW3vNLVkPlD3FQEOJ8iioWraMMKX9h4K
# 4 header: last_password_change row: 2013-11-14 10:41:14.000425
# 5 header: address1 row: address one
# 6 header: address2 row: address two
# 7 header: postcode row: 12345 foo
# 8 header: city row: Footown Mäh
# 9 header: country row: Foocountry
# 10 header: locale row: DE
# 11 header: date_of_birth row: 2013-11-14
# 12 header: email_is_confirmed row: True
# 13 header: email_confirm_code row: ABCDEFGHIJ
# 14 header: num_shares row: 10
# 15 header: date_of_submission row: 2013-11-14 10:41:14.000506
# 16 header: membership_type row: normal
# 17 header: member_of_colsoc row: True
# 18 header: name_of_colsoc row: GEMA
# 19 header: signature_received row: False
# 20 header: signature_received_date row: 1970-01-01 00:00:00
# 21 header: payment_received row: False
# 22 header: payment_received_date row: 1970-01-01 00:00:00
# 23 header: signature_confirmed row: True
# 24 header: signature_confirmed_date row: 2014-01-04 23:22:02.652407
# 25 header: payment_confirmed row: True
# 26 header: payment_confirmed_date row: 2013-12-11 20:19:53.365248
# 27 header: accountant_comment row:

        #import pdb
        #pdb.set_trace()
        #print(row[12] is True)

        import_member = C3sMember(
            firstname=row[0],
            lastname=row[1],
            email=row[2],
            password=row[3],
            address1=row[5],
            address2=row[6],
            postcode=row[7],
            city=row[8],
            country=row[9],
            locale=row[10],
            date_of_birth=datetime.strptime(row[11], '%Y-%m-%d'),
            # (1970, 1, 1)
            email_is_confirmed=True if (row[12] == 'True') else False,
            email_confirm_code=row[13],
            date_of_submission=row[15],
            membership_type=row[16],
            member_of_colsoc=True if (row[17] == 'True') else False,
            name_of_colsoc=row[18],
            num_shares=row[14],
        )
        import_member.last_password_change = datetime.strptime(
            row[4], '%Y-%m-%d %H:%M:%S.%f')
        import_member.date_of_submission = datetime.strptime(
            row[15], '%Y-%m-%d %H:%M:%S.%f')
        import_member.signature_received = True if (
            row[19] == 'True') else False
        try:
            import_member.signature_received_date = datetime.strptime(
                row[20], '%Y-%m-%d %H:%M:%S.%f')
        except:  # pragma: no cover
            import_member.signature_received_date = datetime.strptime(
                row[20], '%Y-%m-%d %H:%M:%S')
        import_member.payment_received = True if (row[21] == 'True') else False
        try:
            import_member.payment_received_date = datetime.strptime(
                row[22], '%Y-%m-%d %H:%M:%S')
        except:  # pragma: no cover
            import_member.payment_received_date = datetime.strptime(
                row[22], '%Y-%m-%d %H:%M:%S.%f')
        import_member.signature_confirmed = True if (
            row[23] == 'True') else False
        try:
            import_member.signature_confirmed_date = datetime.strptime(
                row[24], '%Y-%m-%d %H:%M:%S')
        except:  # pragma: no cover
            import_member.signature_confirmed_date = datetime.strptime(
                row[24], '%Y-%m-%d %H:%M:%S.%f')

        import_member.payment_confirmed = True if (
            'True' in row[25]) else False
        try:
            import_member.payment_confirmed_date = datetime.strptime(
                row[26], '%Y-%m-%d %H:%M:%S')
        except:   # pragma: no cover
            import_member.payment_confirmed_date = datetime.strptime(
                row[26], '%Y-%m-%d %H:%M:%S.%f')

        import_member.accountant_comment = row[27]
        #print('importing %s now...' % counter)
        try:
            dbsession = DBSession
            dbsession.add(import_member)
            dbsession.flush()
            log.info(
                "%s imported dataset %s" % (
                    authenticated_userid(request),
                    import_member.email_confirm_code))
            request.session.flash(
                "imported dataset %s" % (import_member.email_confirm_code),
                'messages',
            )
            #print('done with %s!' % counter)
        except ResourceClosedError, rce:  # pragma: no cover
            # XXX can't catch this exception,
            # because it happens somwhere else, later, deeper !?!
            print "transaction was aborted/resource closed"
            print rce
            return {'message': ("tried import of dataset(s) with "
                                "existing confirm code. ABORTED!")}
        except IntegrityError, ie:  # pragma: no cover
            print "integrity error"
            dbsession.rollback()
            print ie
            if 'column email_confirm_code is not unique' in ie.message:
                print("import of dataset %s failed, because the confirmation"
                      "code already existed" % counter)
                return {'message': ("tried import of dataset(s) with "
                                    "existing confirm code. ABORTED!")}
        except StopIteration, si:  # pragma: no cover
            print "stop iteration reached"
            print si
            return {'message': "file found, StopIteration reached."}
        #except:
        #    print "passing"
        #    pass

    #print("done with all import steps, successful or not!")
    return HTTPFound(
        request.route_url('dashboard_only'))
                # _codes.append(row[13])
                # print("the codes: %s" % str(_codes))

    # except StopIteration, si:
    #     print si
    #     print("counter: %s" % counter)
    #     return {'message': "file found. import complete",
    #             #'codes': _codes,
    #             }


@view_config(renderer='templates/import.pt',
             permission='manage',
             route_name='import_with_ids')
def import_db_with_ids(request):
    """
    import the contents of import.csv to the database
    and retain the given ids
    """
    try:  # check if the file exists
        with open('import/import.csv', 'r') as f:
            # store contents in tempfile
            content = tempfile.NamedTemporaryFile()
            content.write(f.read())
            content.seek(0)  # rewind to beginning
            print "found the impport file."

    except IOError, ioe:
        print ioe
        return {'message': "file not found.",
                #        'codes': ''
                }
    # reader for CSV files
    r = unicodecsv.reader(content.file, delimiter=';',
                          encoding='utf-8',
                          quoting=unicodecsv.QUOTE_ALL
                          )
    header = r.next()  # first line is the header.
    #print("the header: %s" % header)
    # check it for compatibility
    try:
        expected_header = [
            u'id',  # n-1 ;-)
            u'firstname', u'lastname', u'email',  # 0, 1, 2
            u'password', u'last_password_change',  # 3, 4
            u'address1', u'address2', u'postcode', u'city', u'country',  # 5-9
            u'locale', u'date_of_birth',  # 10, 11
            u'email_is_confirmed', u'email_confirm_code',  # 12, 13
            u'num_shares', u'date_of_submission',  # 14, 15
            u'membership_type',  # 16
            u'member_of_colsoc', u'name_of_colsoc',  # 17, 18
            u'signature_received', u'signature_received_date',  # 19, 20
            u'payment_received', u'payment_received_date',  # 21, 22
            u'signature_confirmed', u'signature_confirmed_date',  # 23, 24
            u'payment_confirmed', u'payment_confirmed_date',  # 25, 26
            u'accountant_comment'  # 27
        ]
        assert header == expected_header
    except AssertionError, ae:
        print ae
        print "the header of the CSV does not match what we expect"
        print "expected:"
        print expected_header
        print "got:"
        print header
        return {'message': "header fields mismatch. NOT importing",
                #'codes': _codes,
                }

    # remember the codes imported
    # _codes = []

    # count the datasets
    counter = 0

    while True:
        # import pdb
        # pdb.set_trace()
        try:
            row = r.next()
        except:
            break
        counter += 1
        import_member = C3sMember(
            firstname=row[1],
            lastname=row[2],
            email=row[3],
            password=row[4],
            address1=row[6],
            address2=row[7],
            postcode=row[8],
            city=row[9],
            country=row[10],
            locale=row[11],
            date_of_birth=datetime.strptime(row[12], '%Y-%m-%d'),
            # (1970, 1, 1)
            email_is_confirmed=True if (row[13] == 'True') else False,
            email_confirm_code=row[14],
            date_of_submission=row[16],
            membership_type=row[17],
            member_of_colsoc=True if (row[18] == 'True') else False,
            name_of_colsoc=row[19],
            num_shares=row[15],
        )
        import_member.last_password_change = datetime.strptime(
            row[5], '%Y-%m-%d %H:%M:%S.%f')
        import_member.date_of_submission = datetime.strptime(
            row[16], '%Y-%m-%d %H:%M:%S.%f')
        import_member.signature_received = True if (
            row[20] == 'True') else False
        try:
            import_member.signature_received_date = datetime.strptime(
                row[21], '%Y-%m-%d %H:%M:%S.%f')
        except:
            import_member.signature_received_date = datetime.strptime(
                row[21], '%Y-%m-%d %H:%M:%S')
        import_member.payment_received = True if (row[21] == 'True') else False
        try:
            import_member.payment_received_date = datetime.strptime(
                row[23], '%Y-%m-%d %H:%M:%S')
        except:
            import_member.payment_received_date = datetime.strptime(
                row[23], '%Y-%m-%d %H:%M:%S.%f')
        import_member.signature_confirmed = True if (
            row[24] == 'True') else False
        try:
            import_member.signature_confirmed_date = datetime.strptime(
                row[25], '%Y-%m-%d %H:%M:%S')
        except:
            import_member.signature_confirmed_date = datetime.strptime(
                row[25], '%Y-%m-%d %H:%M:%S.%f')

        import_member.payment_confirmed = True if (
            'True' in row[26]) else False
        try:
            import_member.payment_confirmed_date = datetime.strptime(
                row[27], '%Y-%m-%d %H:%M:%S')
        except:
            import_member.payment_confirmed_date = datetime.strptime(
                row[27], '%Y-%m-%d %H:%M:%S.%f')

        import_member.accountant_comment = row[28]
        #print('importing %s now...' % counter)
        from types import NoneType
        try:
            _id = row[0]
            print("the id we want to import to: %s" % _id)
            # check if the id is present in the DB. if yes: goto fail
            _mem = C3sMember.get_by_id(_id)  # load from id
            if isinstance(_mem, NoneType):  # check if id is taken
                import_member.id = _id  # set id as specified by import
        except:
            # well, we found an entry, so we just add a new id at the end
            print "this id seems to have been taken."
            return {'message': "header fields mismatch. NOT importing"}
            #pass

        try:
            dbsession = DBSession
            dbsession.add(import_member)
            dbsession.flush()
            log.info(
                "%s imported dataset %s" % (
                    authenticated_userid(request),
                    import_member.email_confirm_code))
            #print('done with %s!' % counter)
        except ResourceClosedError, rce:
            # XXX can't catch this exception,
            # because it happens somwhere else, later, deeper !?!
            print "transaction was aborted/resource closed"
            print rce
            return {'message': ("tried import of dataset(s) with "
                                "existing confirm code. ABORTED!")}
        except IntegrityError, ie:
            print "integrity error"
            dbsession.rollback()
            print ie
            if 'column email_confirm_code is not unique' in ie.message:
                print("import of dataset %s failed, because the confirmation"
                      "code already existed" % counter)
                return {'message': ("tried import of dataset(s) with "
                                    "existing confirm code. ABORTED!")}
        except StopIteration, si:
            print "stop iteration reached"
            print si
            return {'message': "file found, StopIteration reached."}
        #except:
        #    print "passing"
        #    pass

    #print("done with all import steps, successful or not!")
    return HTTPFound(
        request.route_url('dashboard_only'))


@view_config(renderer='csv',
             permission='manage',
             route_name='export_all')
def export_db(request):
    """
    export the database to a CSV file
    """
    datasets = C3sMember.member_listing(
        "id", how_many=C3sMember.get_number(), order='asc')
    header = ['firstname', 'lastname', 'email',
              'password', 'last_password_change',
              'address1', 'address2', 'postcode', 'city', 'country',
              'locale', 'date_of_birth',
              'email_is_confirmed', 'email_confirm_code',
              'num_shares', 'date_of_submission',
              'membership_type',
              'member_of_colsoc', 'name_of_colsoc',
              'signature_received', 'signature_received_date',
              'payment_received', 'payment_received_date',
              'signature_confirmed', 'signature_confirmed_date',
              'payment_confirmed', 'payment_confirmed_date',
              'accountant_comment',
              ]
    rows = []  # start with empty list
    for m in datasets:
        rows.append(
            (m.firstname, m.lastname, m.email,
             m.password, m.last_password_change,
             m.address1, m.address2, m.postcode, m.city, m.country,
             m.locale, m.date_of_birth,
             m.email_is_confirmed, m.email_confirm_code,
             m.num_shares, m.date_of_submission,
             m.membership_type,
             m.member_of_colsoc, m.name_of_colsoc,
             m.signature_received, m.signature_received_date,
             m.payment_received, m.payment_received_date,
             m.signature_confirmed, m.signature_confirmed_date,
             m.payment_confirmed, m.payment_confirmed_date,
             m.accountant_comment)
        )
    return {
        'header': header,
        'rows': rows}


@view_config(renderer='csv',
             permission='manage',
             route_name='export_yes_emails')
def export_yes_emails(request):
    """
    export the database to a CSV file
    """
    datasets = C3sMember.member_listing(
        "id", how_many=C3sMember.get_number(), order='asc')
    rows = []  # start with empty list
    for m in datasets:
        if m.signature_received and m.payment_received:
            rows.append(
                (m.firstname + ' ' + m.lastname + ' <' + m.email + '>',))
    return {
        'header': ['Vorname Nachname <devnull@c3s.cc>', ],
        'rows': rows}


@view_config(renderer='csv',
             permission='manage',
             route_name='export_members')
def export_memberships(request):
    """
    export the database to a CSV file
    """
    _num = C3sMember.get_number()
    datasets = C3sMember.get_members(
        'id', how_many=_num, offset=0, order=u'asc')
    header = ['firstname', 'lastname', 'email',
              'address1', 'address2', 'postcode', 'city', 'country',
              'locale', 'date_of_birth',
              #'email_is_confirmed',
              'email_confirm_code',
              'membership_date',
              'num_shares',  # 'date_of_submission',
              #'shares list (number+date)',
              'membership_type',
              'member_of_colsoc', 'name_of_colsoc',
              'signature_received', 'signature_received_date',
              'payment_received', 'payment_received_date',
              #'signature_confirmed', 'signature_confirmed_date',
              #'payment_confirmed', 'payment_confirmed_date',
              'accountant_comment',
              'is_legalentity',
              'court of law',
              'registration number',
              ]
    rows = []  # start with empty list
    for m in datasets:
        rows.append(
            (m.firstname, m.lastname, m.email,
             m.address1, m.address2, m.postcode, m.city, m.country,
             m.locale, m.date_of_birth,
             #m.email_is_confirmed,
             m.email_confirm_code,
             m.membership_date,
             m.num_shares,
             #m.date_of_submission,
             #'+'.join(str(s.id)+'('+str(s.number)+')' for s in m.shares),
             m.membership_type,
             m.member_of_colsoc, m.name_of_colsoc,
             m.signature_received, m.signature_received_date,
             m.payment_received, m.payment_received_date,
             #m.signature_confirmed, m.signature_confirmed_date,
             #m.payment_confirmed, m.payment_confirmed_date,
             m.accountant_comment,
             m.is_legalentity,
             m.court_of_law,
             m.registration_number,)
        )
    return {
        'header': header,
        'rows': rows}
