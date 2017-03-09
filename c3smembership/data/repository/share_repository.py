# -*- coding: utf-8  -*-
"""
Repository to initiate and operate shares as well as retrieving share
information.
"""

from datetime import date

from sqlalchemy import Date
from sqlalchemy.sql import (
    func,
    expression
)

from c3smembership.data.model.base import DBSession
from c3smembership.models import (
    C3sMember,
    Shares,
    members_shares,
)


class ShareRepository(object):
    """
    Repository class for shares.
    """

    @classmethod
    def get_member_shares(cls, membership_number):
        """
        Gets the share of a members.

        Args:
            membership_number: The membership number of the member of which the
                shares are returned.

        Returns:
            The shares of the member.
        """
        return DBSession.query(Shares) \
            .join(members_shares) \
            .join(C3sMember) \
            .filter(C3sMember.membership_number == membership_number) \
            .all()

    @classmethod
    def get_approved(cls, start_date, end_date):
        """
        Gets all shares approved between and including both start date and end
        date.

        Args:
            start_date: The first date for which approved shares are returned.
            end_date: The last date for which approved shares are returned.

        Returns:
            All shares approved between and including both start date and end
            date.
        """
        return DBSession.query(Shares).filter(
            expression.and_(
                Shares.date_of_acquisition >= start_date,
                Shares.date_of_acquisition <= end_date)).all()

    @classmethod
    def get_approved_count(cls, start_date, end_date):
        """
        Gets the number of all shares approved between and including both start
        date and end date.

        Args:
            start_date: The first date for which approved shares are counted.
            end_date: The last date for which approved shares are counted.

        Returns:
            The number of all shares approved between and including both start
            date and end date.
        """
        count = DBSession.query(func.sum(Shares.number)).filter(
            expression.and_(
                Shares.date_of_acquisition >= start_date,
                Shares.date_of_acquisition <= end_date)).scalar()
        if count is None:
            count = 0
        return count

    @classmethod
    def get_paid_not_approved(cls, start_date, end_date):
        """
        Gets all shares which are paid between and including both start date and
        end date but not paid until after the end date.

        Args:
            start_date: The first date for which shares are returned.
            end_date: The last date for which share are returned.

        Returns:
            All shares which are paid between and including both start date and
            end date but not paid until after the end date.

            Attributes:
                id: The technical primary key of the member
                lastname: The last name of the member
                firstname: The first name of the member
                shares_count: The number of shares
                payment_received_date: The payment date for the shares
        """
        return cls._get_paid_not_approved_query(
            'data',
            start_date,
            end_date
        ).all()

    @classmethod
    def get_paid_not_approved_count(cls, start_date, end_date):
        """
        Gets the number of all shares paid between and including both start date
        and end date but not paid after end date.

        Args:
            start_date: The first date for which shares are counted.
            end_date: The last date for which share are counted.

        Returns:
            The number of all shares paid between and including both start date
            and end date but not paid after end date.
        """
        query = cls._get_paid_not_approved_query(
            'shares_count',
            start_date,
            end_date)
        count = query.scalar()
        if count is None:
            count = 0
        return count

    @classmethod
    def _get_paid_not_approved_query(cls, query_type, start_date, end_date):
        """
        Gets the query for paid but not approved shares between and including
        start and end date.

        Args:
            query_type: The type of the query to be build. 'data' for retrieving
                rows and 'shares_count' for an aggregate count query.
            start_date: The first date of which paid and not approved shares are
                considered.
            end_date: The last date of which paid and not approved shares are
                considered.

        Returns:
            A query according to the specified query_type.

            For 'data' the query is build to retrieve rows with attributes 'id'
            for member id, 'lastname' for the member's lastname, 'firstname' for
            the member's firstname, 'shares_count' for the number of shares and
            'payment_received_date' for the date on which the payment was
            received

            For 'shares_count' an aggregate count query is returned to retrieve
            the number of shares of all relevant shares packages.
        """
        # Shares which of the day of the request have not been approved are not
        # yet stored in Shares but only available on the C3sMember.
        shares_count = expression.case(
            [(Shares.id == None, C3sMember.num_shares)],
            else_=Shares.number
        )
        payment_received_date = expression.case(
            [(
                Shares.id == None,
                # C3sMember.payment_received_date has the data type DateTime but
                # Date is required as it is used in
                # Shares.payment_received_date. As CAST on DateTime '2017-01-02
                # 12:23:34.456789' returns '2017' in SQLite and therefore cannot
                # be used substring is used instead and then SQLAlchemy is
                # forced by type_coerce to parse it as a Date column.
                expression.type_coerce(
                    func.substr(C3sMember.payment_received_date, 1, 10), Date)
            )],
            else_=Shares.payment_received_date
        )
        date_of_acquisition = expression.case(
            [(Shares.id == None, C3sMember.membership_date)],
            else_=Shares.date_of_acquisition
        )

        if query_type == 'data':
            query = DBSession.query(
                C3sMember.id,
                C3sMember.lastname,
                C3sMember.firstname,
                shares_count.label('shares_count'),
                payment_received_date.label('payment_received_date'),
            )
        if query_type == 'shares_count':
            query = DBSession.query(
                func.sum(shares_count)
            )
        # Use outer joins as Shares do not have to exist yet.
        return query.select_from(C3sMember) \
            .outerjoin(members_shares) \
            .outerjoin(Shares) \
            .filter(
                expression.and_(
                    # membership not approved in time period
                    expression.or_(
                        # membership or share approved later than end date
                        date_of_acquisition > end_date,
                        # or membership or share not approved yet (default date)
                        date_of_acquisition == date(1970, 1, 1),
                    ),
                    # payment received in time period
                    payment_received_date >= start_date,
                    payment_received_date <= end_date,
                )
            )
