# -*- coding: utf-8 -*-
"""
Provides share information.
"""


# pylint: disable=too-few-public-methods
class ShareInformation(object):
    """
    Provides share statistics.
    """

    def __init__(self, share_repository):
        """
        Initialises the ShareInformation object.

        Args:
            share_repository: The share repository providing the statistics
                methods get_approved, get_approved_count, get_paid_not_approved
                and get_paid_not_approved_count.
        """
        self.share_repository = share_repository

    def get_statistics(self, start_date, end_date):
        """
        Gets share statistics.

        Args:
            start_date: The start date of the statistics time period.
            end_date: The end date of the statistics time period.

        Returns:
            A dictionary with the keys 'new_shares' containing an array of
            shares acquired during the time period, 'count_shares' containing
            the number of shares acquired during the time period,
            'shares_paid_unapproved' containing an array of shares which are
            paid but not apporved by the administration board during the time
            period, 'shares_paid_unapproved_count' containing the number of
            shares which are paid but not apporved by the administration board
            during the time period.
        """
        statistics = {}
        statistics['approved_shares'] = \
            self.share_repository.get_approved(start_date, end_date)
        statistics['approved_shares_count'] = \
            self.share_repository.get_approved_count(start_date, end_date)
        statistics['paid_not_approved_shares'] = \
            self.share_repository.get_paid_not_approved(start_date, end_date)
        statistics['paid_not_approved_shares_count'] = \
            self.share_repository.get_paid_not_approved_count(
                start_date, end_date)
        return statistics

    def get_share_count(self, effective_date=None):
        """
        Gets the total number of shares at the effective date.

        Args:
            effective_date: Optional. The date for which the number of shares is
                calculated.

        Returns:
            The total number of shares at the effective date.
        """
        return self.share_repository.get_share_count(effective_date)

    def get_member_share_count(self, membership_number, effective_date=None):
        """
        Gets the number of shares of the member on the effective date.

        Args:
            membership_number: The membership number of the member for which the
                number of shares is calculated.
            effective_date: Optional. The date for which the number of shares
                for the member is calculated.
        """
        return self.share_repository.get_member_share_count(
            membership_number,
            effective_date)
