c3sMembership README
====================

This Pyramid app handles membership for C3S SCE
(Cultural Commons Collecting Society SCE mit beschränkter Haftung.

The app that once started as a form to gain new members has
grown to a membership administration system catering to the needs of a
growing european cooperative (C3S SCE) with around 1000 members as of now.

Some features:

* Internationalisation (i18n)
* Membership information is persisted in a database.
* GnuPG encrypted mail with details submitted is sent to C3S staff.
* Once the email is verified, form submission data is used to populate a pdf with form fields
  (using fdf and pdftk) and the resulting PDF is ready for download.
* Membership certificates (pdflatex)
* Membership Dues (pdflatex)


Documentation
-------------

There is plenty of documentation under /docs, both in this repository
and in the running app (if you have sphinx compile the docs to HTML):
::

   cd docs
   make html

A compiled version of the documentation is available at:
https://yes.c3s.cc/docs/


Setup
-----

Install dependencies:

Development:
::

   $ sudo apt-get install python-pip python-dev python2.7-dev python-virtualenv libxml2-dev libxslt1-dev build-essential pdftk zlib1g-dev


Fonts:

The .odt files for the membership application in pdftk require the font
Signika which can be downloaded at:
https://www.google.com/fonts/specimen/Signika

LaTeX pdf compilation:
::

   $ sudo apt-get install texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra pgf texlive-lang-german texlive-luatex

Documentation:
::

   $ sudo apt-get install graphviz openjdk-8-jre
   $ mkdir utils
   $ wget 'http://downloads.sourceforge.net/project/plantuml/plantuml.jar' -O utils/plantuml.jar
   $ env/bin/pip install sphinx sphinxcontrib-plantuml

Setup:
::

   $ virtualenv env
   $ env/bin/python setup.py develop

Creating an initial database:
::

   $ env/bin/initialize_c3sMembership_db development.ini



Run (in development mode)
-------------------------

::

   $ env/bin/pserve development.ini --reload

The app will rebuild templates and reload code whenever there are changes by
using --reload.



Run (in production mode, daemon mode)
-------------------------------------
::

   $ pserve production.ini start

