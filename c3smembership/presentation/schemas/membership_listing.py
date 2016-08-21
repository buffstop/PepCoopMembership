# -*- coding: utf-8 -*-
"""
Form and validation schemas for membership listings.
"""

import datetime

import colander
import deform

from c3smembership.presentation.i18n import _


class MembershipListingDate(colander.Schema):
    """
    Provides a colander schema for entering a date.
    """

    date = colander.SchemaNode(
        colander.Date(),
        title=_('Date'),
        validator=colander.Range(
            max=datetime.date.today(),
            max_err=_('${val} is later than today')),
        default=datetime.date.today())


class MembershipListingYearEnd(colander.Schema):
    """
    Provides a colander schema for selecting a year.
    """

    date = colander.SchemaNode(
        colander.Date(),
        title=_('Year'),
        widget=deform.widget.SelectWidget(
            values=[
                (datetime.date(year, 12, 31), str(year)) \
                for year in reversed(range(2013, datetime.date.today().year))
            ]
        )
    )
