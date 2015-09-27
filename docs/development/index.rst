===========
Development
===========


The following section describes important concepts which are used for
developing the c3sMembership application.



------------------
Database Migration
------------------

c3sMembership uses `Alembic <https://alembic.readthedocs.org/en/latest/>`_ for
database migration.

When development changes the database model, a migration script needs to be
created which migrates the existing database from the old model to the new
model. For example, new tables are created, columns are added to 
tables or removed from them. Alembic provides functionality to auto-generate
basic scripts for the migration as well as executing the migration scripts for
upgrading and downgrading the database.

The configuration is stored in the file alembic.ini which is part of the
repository. Amongst other settings it configures the path to the migration
scripts and the database url. All commands for using Alembic need to be
executed in the folder which contains the alembic.ini configuration file.

Like GIT, Alembic identifies the version of a database by a hash value. It
stores the current version of the database inside the database in the
table alembic_versions. The table contains a single column and a single row
with the hash value identifying the database's version.

There are three important steps to consider when changing the data model.

1. Auto-generating and if necessary adjusting the migration scripts.

2. Upgrading the database to the changed model.

3. Downgrading the database to a previous model when rolling back changes.



Auto-Generating Migration Scripts
=================================


Alembic supports auto-generation of the database migration scripts. This
command creates a new revision, i.e. a new migration script, representing the
recent changes to the database model.

It is important to note that the auto-generated migration scripts only concern
the database's structure. The migration of data in particular is not part of
the auto-generated migration scripts. If the change to the database model
assumes that data previously stored in one column of a table now resides in
another column of another table, the commands to perform this transformation
of the data during the migration needs to be added manually.

.. code-block:: shell

   $ alembic revision --autogenerate -m "Some message"

Alembic then generates a script inside the configured path. The filename
starts with the hash value identifying the version and ends with the filename
compatible string of "Some message". The generated script contains the 
revision's hash, the hash of the previous version as well as two functions
*upgrade()* and *downgrade()*. These functions need to be checked and probably
adjusted as the auto-generation functionality is very basic.



Upgrading the Database
======================


The following command lets Alembic upgrade the database to the most recent
version:

.. code-block:: shell

   $ alembic upgrade head

It is also possible to upgrade to a certain version of the database by passing
the version's identifying hash value to the upgrade command:

.. code-block:: shell

   $ alembic upgrade 712149474d9



Downgrading the Database
========================


Similar to upgrading the database, Alembic can also downgrade it. The commandis:

.. code-block:: shell

   $ alembic downgrade 712149474d9



--------------------
Internationalization
--------------------


Refreshing the internationalization or short i18n (for the 18 characters left
out) uses three stages:

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

