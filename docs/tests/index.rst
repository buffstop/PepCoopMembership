=======
Testing
=======

All code should be tested. That is easily said, sometimes hard to do.
But with pyramid it is possible.

Test frameworks
---------------

We use a combination of Unit tests, Webtest and Selenium/webdriver tests.
Each have their pros and cons.
Selenium for example does (depending on how it is used or how the app is invoked)
not give valid coverage information. (This is a TODO to work on and improve.)

Test code should reside in a folder *tests/* and in files starting with *test_*.

The entire set of tests can be run with *nose*:
::

   env/bin/nosetests c3smembership/


We also look at **coverage** to see if the tests touched all code.

Continuous Integration
----------------------

We have a Jenkins instance run our codes tests after every new commit.


Test Documentation
------------------

The documentation particles below are generated from the docstrings in the
actual Python test code. 


.. toctree::
   :maxdepth: 2
   :glob:

   *
