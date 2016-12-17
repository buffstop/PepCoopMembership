"""
This module holds the main method: config and route declarations
"""

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from c3smembership.presentation.parameter_validation import (
    ParameterValidationException
)
from c3smembership.data.model.base import Base
from c3smembership.security.request import RequestWithUserAttribute
from c3smembership.security import (
    Root,
    groupfinder
)
from pyramid_beaker import session_factory_from_settings
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from c3smembership.presentation.views.dashboard import dashboard_content_size_provider
from c3smembership.presentation.views.membership_listing import membership_content_size_provider


from pkg_resources import get_distribution
__version__ = get_distribution('c3sMembership').version


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    session_factory = session_factory_from_settings(settings)

    authn_policy = AuthTktAuthenticationPolicy(
        's0secret!!',
        callback=groupfinder,)
    authz_policy = ACLAuthorizationPolicy()

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
    config.include('cornice')
    config.include('c3smembership.presentation.pagination')
    config.add_translation_dirs(
        'colander:locale/',
        'deform:locale/',  # copy deform.po and .mo to locale/de/LC_MESSAGES/
        'c3smembership:locale/')
    config.add_static_view('static_deform', 'deform:static')
    config.add_static_view('static',
                           'c3smembership:static', cache_max_age=3600)
    config.add_static_view(
        'docs',
        '../docs/_build/html/', cache_max_age=3600)

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

    # ## Membership application process
    # Step 1 (join.pt): home is /, the membership application form
    config.add_route('join', '/')
    # Step 2 (success.pt): check and edit data
    config.add_route('success', '/success')
    # Step 3 email was sent (check-mail.pt): send verification email address
    config.add_route('success_check_email', '/check_email')
    # Still step 3 (verify_password.pt): enter password
    # and step 4 (verify_password.pt): download form
    config.add_route('verify_email_password', '/verify/{email}/{code}')  # PDF
    # PDF download of Step 4.
    config.add_route('success_pdf', '/C3S_SCE_AFM_{namepart}.pdf')  # download
    # confirm email address later (30c3 cases)
    config.add_route(
        'verify_afm_email',
        '/vae/{refcode}/{token}/{email}')  # verify afm email
    # config.add_route(
    #    'verify_member_email',
    #    '/vfe/{refcode}/{token}/{email}')  # verify founders mail?

    # routes & views for staff
    # applications for membership
    config.add_route('dashboard', '/dashboard')
    config.make_pagination_route(
        'dashboard',
        dashboard_content_size_provider,
        sort_property_default='id',
        page_size_default=int(settings.get('c3smembership.dashboard_number', 30)))

    config.add_route('dash', '/dash/{number}/{orderby}/{order}')
    config.add_route('toolbox', '/toolbox')
    config.add_route('stats', '/stats')
    config.add_route('staff', '/staff')
    config.add_route('new_member', '/new_member')
    config.add_route('detail', '/detail/{memberid}')
    config.add_route('edit', '/edit/{_id}')




    from models import C3sMember
    from c3smembership.business.membership_application import MembershipApplication
    membership_application = MembershipApplication(C3sMember)

    config.registry.membership_application = membership_application
    config.add_route('switch_sig', '/switch_sig/{memberid}')
    config.add_route('switch_pay', '/switch_pay/{memberid}')


    config.add_route('mail_sig_confirmation', '/mail_sig_conf/{memberid}')
    config.add_route('regenerate_pdf', '/re_C3S_SCE_AFM_{code}.pdf')
    config.add_route('mail_pay_confirmation', '/mail_pay_conf/{memberid}')
    config.add_route('mail_mail_confirmation', '/mail_mail_conf/{memberid}')
    config.add_route('mail_sig_reminder', '/mail_sig_reminder/{memberid}')
    config.add_route('mail_pay_reminder', '/mail_pay_reminder/{memberid}')
    config.add_route('delete_entry', '/delete/{memberid}')
    config.add_route('delete_afms', '/delete_afms')
    config.add_route('login', '/login')
    config.add_route('export_all', '/export_all')
    config.add_route('export_members', '/export_members')
    config.add_route('export_yes_emails', '/export_yes_emails')
    config.add_route('import_all', '/import_all')
    config.add_route('import_with_ids', '/import_with_ids')
    config.add_route('import_founders', '/import_founders')
    config.add_route('import_crowdfunders', '/import_crowdfunders')
    config.add_route('fix_import_crowdfunders', '/fix_import_crowdfunders')
    config.add_route('logout', '/logout')
    # gather missing information
    config.add_route('mail_mtype_form', '/mtype/{afmid}')  # mail link to form
    config.add_route('mtype_form', '/mtype/{refcode}/{token}/{email}')  # form
    config.add_route('mtype_thanks', '/mtype_thanks')  # thanks
    # applications for membership
    config.add_route('afms_awaiting_approval', '/afms_awaiting_approval')
    # memberships
    config.add_route('flag_duplicates', '/flag_dup')
    config.add_route('merge_duplicates', '/merge_dup')
    config.add_route('make_member', '/make_member/{afm_id}')
    config.add_route('merge_member', '/merge_member/{afm_id}/{mid}')
    config.add_route('make_founders_members', '/make_founders_members')
    config.add_route('make_crowdfounders_members',
                     '/make_crowdfounders_members')
    config.add_route('make_yesser_members',
                     '/make_yesser_members')

    config.add_route('membership_listing_backend',
                     '/memberships')
    config.make_pagination_route(
        'membership_listing_backend',
        membership_content_size_provider,
        sort_property_default='id',
        page_size_default=int(settings.get('c3smembership.membership_number', 30)))

    config.add_route('membership_listing_alphabetical',
                     '/aml')
    config.add_route('membership_listing_date_pdf',
                     '/aml-{date}.pdf')
    config.add_route('membership_listing_aufstockers',
                     '/aml_aufstockers')


    # membership dues 2015
    config.add_route('send_dues15_invoice_email', '/dues15_invoice/{member_id}')
    config.add_route('send_dues15_invoice_batch', '/dues15_invoice_batch')
    # config.add_route('send_dues_receipt_mail',
    #                  '/dues_receipt_mail/{member_id}')
    # config.add_route('make_dues_invoice_pdf',  # retired! use route below!
    #                 '/dues_invoice/{email}/{code}/invoice.pdf')
    config.add_route('make_dues15_invoice_no_pdf',
                     '/dues15_invoice_no/{email}/{code}/C3S-dues15-{i}.pdf')
    config.add_route('dues15_reduction',
                     '/dues15_reduction/{member_id}')
    config.add_route('make_dues15_reversal_invoice_pdf',
                     '/dues15_reversal/{email}/{code}/C3S-dues15-{no}-S.pdf')
    config.add_route('dues15_notice', '/dues15_notice/{member_id}')
    config.add_route('dues15_listing', '/dues15_listing')


    # membership dues 2016
    config.add_route('send_dues16_invoice_email', '/dues16_invoice/{member_id}')
    config.add_route('send_dues16_invoice_batch', '/dues16_invoice_batch')
    config.add_route('make_dues16_invoice_no_pdf',
                     '/dues16_invoice_no/{email}/{code}/C3S-dues16-{i}.pdf')
    config.add_route('dues16_reduction',
                     '/dues16_reduction/{member_id}')
    config.add_route('make_dues16_reversal_invoice_pdf',
                     '/dues16_reversal/{email}/{code}/C3S-dues16-{no}-S.pdf')
    config.add_route('dues16_notice', '/dues16_notice/{member_id}')
    config.add_route('dues16_listing', '/dues16_listing')


    from c3smembership.models import C3sMember, Dues15Invoice
    from c3smembership.data.model.base import DBSession
    from c3smembership.business.dues_invoice_archiving import DuesInvoiceArchiving
    from c3smembership.views.membership_dues import (
        make_invoice_pdf_pdflatex,
        make_reversal_pdf_pdflatex,
    )
    import os
    invoices_archive_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../invoices/'))
    config.registry.dues_invoice_archiving = DuesInvoiceArchiving(
        DBSession,
        C3sMember,
        Dues15Invoice,
        make_invoice_pdf_pdflatex,
        make_reversal_pdf_pdflatex,
        invoices_archive_path)
    config.add_route('batch_archive_pdf_invoices', '/batch_archive_pdf_invoices')

    # utilities & wizardry
    config.add_route('plz_dist', '/plz_dist')
    config.add_route('get_member', '/members/{memberid}')
    config.add_route('error_page', '/error')  # generic error view

    # shares
    config.add_route('shares_detail', '/shares_detail/{id}')
    config.add_route('shares_edit', '/shares_edit/{id}')
    config.add_route('shares_delete', '/shares_delete/{id}')
    # membership_certificate
    config.add_route('certificate_mail', '/cert_mail/{id}')
    config.add_route('certificate_pdf', '/cert/{id}/C3S_{name}_{token}.pdf')
    config.add_route('certificate_pdf_staff', '/cert/{id}/C3S_{name}.pdf')
    # annual reports
    config.add_route('annual_reporting', '/annual_reporting')
    # invite people
    config.add_route('invite_member', '/invite_member/{m_id}')
    config.add_route('invite_batch', '/invite_batch/{number}')
    # search for people
    config.add_route('search_people', '/search_people')
    config.add_route('autocomplete_people_search', '/aps/')
    # search for codes
    config.add_route('search_codes', '/search_codes')
    config.add_route('autocomplete_input_values', '/aiv/')
    # fix the database
    config.scan()
    return config.make_wsgi_app()
