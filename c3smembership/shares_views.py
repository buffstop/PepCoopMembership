from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from types import NoneType
from c3smembership.models import Shares


@view_config(renderer='templates/shares_detail.pt',
             permission='manage',
             route_name='detail_shares')
def detail_shares(request):
    '''
    show details about a package of shares
    '''
    _s = Shares.get_by_id(request.matchdict['id'])
    if isinstance(_s, NoneType):
        # entry was not found in database
        return HTTPFound(request.route_url(
            'membership_listing', number=30, orderby='id', order='asc'))
    else:
        #import pdb
        #pdb.set_trace()
        return {'s': _s, }
