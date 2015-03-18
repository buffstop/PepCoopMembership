===========
Development
===========

Internationalization
--------------------

Refreshing the internationalization or short i18n (for the 18 characters left
out) uses three stages.

  1. The .pot Portable Object Template file: This file contains the full list
     of all translation string names without any of their values. It is the
     template for actual translation files for specific languages.

  2. The .po Portable Object file: This is a copy of the .pot which exists for
     each single language. Here the string names are assigned language
     specific values which are used for the translation.

  3. The .mo Machine Object file: This is a compiled binary version of the
     language specific .po file which makes it faster to process.

After changing a template or python file which uses i18n it is necessary to
update the translation files. This again consists of three steps:

  1. Refresh the translation template .pot

     .. code-block:: shell

       $ python setup.py extract_messages

  2. Refresh the language specific .po files

     .. code-block:: shell

       $ python setup.py update_catalog

     Now you can modify the language specific files and enter the values
     for the newly created messages.

  3. Finally, you need to recreate the binary file.

     .. code-block:: shell

       $ python setup.py compile_catalog


References:

  - http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/i18n.html#translation-domains

  - http://pyramid-cookbook.readthedocs.org/en/latest/templates/chameleon_i18n.html

  - http://danilodellaquila.com/blog/pyramid-internationalization-howto

  - http://www.plone-entwicklerhandbuch.de/plone-entwicklerhandbuch/internationalisierung/internationalisieren-des-user-interfaces
