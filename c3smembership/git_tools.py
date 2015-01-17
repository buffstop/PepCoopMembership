# -*- coding: utf-8 -*-
"""Provides methods to access git information."""

import subprocess
import re

class GitTools(object):
    """Provides methods to access git information."""

    @classmethod
    def __execute_shell_command(cls, command):
        """Encapsulates the execution of a shell command.

        Performs the execution of the shell command and handles the result.
        If an error occurred, the result will be None. Otherwise the
        strout value will be returned as a stripped string.
        """
        try:
            git = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                universal_newlines=True)
        except Exception:
            # catch any exception which might be raised by the child process
            return None
        stdout_value, stderr_value = git.communicate()
        if stderr_value != '' or len(stdout_value) < 1:
            return None
        return stdout_value.strip()


    @classmethod
    def get_commit_hash(cls):
        """Returns the current git commit hash."""
        return cls.__execute_shell_command(
            'git rev-parse HEAD')


    @classmethod
    def get_branch(cls):
        """Returns the current branch name."""
        return cls.__execute_shell_command(
            'git rev-parse --abbrev-ref HEAD')


    @classmethod
    def get_tag(cls):
        """Returns the current tag name."""
        return cls.__execute_shell_command('git describe HEAD')


    @classmethod
    def get_github_base_url(cls):
        """Returns the Github base URL if any.

        If the origin remote references Gibhut, the base URL is returned.
        """
        git_remote_url = cls.__execute_shell_command(
            'git config --get remote.origin.url')
        if git_remote_url is None:
            return None
        match = re.search(
            '^(?P<protocol>(https|git))://(?P<www>www.)?github.com/' + \
                '(?P<user>[A-Za-z0-9]+)/(?P<repository>[A-Za-z0-9]+)(.git)?$',
            git_remote_url)
        if match is not None and match.groups():
            return 'https://github.com/{0}/{1}'.format(
                match.group('user'),
                match.group('repository'))
        else:
            return None


    @classmethod
    def get_github_commit_url(cls):
        """Return the Github URL to the current commit if any.

        If the origin remote references Github, the URL to the current
        commit is returned.
        """
        git_commit = cls.get_commit_hash()
        github_base_url = cls.get_github_base_url()
        if git_commit is not None and github_base_url is not None:
            return '{0}/commit/{1}'.format(
                github_base_url,
                git_commit)
        else:
            return None


    @classmethod
    def get_github_branch_url(cls):
        """Return the Github URL to the current branch.

        If the origin remote references Github, the URL to the current
        branch is returned.
        """
        git_branch = cls.get_branch()
        github_base_url = cls.get_github_base_url()
        if git_branch is not None and github_base_url is not None:
            return '{0}/tree/{1}'.format(
                github_base_url,
                git_branch)
        else:
            return None
