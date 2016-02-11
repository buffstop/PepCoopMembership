import os
import unittest
# import subprocess

# from c3smembership import scripts  # just to trigger coverage
# from c3smembership.scripts.initialize_db import init_50


class TestDBInitialization(unittest.TestCase):
    """
    tests for the database initialization scripts
    """
    print("--------------------------------------------------------------")
    print("-- tests for the initialize_db script (output unsuppressed)")

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_usage(self):
        from c3smembership.scripts.initialize_db import usage
        argv = ['initialize_c3sMembership_db']
        try:  # we will hit SystemExit: 1
            result = usage(argv)
            print("the result: %s" % result)
        except:
            # print ("caught exception!")
            pass
        print("--------------------------------------------------------------")

    # def test_usage_process(self):
    #     try:
    #         res = subprocess.check_output(
    #             ['env/bin/initialize_c3sMembership_db'])
    #         #print res
    #     except subprocess.CalledProcessError, cpe:
    #         #print("return code: %s" % cpe.returncode)
    #         #print("output: %s" % cpe.output)
    #         self.assertTrue(cpe.returncode is 1)
    #         self.assertTrue(
    #           'usage: initialize_c3sMembership_db <config_uri>' in cpe.output
    #         )

    def test_init(self):
        from c3smembership.scripts.initialize_db import init
        result = init()
        print(result)

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
            result = main(argv)
        argv = ['notExisting.ini', ]
        with self.assertRaises(SystemExit) as cm:
            result = main(argv)
            result  # apease flake8
        self.assertEqual(cm.exception.code, 1)
        print("--------------------------------------------------------------")

    def test_main_correct(self):
        """
        test the initialize_c3sMembership_db script with correct arguments
        """
        from c3smembership.scripts.initialize_db import main
        filename = 'webdrivertest.db'
        if os.path.isfile(filename):
            os.unlink(filename)  # delete file if present
        argv = ['initialize_c3sMembership_db', 'webdrivertest.ini']
        result = main(argv)
        result  # apease flake8
        print("--------------------------------------------------------------")
