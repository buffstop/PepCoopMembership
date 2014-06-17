import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'alembic',  # migrate the database when introducing new fields
    'Babel',
    'cryptacular',
    'deform',  # should get deform-2.0...
    'fdfgen',
    'lingua',
    'pycountry',  # replacing 'webhelpers',
    'pyramid<1.6a',  # use pyramid 1.5
    'pyramid_beaker',
    'pyramid_chameleon',  # 'pyramid 1.5 extension'
    'pyramid_debugtoolbar',
    'pyramid_mailer',
    'pyramid_tm',
    'python-gnupg',
    'SQLAlchemy',
    'transaction',
    'unicodecsv',
    'waitress',
    'zope.sqlalchemy',
]
# for the translations machinery using transifex you also need to
# "pip install transifex-client"
test_requirements = [
    'coverage',
    'nose',
    'pdfminer',  # and its dependency
    'pyquery',
    'selenium',
    'slate',  # pdf to text helper
    'webtest',
]

if sys.version_info[:3] < (2, 5, 0):
    requires.append('pysqlite')

setup(name='c3smembership',
      version='0.1',
      description='Membership Form for C3S (form, PDF, email)',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Christoph Scheid',
      author_email='christoph@c3s.cc',
      url='http://www.c3s.cc',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='c3smembership',
      install_requires=requires + test_requirements,
      entry_points="""\
      [paste.app_factory]
      main = c3smembership:main
      [console_scripts]
      initialize_c3sMembership_db = c3smembership.scripts.initialize_db:main
      """,
      # http://opkode.com/media/blog/
      #        using-extract_messages-in-your-python-egg-with-a-src-directory
      message_extractors={
          'c3smembership': [
              ('**.py', 'lingua_python', None),
              ('**.pt', 'lingua_xml', None),
          ]},
      )
