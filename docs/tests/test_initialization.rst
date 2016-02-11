.. _test_docs_initialization:


Tests Database Initialization
-------------------------------

The c3sMembership app needs a database both for persistence of applications for
membership (and accepted members) and for user accounting (staff login),
amongst other things.
When the app is started, a database must exist,
otherwise most things will not work properly.

The script *initialize_c3sMembership_db* can be used to set up a minimal database.
There are tests for this:

.. automodule:: test_initialization
    :members:
    :member-order: bysource
