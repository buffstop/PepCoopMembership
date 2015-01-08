# -*- coding: utf-8 -*-
"""Provides methods to access git information."""

import subprocess
import re

class GitTools(object):
    """Provides methods to access git information."""

    @classmethod
    def get_commit_hash(cls):
        """Returns the current git commit hash."""
        git_commit_hash = None
        try:
            git_commit_hash = subprocess.check_output([
                'git', 'rev-parse', 'HEAD'])
        except subprocess.CalledProcessError:
            pass
        return git_commit_hash

    @classmethod
    def get_tag(cls):
        """Returns the current tag."""
        git_tag = None
        try:
            git_tag = subprocess.check_output(
                ['git', 'describe', 'HEAD'])
        except subprocess.CalledProcessError:
            pass
        return git_tag

    @classmethod
    def get_github_base_url(cls):
        """Returns the Github base URL if any.

        If the origin remote references Gibhut, the base URL is returned.
        """
        github_base_url = None
        try:
            git_remote_url = subprocess.check_output(
                ['git', 'config', '--get', 'remote.origin.url'])
            match = re.search(
                '^https://(?P<www>www.)?github.com/(?P<user>' + \
                    '[A-Za-z0-9]+)/(?P<project>[A-Za-z0-9]+)(.git)?$',
                git_remote_url)
            if match is not None and match.groups():
                github_base_url = 'https://github.com/{0}/{1}'.format(
                    match.group('user'),
                    match.group('project'))
        except subprocess.CalledProcessError:
            pass
        return github_base_url

    @classmethod
    def get_github_commit_url(cls):
        """Return the Github URL to the current commit if any.

        If the origin remote references Github, the URL to the current
        commit is returned.
        """
        github_commit_url = None
        git_commit = cls.get_commit_hash()
        github_base_url = cls.get_github_base_url()
        if git_commit is not None and github_base_url is not None:
            github_commit_url = '{0}/commit/{1}'.format(
                github_base_url,
                git_commit)
        return github_commit_url


