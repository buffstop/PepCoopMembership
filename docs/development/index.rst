===========
Development
===========


The following section describes important concepts which are used for
developing the c3sMembership application.



.. _tracking_changes:

----------------
Tracking Changes
----------------


The application contains a `MarkDown <http://daringfireball.net/projects/
markdown/>`_ formated file named ``CHANGES.md`` describing all the changes
made for a specific release.

New development which has not been released yet is documented on the top
of the document below the section "Next Release".

At the time of the release, this headline has to be changed to the
corresponding release number.

Changes should be documented with each single commit. They can be rewritten,
combined and sumarized later on if it seems appropiate.



---------------
Branching Model
---------------


The development uses a branching model which is similar to `GitFlow
<https://de.atlassian.com/git/tutorials/comparing-workflows/gitflow-
workflow>`_ as `proposed by Vincent Driessen <http://nvie.com/posts/a-
successful-git-branching-model/>`_ with some minor modifications.



The Master Branch
=================


The basic idea is that the master branch is always in a stable state (opposed
to Vincent Driessen's GitFlow where it only contains final releases).
Currently it is our opinion that it is easier to keep the master branch as the
main branch for development as developers who are not familiar with GitFlow
will use it for this purpose anyway.



Feature Branches
================


For the development of new features, a new feature branch is created from
master. They follow the naming convention ``feature/1234`` with 1234 being
the issues id in the `C3S issue tracker <https://chili.c3s.cc>`_.

.. code-block:: console

   $ git checkout master
   $ git branch feature/1234
   $ git checkout feature/1234

After the development is finished and the code tested, the feature
branch is merged into the master branch.

.. code-block:: console

   $ git checkout master
   $ git merge feature/1234
   $ git push origin master

After being merged into the master branch, feature branches are removed
from the repository, locally as well as on the remote.

.. code-block:: console

   $ # Delete the feature branch locally.
   $ git branch -d feature/1234
   $ # Delete the feature branch on the origin remote.
   $ git push origin :feature/1234


.. _release_branches:

Release Branches
================

At some point the development aims for a release. At this point a release
branch is created from the master branch. The naming convention for release
branches is ``release/1.2.3`` with 1.2.3 being the version number of the
coming release according to `Semantic Versioning Specification
<http://semver.org/>`_.

.. code-block:: console

   $ git checkout master
   $ git branch release/1.2.3
   $ git checkout release/1.2.3

This release branch separates the release development
from the parallel development of new features. From this point on release
fixes are only performed on the release branch.

Release branches are removed from the local and remote repository after the
release was made final (see :ref:`the_release`).

.. code-block:: console

   $ # Delete the release branch locally.
   $ git branch -d release/1.2.3
   $ # Delete the release branch on the origin remote
   $ git push origin :release/1.2.3



.. _the_uat_branch:

The UAT Branch
==============


A release at C3S goes through user acceptance tests (UAT) in which the users
check the application for issues. It seems convenient to have a corresponding
branch named "uat" which the states of the UAT system. Therefore, when UAT
starts, the release branch is merged into the uat branch.

.. code-block:: console

   $ git checkout uat
   $ git merge release/1.2.3
   $ git push origin uat

On the UAT system only needs to pull to get the designated code version.

.. code-block:: console

   user@uat:~/c3sMembership$ git pull

Fixes during UAT are performed on the release branch and merged into the uat
branch when the next version is ready for testing.

No commits are made to the uat branch except for merges with release branches.



.. _the_release:

The Release
===========


Once the release passes UAT, it is made final. At this point the version
number in CHANGE.md (see :ref:`tracking_changes`) as well as the file 
`__init__.py <https://github.com/C3S/c3sMembership/blob/master/
c3smembership/__init__.py>`_ which defines the python package version at its
top.

The repository then gets assigned the final version number as a git tag and
is listed as a release in the `c3sMembership Github repository <https://
github.com/C3S/c3sMembership/releases>`_. The commit creating the tag should
contain all changes of the release from ``CHANGES.MD`` as its commit message.

.. code-block:: console

   $ git checkout release/1.2.3
   $ # Change "Next Release" in CHANGES.md to 1.2.3:
   $ nano CHANGES.md
   $ # Set the version number in __init__.py to 1.2.3:
   $ nano __init__.py
   $ git commit -m "Set version number to 1.2.3."
   $ git push release/1.2.3
   $ # Copy change notes from CHANGES.md to the commit message of the tag:
   $ git tag -a 1.2.3
   $ git push origin 1.2.3

Once the release is final, the code gets merged back into master and the
release branch gets removed:

.. code-block:: console

   $ git checkout master
   $ git merge release/1.2.3
   $ git push origin master
   $ # Delete the release branch locally.
   $ git branch -d release/1.2.3
   $ # Delete the release branch on the origin remote.
   $ git push origin :release/1.2.3



The Production Branch
=====================


Similar to the uat branch a branch named "production" is maintained
representing the state of the production server running the application.
Therefore, the final release gets merged into the production branch.

.. code-block:: console

   $ git checkout production
   $ git merge 1.2.3
   $ git push origin production

A pull command gets the production server the code it needs:

.. code-block:: console

   user@prod:~/c3sMembership$ git pull

No commits are made to the production branch except for merges with final
releases.



Hotfix Branches
===============


Hotfix branches are somewhat similar to :ref:`release_branches`. They are
created in case a fix needs to be performed on the production state
without wanting to integrate the fix into the normal feature release process.

The reason for not going through the normal feature release process might be
that it would take too much time. When fixing an issues via a feature
branch and merging it into the master branch afterwards, not only the fix
goes through the normal release process but all new features which have been
developed since the last release and which already reside on the master
branch.

Instead, a hotfix branch can be created from the production branch.

.. code-block:: console

   $ git checkout production
   $ git branch hotfix/1.2.3
   $ git checkout hotfix/1.2.3

Hotfixes should also go through the UAT phase in case they require user
testing and approval.

The release process of hotfixes does not differ from the one which applies to
:ref:`release_branches`. Hotfixes can be seen as special release branches
which just branch from production instead of master.

Hotfix branches are removed from the local and remote repository after
:ref:`the_release` was made final.

.. code-block:: console

   $ # Delete the release branch locally.
   $ git branch -d hotfix/1.2.3
   $ # Delete the release branch on the origin remote
   $ git push origin :hotfix/1.2.3



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
table *alembic_version*. The table contains a single column and a single row
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

