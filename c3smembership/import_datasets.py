# -*- coding: utf-8 -*-
from c3smembership.models import (
    C3sMember,
    DBSession,
    Shares,
#    Membership,
)
import datetime

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    authenticated_userid,
)
from sqlalchemy.exc import (
    IntegrityError,
    ResourceClosedError,
)
import tempfile
from types import NoneType
import unicodecsv


@view_config(permission='manage',
             route_name='import_founders')
def import_founders(request):
    '''
    import the list of founders
    '''
    try:  # check if the file exists
        with open(request.registry.settings['founders_importfile'], 'r') as f:
            # store contents in tempfile
            content = tempfile.NamedTemporaryFile()
            content.write(f.read())
            content.seek(0)  # rewind to beginning

    except IOError, ioe:
        print ioe
        request.session.flash("file not found.", 'messages')
        return HTTPFound(request.route_url('dashboard_only'))

    # reader for CSV files
    r = unicodecsv.reader(content.file, delimiter=',',
                          encoding='utf-8',
                          #encoding='iso-8859-2',
                          quoting=unicodecsv.QUOTE_ALL
                          )
    header = r.next()  # first line is the header.
    print("the header: %s" % header)
    try:
        assert header == [
            u'Reihenfolge', u'Vorname', u'Nachname',  # 0, 1, 2
            u'Email', u'Adresse',  # 3, 4
            u'Adresse 2', u'PLZ', u'Ort', u'Bundesland etc', u'Land',  # 5-9
            u'Anteile',  # 10
            u'Geburtsdatum',  # 11
        ]
    except AssertionError, ae:
        print ae
        print "the header of the CSV does not match what we expect"
        request.session.flash(
            "Import: header fields mismatch. NOT importing",
            'message_to_staff')
        return HTTPFound(request.route_url('toolbox'))

    # count the datasets
    counter = 0

    while True:
        try:
            row = r.next()
        except:
            break
        counter += 1

        import_member = C3sMember(
            firstname=row[1],
            lastname=row[2],
            email=row[3],
            password='None',
            address1=row[4],
            address2=row[5],
            postcode=row[6],
            city=row[7],
            country=row[9],
            locale=u'de',
            date_of_birth=datetime.datetime.strptime(row[11], '%Y-%m-%d'),
            email_is_confirmed=True,
            email_confirm_code=u'GründungHH_{}'.format(counter),
            date_of_submission=datetime.datetime(2013, 9, 25),
            membership_type=u'unknown',
            member_of_colsoc=False,
            name_of_colsoc=u'',
            num_shares=row[10],
        )
        import_member.signature_received = True
        import_member.signature_received_date = datetime.datetime.strptime(
            '2013-09-25', '%Y-%m-%d')
        import_member.signature_confirmed = True
        import_member.signature_confirmed_date = datetime.datetime.strptime(
            '2013-09-25', '%Y-%m-%d')
        import_member.payment_received = True
        import_member.payment_received_date = datetime.date(2013, 9, 25)
        import_member.payment_confirmed = True
        import_member.payment_confirmed_date = datetime.date(2013, 9, 25)
        import_member.date_of_submission = datetime.date(2013, 9, 25)
        try:
            dbsession = DBSession
            dbsession.add(import_member)
            request.session.flash(
                "imported dataset %s" % (import_member.email_confirm_code),
                'messages')
        except ResourceClosedError, rce:
            print "transaction was aborted/resource closed"
            print rce
            return {
                'message': "resource closed error. ABORTED!"}
        except IntegrityError, ie:
            print "integrity error"
            dbsession.rollback()
            print ie
            if 'column email_confirm_code is not unique' in ie.message:
                print("import of dataset %s failed, because the confirmation"
                      "code already existed" % counter)
                return {
                    'message': "integrity error. ABORTED!"}
        except StopIteration, si:
            print "stop iteration reached"
            print si
            return {'message': "file found, StopIteration reached."}
    return HTTPFound(
        request.route_url(
            'dashboard', number=0, orderby='id', order='asc'))


@view_config(permission='manage',
             route_name='import_crowdfunders')
def import_crowdfunders(request):
    '''
    import the list of crowdfunders to the membership database
    '''
    try:  # check if the file exists
        #with open('import/startnext_success.utf8.csv', 'r') as f:
        startnext_importfile = request.registry.settings['startnext_importfile']
        with open(startnext_importfile, 'r') as f:
            print("the csv file was found.")
            # store contents in tempfile
            content = tempfile.NamedTemporaryFile()
            content.write(f.read())
            content.seek(0)  # rewind to beginning

    except IOError, ioe:
        print ioe
        request.session.flash("file not found.", 'messages')
        request.session.flash(ioe, 'messages')
        return HTTPFound(request.route_url('dashboard_only'))

    # reader for CSV files
    #rdr = unicodecsv.reader(content.file, delimiter='\t',
    rdr = unicodecsv.reader(content.file, delimiter=';',
                            encoding='utf-8',
                            quoting=unicodecsv.QUOTE_ALL
                            )
    header = rdr.next()  # first line is the header.
    '''
    the header (first line) of the CSV file is used to confirm the format
    '''
    print("the header = %s" % header)
    try:
        # assert header == [u'Gesamtwert',  # 0
        #                   u'Ort',  # 1
        #                   u'Kommentar',  # 2
        #                   u'Land',  # 3 DROP
        #                   u'Anschrift - Lieferadresse',  # 4
        #                   u'Ort - Lieferadresse',  # 5
        #                   u'Land - Lieferadresse',  # 6
        #                   u'Vorname - Lieferadresse',  # 7
        #                   u'Nachname - Lieferadresse',  # 8
        #                   u'PLZ - Lieferadresse',  # 9
        #                   u'Freie Unterst\xfctzung',  # 10
        #                   u'Dankesch\xf6n 1',  # 11
        #                   u'Vertragsnummer',  # 12
        #                   u'Investmentvertrag eingegangen',  # 13
        #                   u'Investment-Status',  # 14
        #                   u'Best.-Nr.',  # 15
        #                   u'Einzahler',  # 16
        #                   u'Zahlungsart',  # 17
        #                   u'Projekt-Status',  # 18 DROP
        #                   u'Projekt-Titel',  # 19 DROP
        #                   u'URL',  # 20 DROP
        #                   u'Starter-Vorname',  # 21 DROP
        #                   u'Starter-Nachname',  # 22 DROP
        #                   u'Funding-Status',  # 23 DROP
        #                   u'Datum',  # 24
        #                   u'E-Mail',  # 25
        #                   u'Unterst\xfctzer-Vorname',  # 26
        #                   u'Unterst\xfctzer-Nachname',  # 27
        #                   u'Nickname',  # 28 DROP
        #                   u'Transaktions-ID']  # 29 TR001
        expected_header = [u'Gesamtwert',  # 0
                           u'Dankesch\xf6n 1',  # 1
                           u'Anschrift',  # 2
                           u'PLZ ',  # 3
                           u'Ort ',  # 4
                           u'Land',  # 5
                           u'Vorname',  # 6
                           u'Nachname',  # 7
                           u'E-Mail',  # 8
                           u'Transaktions-ID',  # 9
                           u'Geburtsdatum',  # 10
                           u'memberDate',  # 11
                           u'Kommentar',  # 12
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'',
                           u'', ]
        assert header == expected_header
    except AssertionError, ae:
        print ae
        print "the header of the crowdfunder CSV does not match what we expect"
        #print "==== got:"
        #print header
        #print "==== expected:"
        #print expected_header
        request.session.flash(
            "Importing Crowdfunders: header fields mismatch. NOT importing",
            'message_to_staff')
        return HTTPFound(request.route_url('toolbox'))

    # remember the codes imported
    # _codes = []

    # count the datasets
    counter = 0

    while True:
        try:
            row = rdr.next()
            # DEBUG: just take 10 for testing
            #if counter == 11:
            #    break
        except:
            break  # stop import if there is no next line
        counter += 1
        print("=== row %s: %s" % (counter, row))

        # extract info about shares from the dankeschoen
        try:
            '''
            the number of shares can be extracted from row 1
            '''
            _num_shares = row[1].split('x')[0]
            #print("the number of shares: %s" % _num_shares)
        except:
            print(
                "failed to extract data: row %s, TR-ID %s. %s" % (
                    counter, row[9], row[1]))

        import_startnexter = C3sMember(
            firstname=row[6],
            lastname=row[7],
            email=row[8].lstrip('<').rstrip('>'),
            password=u'None',
            address1=row[2],
            address2=u'',
            postcode=row[3],
            city=row[4],
            country=row[5],
            locale=u'de',
            date_of_birth=datetime.datetime.strptime(row[10], '%Y-%m-%d'),
            email_is_confirmed=True,
            email_confirm_code=row[9],
            num_shares=_num_shares,
            # XXX date_of_submission is actually the membership date !!!
            date_of_submission=datetime.datetime.strptime(row[11], '%Y-%m-%d'),
            membership_type=u'startnext',
            member_of_colsoc=False,
            name_of_colsoc=u'StartNext',
        )
        import_startnexter.accountant_comment = row[12]
        import_startnexter.signature_received = True
        import_startnexter.signature_confirmed = True
        import_startnexter.payment_received = True
        import_startnexter.payment_confirmed = True
        #print('importing %s now...' % counter)
        try:
            dbsession = DBSession
            dbsession.add(import_startnexter)
            #dbsession.flush()
            request.session.flash(
                "imported dataset {}".format(
                    import_startnexter.email_confirm_code),
                'messages'
            )
            #log.info(
            #    "%s imported dataset %s" % (
            #        authenticated_userid(request),
            #        import_startnexter.email_confirm_code))
            #print('done with %s!' % counter)
        except ResourceClosedError, rce:
            # XXX can't catch this exception,
            # because it happens somwhere else, later, deeper !?!
            print "transaction was aborted/resource closed"
            print rce
            return {
                'message': "tried import of dataset but resource is closed. ABORTED!"}
        except IntegrityError, ie:
            print "integrity error"
            dbsession.rollback()
            print ie
            if 'column email_confirm_code is not unique' in ie.message:
                print("import of dataset %s failed, because the confirmation"
                      "code already existed" % counter)
                return {
                    'message': "tried import of dataset(s) with existing confirm code. ABORTED!"}
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
                # _codes.append(row[13])
                # print("the codes: %s" % str(_codes))

    # except StopIteration, si:
    #     print si
    #     print("counter: %s" % counter)
    #     return {'message': "file found. import complete",
    #             #'codes': _codes,
    #             }
#return
