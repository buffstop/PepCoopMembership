.. _tracking_changes:

----------------
Tracking Changes
----------------


The application contains a `reStructuredText <http://docutils.sourceforge.net/
rst.html>`_ formatted file named ``CHANGES.rst`` describing all the changes
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


A release at C3S goes through user acceptance tests (UAT)
in which the users check the application for issues,
rigorously checking functionality of the newly developed features.

It seems convenient to have a corresponding branch named "uat"
with the states of the UAT system. Therefore, when UAT
starts, the release branch is merged into the *uat* branch.

.. code-block:: console

   $ git checkout uat
   $ git merge release/1.2.3
   $ git push origin uat

On the UAT system one only needs to *pull* to get the designated code version.

.. code-block:: console

   user@uat:~/c3sMembership$ git pull

Fixes during UAT are performed on the release branch and merged into the *uat*
branch when the next version is ready for testing.

No commits are made to the *uat* branch except for merges with release branches.



.. _the_release:

The Release
===========


Once the release passes UAT, it is made final. At this point the version
number in ``CHANGES.rst`` (see :ref:`tracking_changes`) as well as in the file 
`version.py <https://github.com/C3S/c3sMembership/blob/master/
c3smembership/version.py>`_ which defines the python package version.
.. XXX TODO there is a verb missing near the end of the preceeding sentence!
.. XXX TODO maybe "are synced"?

The repository then gets assigned the final version number as a git tag and
is listed as a release in the `c3sMembership Github repository <https://
github.com/C3S/c3sMembership/releases>`_. The commit creating the tag should
contain all changes of the release from ``CHANGES.rst`` as its commit message.

.. code-block:: console

   $ git checkout release/1.2.3
   $ # Change "Next Release" in CHANGES.rst to 1.2.3:
   $ nano CHANGES.rst
   $ git add CHANGES.rst
   $ # Set the version number in VERSION to 1.2.3:
   $ nano VERSION
   $ git add VERSION
   $ # Commit and push to remote:
   $ git commit -m "Set version number to 1.2.3."
   $ git push origin release/1.2.3
   $ # Copy change notes from CHANGES.rst to the commit message of the tag:
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
   $ # Merging the new release into production is possible as
   $ # fast-forward without merge commit.
   $ git merge 1.2.3 --ff-only
   $ git push origin production

No commits are made to the production branch. It is merely a pointer to the
release which is currently determined for the production server.

The new application version can now be installed on the production server:

.. code-block:: console

   me@prod:~$ # Create application backup including virtual environment
   me@prod:~$ tar -cvzf c3sMembership.$(date "+%Y-%m-%d_%H-%M-%S").tgz c3sMembership
   me@prod:~$ # Stash production configuration
   me@prod:~$ cd c3sMembership
   me@prod:~/c3sMembership$ git stash
   me@prod:~/c3sMembership$ # Pull new release from production branch
   me@prod:~/c3sMembership$ git pull
   me@prod:~/c3sMembership$ # Pull from private certificate repository
   me@prod:~/c3sMembership$ cd certificate
   me@prod:~/c3sMembership/certificate$ git pull
   me@prod:~/c3sMembership/certificate$ cd ..
   me@prod:~/c3sMembership$ # Re-apply stashed configuration
   me@prod:~/c3sMembership$ git stash pop
   me@prod:~/c3sMembership$ # Install new application version and dependencies
   me@prod:~/c3sMembership$ env/bin/python setup.py develop
   me@prod:~/c3sMembership$ # Create database backup
   me@prod:~/c3sMembership$ cp c3sMembership.db c3sMembership.db.$(date "+%Y-%m-%d_%H-%M-%S")
   me@prod:~/c3sMembership$ # Migrate database if necessary (changed models.py?)
   me@prod:~/c3sMembership$ env/bin/alembic upgrade head
   me@prod:~/c3sMembership$ # Build documentation
   me@prod:~/c3sMembership$ cd docs
   me@prod:~/c3sMembership/docs$ make html
   me@prod:~/c3sMembership/docs$ # Restart the web server
   me@prod:~/c3sMembership/docs$ sudo service apache2 restart



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

