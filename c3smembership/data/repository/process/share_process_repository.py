# -*- coding: utf-8  -*-
"""
Repository to initiate and operate share processes as well as retrieving share
process information.
"""

from c3smembership.data.model.base import DBSession
from c3smembership.models import (
    C3sMember,
    Shares,
    members_shares,
)


class ShareProcessRepository(object):
    """
    Repository class for shares processes.
    """

    @classmethod
    def get_member_processes(cls, membership_number):
        """
        Gets the share processes of a members.

        Args:
            membership_number: The membership number of the member of which the
                share processes are returned.

        Returns:
            The share processes of the member.
        """
        return DBSession.query(Shares) \
            .join(members_shares) \
            .join(C3sMember) \
            .filter(C3sMember.membership_number == membership_number) \
            .all()
