from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from c3smembership.models import Base
from c3smembership.security.request import RequestWithUserAttribute
from c3smembership.security import (
    Root,
    groupfinder
)
from pyramid_beaker import session_factory_from_settings
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    session_factory = session_factory_from_settings(settings)

    authn_policy = AuthTktAuthenticationPolicy(
        's0secret!!',
        callback=groupfinder,)
    authz_policy = ACLAuthorizationPolicy()

    #DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          session_factory=session_factory,
                          root_factory=Root)
    # using a custom request with user information
    config.set_request_factory(RequestWithUserAttribute)

    config.include('pyramid_mailer')
    config.include('pyramid_chameleon')  # for pyramid 1.5a... for later
    config.add_translation_dirs(
        'colander:locale/',
        'deform:locale/',  # copy deform.po and .mo to locale/de/LC_MESSAGES/
        'c3smembership:locale/')
    config.add_static_view('static_deform', 'deform:static')
    config.add_static_view('static',
                           'c3smembership:static', cache_max_age=3600)

    config.add_subscriber('c3smembership.subscribers.add_base_template',
                          'pyramid.events.BeforeRender')
    config.add_subscriber(
        'c3smembership.subscribers.add_base_bootstrap_template',
        'pyramid.events.BeforeRender')
    config.add_subscriber('c3smembership.subscribers.add_backend_template',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('c3smembership.subscribers.add_locale_to_cookie',
                          'pyramid.events.NewRequest')
    config.add_renderer(name='csv',
                        factory='c3smembership.renderers.CSVRenderer')
    # home is /, the membership application form
    config.add_route('join', '/')
    # info pages
    #config.add_route('disclaimer', '/disclaimer')
    #config.add_route('faq', '/faq')
    #config.add_route('statute', '/statute')
    #config.add_route('manifesto', '/manifesto')
    # success and further steps
    config.add_route('success', '/success')
    config.add_route('success_check_email', '/check_email')
    config.add_route('verify_email_password', '/verify/{email}/{code}')  # PDF
    config.add_route('success_pdf', '/C3S_SCE_AFM_{namepart}.pdf')  # download
    # confirm email address later (30c3 cases)
    config.add_route(
        'verify_afm_email',
        '/vae/{refcode}/{token}/{email}')  # verify afm email
    #config.add_route(
    #    'verify_member_email',
    #    '/vfe/{refcode}/{token}/{email}')  # verify founders mail?
    # routes & views for staff
    # applications for membership
    config.add_route('dashboard_only', '/dashboard')
    config.add_route('dashboard', '/dashboard/{number}/{orderby}/{order}')
    config.add_route('autocomplete_input_values', '/aiv/')
    config.add_route('toolbox', '/toolbox')
    config.add_route('stats', '/stats')
    config.add_route('staff', '/staff')
    config.add_route('new_member', '/new_member')
    config.add_route('detail', '/detail/{memberid}')
    config.add_route('edit', '/edit/{_id}')
    config.add_route('switch_sig', '/switch_sig/{memberid}')
    config.add_route('mail_sig_confirmation', '/mail_sig_conf/{memberid}')
    config.add_route('regenerate_pdf', '/re_C3S_SCE_AFM_{code}.pdf')
    config.add_route('switch_pay', '/switch_pay/{memberid}')
    config.add_route('mail_pay_confirmation', '/mail_pay_conf/{memberid}')
    config.add_route('mail_mail_confirmation', '/mail_mail_conf/{memberid}')
    config.add_route('mail_sig_reminder', '/mail_sig_reminder/{memberid}')
    config.add_route('mail_pay_reminder', '/mail_pay_reminder/{memberid}')
    config.add_route('delete_entry', '/delete/{memberid}')
    config.add_route('delete_afms', '/delete_afms')
    config.add_route('login', '/login')
    config.add_route('export_all', '/export_all')
    config.add_route('export_yes_emails', '/export_yes_emails')
    config.add_route('import_all', '/import_all')
    config.add_route('import_with_ids', '/import_with_ids')
    config.add_route('import_founders', '/import_founders')
    config.add_route('import_crowdfunders', '/import_crowdfunders')
    config.add_route('logout', '/logout')
    # gather missing information
    config.add_route('mail_mtype_form', '/mtype/{afmid}')  # mail link to form
    config.add_route('mtype_form', '/mtype/{refcode}/{token}/{email}')  # form
    config.add_route('mtype_thanks', '/mtype_thanks')  # thanks
    # memberships
    config.add_route('make_member', '/make_member/{afm_id}')
    config.add_route('membership_listing',
                     '/memberships/{number}/{orderby}/{order}')
    # fix the database
    config.add_route('fix_database', '/fix_database')
    config.scan()
    return config.make_wsgi_app()
