from cornice import Service
import json
from types import NoneType
from webob.exc import HTTPUnauthorized

from c3smembership.models import C3sMember

api_ver = '0.1dev'

member = Service(name='member', path='/lm', description="load user info")


def token_does_match(request):
    '''
    a validator to check the token
    '''
    _token = request.headers['X-messaging-token']
    #print "the api received this: {}".format(_token)
    if ((_token in request.registry.settings['api_auth_token']) and
            (request.registry.settings['api_auth_token'] in _token)):
        #print "validator: token: all good!"
        pass
    else:
        request.errors.add('url', 'name', 'Token does not match!')
        raise HTTPUnauthorized()


def does_exist(request):
    req = json.loads(request.body)
    _token = req['token']
    request.validated['refcode'] = _token


@member.put(validators=(does_exist, token_does_match))
def api_userinfo(request):
    '''
    allow api access to load user info (for ticketing)
    '''
    #print "the refcode received: {}".format(request.validated['refcode'])
    _m = C3sMember.get_by_code(request.validated['refcode'])
    if isinstance(_m, NoneType):
        return {
            'firstname': 'None',
            'lastname': 'None',
        }
    #print "api found member: {} {}".format(_m.firstname, _m.lastname)
    return {
        'firstname': _m.firstname,
        'lastname': _m.lastname,
        'email': _m.email,
        'mtype': _m.membership_type,
    }
