"""Test module for c3smembership.GitTools."""

import unittest
import subprocess
import mock

from c3smembership.git_tools import GitTools


class TestGitTools(unittest.TestCase):
    """Testing c3smembership.GitTools.

    The testing of c3smembership.GitTools is performed using the mock package
    to mock subprocess.check_output.
    """

    def __test_check_output_result(
            self,
            args,
            method,
            check_output_result,
            method_expected_output):
        """Mock subprocess.check_output to return check_output_result and
        call method.

        The method subprocess.check_output is mocked and will return
        check_output_result. The method is called invoking check_output.
        Finally, checks are performed that check_output was called with
        args and that method returned method_expected_output.
        """
        with mock.patch('c3smembership.git_tools.subprocess.check_output') \
                as check_output:
            check_output.return_value = check_output_result
            method_output = method()
            check_output.assert_called_once_with(args)
            self.assertEqual(method_output, method_expected_output)

    def __test_check_output_exception(
            self,
            args,
            method,
            method_expected_output):
        """Mock subprocess.check_output to raise CalledProcessError

        The method subprocess.check_output is mocked and will raise a
        CalledProcessError exception. The method is called invoking
        check_output. Finally, checks are performed that check_output was
        called with args and that method returned method_expected_output.
        """
        exception = subprocess.CalledProcessError(1, '', None)
        with mock.patch('c3smembership.git_tools.subprocess.check_output', \
                side_effect=exception) as check_output:
            method_output = method()
            check_output.assert_called_once_with(args)
            self.assertEqual(method_output, method_expected_output)

    def test_get_commit_hash(self):
        """Test method c3smembership.GitTools.get_commit_hash().

        Test for success and failure. Mocking is used to simulate behaviour
        of subprocess.check_output.
        """
        args = ['git', 'rev-parse', 'HEAD']
        check_output_return_value = '0123456789abcdefghijklmnopqrstuvwxyz'
        # test success
        self.__test_check_output_result(
            args,
            GitTools.get_commit_hash,
            check_output_return_value,
            check_output_return_value)
        # test failure
        self.__test_check_output_exception(
            args,
            GitTools.get_commit_hash,
            None)

    def test_get_tag(self):
        """Test method c3smembership.GitTools.get_tag().

        Test for success and failure. Mocking is used to simulate behaviour
        of subprocess.check_output.
        """
        args = ['git', 'describe', 'HEAD']
        check_output_return_value = 'v1.2.3-14-g0123456'
        # test success
        self.__test_check_output_result(
            args,
            GitTools.get_tag,
            check_output_return_value,
            check_output_return_value)
        # test failure
        self.__test_check_output_exception(
            args,
            GitTools.get_tag,
            None)

    def test_get_github_base_url(self):
        """Test method c3smembership.GitTools.get_github_base_url().

        Test for success and failure. Mocking is used to simulate behaviour
        of subprocess.check_output.
        """
        args = ['git', 'config', '--get', 'remote.origin.url']
        expected_return_value = 'https://github.com/user/test123456789'

        # test success
        check_output_return_values = [
            'https://github.com/user/test123456789',
            'https://github.com/user/test123456789.git',
            'https://www.github.com/user/test123456789',
            'https://www.github.com/user/test123456789.git',
        ]
        for check_output_return_value in check_output_return_values:
            self.__test_check_output_result(
                args,
                GitTools.get_github_base_url,
                check_output_return_value,
                expected_return_value)
        # test failure
        self.__test_check_output_exception(
            args,
            GitTools.get_github_base_url,
            None)

