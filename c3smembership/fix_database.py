# -*- coding: utf-8 -*-
from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from types import NoneType

from c3smembership.models import (
    C3sMember,
    DBSession,
    Shares,
)


@view_config(
    route_name='fix_dob',
    permission='manage')
def fix_date_of_acquisition(request):
    '''
    fix the database: date of acquisition for shares must be corrected

    the old way (old code) was the wrong way:
    we used to choose the date we received the signature or payment
    -- the later one -- to mark the date of acquisition,
    when a new package of shares was attributed to a user.
    but we need the date the board (VR) decided upon the approval.
    '''
    _num_total = Shares.get_number()
    print("the number of entries: {}".format(_num_total))
    # print("the range: {}".format(range(_num_total)))
    items_to_fix = []
    for i in range(_num_total+1):
        # print(i)
        s = Shares.get_by_id(i)
        if not isinstance(s, NoneType):
            if (
                    (s.date_of_acquisition > datetime(2013, 9, 25))
                    and (s.date_of_acquisition < datetime(2014, 3, 29))
            ):
                # print("this one needs fixing! {}: {} {}".format(
                #    s.id,
                #    s.date_of_acquisition,
                #    type(s.date_of_acquisition),
                # ))
                s.date_of_acquisition = datetime(2014, 3, 29)
                items_to_fix.append(s.id)
    print("Done. {} items needed fixing.".format(len(items_to_fix)))

    request.session.flash(
        "Done. {} items need fixing.".format(len(items_to_fix)),
        'message_to_staff'
    )
    return HTTPFound('toolbox')


@view_config(route_name='fix_database',
             permission='manage')
def fix_database(request):
    '''
    fix the database: correct values/codes for countries
    '''
    _num_total = C3sMember.get_number()+1
    #print "the number of entries: {}".format(_num_total)
    #print "the range: {}".format(range(_num_total))
    for i in range(_num_total):
        m = C3sMember.get_by_id(i)
        if not isinstance(m, NoneType):
            #print u"country of id {}: {}".format(i, m.country)
            # deutschland
            if ((u'Deutschland' in m.country) or
                    (u'Germany' in m.country) or
                    ('Deutschland' in m.country) or
                    (m.country.endswith('eutschland'))):
                m.country = u'DE'
                DBSession.add(m)
                DBSession.flush()
                print "changed country for id {}".format(i)
            # Österreich
            if ((u'Österreich' in m.country) or ('Austria' in m.country) or
                    (m.country.endswith('sterreich'))):
                m.country = u'AT'
                DBSession.add(m)
                DBSession.flush()
                print "changed country for id {}".format(i)
            # Dändemark
            if m.country == u'Dänemark':
                m.country = u'DK'
                DBSession.add(m)
                DBSession.flush()
                print "changed country for id {}".format(i)
            # Vereinigtes Königreich
            if ((m.country == u'Vereinigtes Königreich') or
                    (m.country.endswith('nigreich'))):
                m.country = u'GB'
                DBSession.add(m)
                DBSession.flush()
                print "changed country for id {}".format(i)
            # Irland
            if m.country == u'Irland':
                m.country = u'IR'
                DBSession.add(m)
                DBSession.flush()
                print "changed country for id {}".format(i)
            # liechtenstein
            if m.country == u'Liechtenstein':
                m.country = u'LI'
                DBSession.add(m)
                DBSession.flush()
                print "changed country for id {}".format(i)
            # France
            if ((m.country == u'France') or (m.country == u'Frankreich') or
                    (m.country == 'Frankreich')):
                m.country = u'FR'
                DBSession.add(m)
                DBSession.flush()
                print "changed country for id {}".format(i)
            # Spanien
            if m.country == u'Spanien':
                m.country = u'ES'
                DBSession.add(m)
                DBSession.flush()
                print "changed country for id {}".format(i)
            # Schweden
            if m.country == u'Schweden':
                m.country = u'SE'
                DBSession.add(m)
                DBSession.flush()
                print "changed country for id {}".format(i)
            # Switzerland
            if ((m.country == u'Switzerland') or (m.country == u'Schweiz')):
                m.country = u'CH'
                DBSession.add(m)
                DBSession.flush()
                print "changed country for id {}".format(i)
    return HTTPFound('stats')
