# -*- coding: utf-8 -*-

import os
import unittest

from c3smembership.data.model.base import DBSession


class TestDBInitialization(unittest.TestCase):
    """
    Tests for the database initialization scripts.
    """

    def test_usage(self):
        from c3smembership.scripts.initialize_db import usage
        argv = ['initialize_c3sMembership_db']
        try:
            usage(argv)
        except:
            pass
        DBSession.close()
        DBSession.remove()

    def test_init(self):
        from c3smembership.scripts.initialize_db import init
        init()
        DBSession.close()
        DBSession.remove()

    def test_main_false(self):
        """
        test the initialize_c3sMembership_db script with faulty arguments

        get it wrong: wrong arguments:
        * must be at least one argument
        * must be name of an existing file

        this gets coverage for the "usage" function in scripts/initialize_db.py
        """
        from c3smembership.scripts.initialize_db import main
        argv = []
        with self.assertRaises(IndexError):
            main(argv)
        argv = ['notExisting.ini', ]
        with self.assertRaises(SystemExit) as context:
            main(argv)
        self.assertEqual(context.exception.code, 1)
        DBSession.close()
        DBSession.remove()

    def test_main_correct(self):
        """
        test the initialize_c3sMembership_db script with correct arguments
        """
        from c3smembership.scripts.initialize_db import main
        filename = 'webdrivertest.db'
        if os.path.isfile(filename):
            os.unlink(filename)
        argv = ['initialize_c3sMembership_db', 'webdrivertest.ini']
        main(argv)
        DBSession.close()
        DBSession.remove()
