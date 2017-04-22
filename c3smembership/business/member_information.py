# -*- coding: utf-8 -*-
"""
Provides member information.
"""


class MemberInformation(object):
    """
    Provides member information.
    """

    def __init__(self, member_repository):
        """
        Initialises the MemberInformation object.

        Args:
            member_repository: The member repository object used to access
                member data.
        """
        self._member_repository = member_repository

    def get_accepted_members_count(self, effective_date=None):
        """
        Gets all members which have been accepted until and including the
        specified effective date sorted by lastname ascending and firstname
        ascending.

        Args:
            effective_date: Optional. The date on which the membership has been
                accepted. If not specified system date is used as effective
                date.

        Returns:
            All members which have been accepted until and including the
            specified effective date sorted by lastname ascending and firstname
            ascending.
        """
        return self._member_repository.get_accepted_members_count(
            effective_date)

    def get_accepted_members_sorted(self, effective_date=None):
        """
        Gets all members which have been accepted until and including the
        specified effective date.

        Args:
            effective_date: Optional. The date on which the membership has been
                accepted. If not specified system date is used as effective
                date.

        Returns:
            All members which have been accepted until and including the
            specified effective date.
        """
        return self._member_repository.get_accepted_members_sorted(
            effective_date)
