# -*- coding: utf-8  -*-
"""
Repository for accessing and operating with member data.
"""

from sqlalchemy.sql import func
from datetime import date

from c3smembership.data.model.base import DBSession
from c3smembership.models import C3sMember


class MemberRepository(object):
    """
    Repository for members.
    """

    @classmethod
    def get_member(cls, membership_number):
        """
        Gets the member of the specified membership number.

        Args:
            membership_number: The membership number of the member which is
                returned.

        Returns:
            The membership of the specified membership number.
        """
        # pylint: disable=no-member
        return DBSession.query(C3sMember).filter(
            C3sMember.membership_number == membership_number).first()

    @classmethod
    def get_accepted_members(cls, effective_date=None):
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
        return cls._accepted_members_query(effective_date).all()

    @classmethod
    def get_accepted_members_sorted(cls, effective_date=None):
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
        return cls._accepted_members_query(effective_date).order_by(
            C3sMember.lastname.asc(),
            C3sMember.firstname.asc()).all()

    @classmethod
    def _accepted_members_query(cls, effective_date=None):
        """
        Gets the query to retrieve members accepted until and including the
        specified effective date.

        Args:
            effective_date: Optional. The date on which the membership has been
                accepted. If not specified system date is used as effective
                date.

        Returns:
            The query to retrieve members accepted until and including the
            specified effective date.
        """
        # pylint: disable=no-member
        all_members_query = DBSession.query(C3sMember)
        accepted_members_query = cls._filter_accepted_member(
            all_members_query,
            effective_date)
        return accepted_members_query

    @classmethod
    def get_accepted_members_count(cls, effective_date=None):
        """
        Gets the number of members which have been accpeted until and including
        the specified effective date.

        Args:
            effective_date: Optional. The date on which the membership has been
                accepted. If not specified system date is used as effective
                date.

        Returns:
            The number of members which have been accpeted until and including
            the specified effective date.
        """
        # pylint: disable=no-member
        all_members_count_query = DBSession.query(func.count(C3sMember.id))
        accepted_members_count_query = cls._filter_accepted_member(
            all_members_count_query,
            effective_date)
        return accepted_members_count_query.scalar()

    @classmethod
    def _filter_accepted_member(cls, query, effective_date=None):
        """
        Gets the filter for the query to retrieve members accepted until and
        including the specified effective date.

        Args:
            effective_date: Optional. The date on which the membership has been
                accepted. If not specified system date is used as effective
                date.

        Returns:
            The filter for the query to retrieve members accepted until and
            including the specified effective date.
        """
        if effective_date is None:
            effective_date = date.today()
        return query \
            .filter(C3sMember.membership_number != None) \
            .filter(C3sMember.membership_accepted) \
            .filter(C3sMember.membership_date <= effective_date)
