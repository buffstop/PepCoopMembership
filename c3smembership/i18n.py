import customization

def enforcing_locale_negotiator(request):
    """ The :term:`custom locale negotiator`. Returns a locale name.

    - First, the negotiator looks for the ``_LOCALE_`` attribute of
      the request object (possibly set by a view or a listener for an
      :term:`event`).

    - Then it looks for the ``request.params['_LOCALE_']`` value.

    - Then it looks for the ``request.cookies['_LOCALE_']`` value.

    - Then it looks for the ``Accept-Language`` header value,
      which is set by the user in his/her browser configuration.

    - Finally, if the locale could not be determined via any of
      the previous checks, the negotiator returns the
      :term:`default locale name`.

    - In all cases it enforces the locale being in customization.translations, falling back to default_locale_name  if the negotiation so far lead to something else
    """

    name = '_LOCALE_'
    locale_name = getattr(request, name, None)
    if locale_name is None:
        locale_name = request.params.get(name)
        if locale_name is None:
            locale_name = request.cookies.get(name)
            if locale_name is None:
                locale_name = request.accept_language.best_match(
                    customization.locale_country_mapping.keys(), request.registry.settings.default_locale_name)
                if not request.accept_language:
                    # If browser has no language configuration
                    # the default locale name is returned.
                    locale_name = request.registry.settings.default_locale_name

    if locale_name not in customization.translations:
        locale_name = request.registry.settings.default_locale_name
        
    return locale_name
