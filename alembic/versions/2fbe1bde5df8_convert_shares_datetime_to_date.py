"""Convert shares datetime to date.

Revision ID: 2fbe1bde5df8
Revises: 5046d87ce083
Create Date: 2017-03-06 17:15:37.737860

"""

from datetime import (datetime, date)

from alembic import op
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    Unicode,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = '2fbe1bde5df8'
down_revision = 'ae1fedc02b0'

# pylint: disable=invalid-name
Base = declarative_base()


def upgrade():
    """
    Upgrades the database.

    Approach:

    1. A temporary table with the new specification is created and the data is
       converted into this table.
    2. The original table is removed.
    3. The temporary table is renamed to the original table name.

    This approach was chosen because date_of_acquisition has a not nullable
    constrait. Adding a column with a not nullable constraint to a table does
    not work because it cannot be initially empty. Therefore, adding the column
    with a different name, filling the data, removing the original column and
    renaming the temporary one would not work.

    This implementation is specifically for SQLite and might not work with other
    database types.
    """
    bind = op.get_bind()
    session = Session(bind=bind)
    op.create_table(
        'shares_migrated',
        Column('id', Integer, primary_key=True),
        Column('number', Integer()),
        Column('date_of_acquisition', Date(), nullable=False),
        Column('reference_code', Unicode(255), unique=True),
        Column('signature_received', Boolean, default=False),
        Column('signature_received_date', Date(), default=date(1970, 1, 1)),
        Column('signature_confirmed', Boolean, default=False),
        Column('signature_confirmed_date', Date(), default=date(1970, 1, 1)),
        Column('payment_received', Boolean, default=False),
        Column('payment_received_date', Date(), default=date(1970, 1, 1)),
        Column('payment_confirmed', Boolean, default=False),
        Column('payment_confirmed_date', Date(), default=date(1970, 1, 1)),
        Column('accountant_comment', Unicode(255)))
    session.execute("""
        insert into
            shares_migrated
            (
                id
                ,
                number
                ,
                date_of_acquisition
                ,
                reference_code
                ,
                signature_received
                ,
                signature_received_date
                ,
                signature_confirmed
                ,
                signature_confirmed_date
                ,
                payment_received
                ,
                payment_received_date
                ,
                payment_confirmed
                ,
                payment_confirmed_date
                ,
                accountant_comment
            )
        select
            id
            ,
            number
            ,
            substr(date_of_acquisition, 1, 10)
            ,
            reference_code
            ,
            signature_received
            ,
            substr(signature_received_date, 1, 10)
            ,
            signature_confirmed
            ,
            substr(signature_confirmed_date, 1, 10)
            ,
            payment_received
            ,
            substr(payment_received_date, 1, 10)
            ,
            payment_confirmed
            ,
            substr(payment_confirmed_date, 1, 10)
            ,
            accountant_comment
        from
            shares
        """)
    session.flush()
    session.commit()
    op.drop_table('shares')
    op.rename_table('shares_migrated', 'shares')


def downgrade():
    """
    Downgrades the database.

    Approach:

    1. A temporary table with the new specification is created and the data is
       converted into this table.
    2. The original table is removed.
    3. The temporary table is renamed to the original table name.

    This approach was chosen because date_of_acquisition has a not nullable
    constrait. Adding a column with a not nullable constraint to a table does
    not work because it cannot be initially empty. Therefore, adding the column
    with a different name, filling the data, removing the original column and
    renaming the temporary one would not work.

    This implementation is specifically for SQLite and might not work with other
    database types.
    """
    bind = op.get_bind()
    session = Session(bind=bind)
    op.create_table(
        'shares_migrated',
        Column('id', Integer, primary_key=True),
        Column('number', Integer()),
        Column('date_of_acquisition', DateTime(), nullable=False),
        Column('reference_code', Unicode(255), unique=True),
        Column('signature_received', Boolean, default=False),
        Column(
            'signature_received_date',
            DateTime(),
            default=datetime(1970, 1, 1)),
        Column('signature_confirmed', Boolean, default=False),
        Column(
            'signature_confirmed_date',
            DateTime(),
            default=datetime(1970, 1, 1)),
        Column('payment_received', Boolean, default=False),
        Column(
            'payment_received_date',
            DateTime(),
            default=datetime(1970, 1, 1)),
        Column('payment_confirmed', Boolean, default=False),
        Column(
            'payment_confirmed_date',
            DateTime(),
            default=datetime(1970, 1, 1)),
        Column('accountant_comment', Unicode(255)))
    session.execute("""
        insert into
            shares_migrated
            (
                id
                ,
                number
                ,
                date_of_acquisition
                ,
                reference_code
                ,
                signature_received
                ,
                signature_received_date
                ,
                signature_confirmed
                ,
                signature_confirmed_date
                ,
                payment_received
                ,
                payment_received_date
                ,
                payment_confirmed
                ,
                payment_confirmed_date
                ,
                accountant_comment
            )
        select
            id
            ,
            number
            ,
            date_of_acquisition || ' 00:00:00.000000'
            ,
            reference_code
            ,
            signature_received
            ,
            signature_received_date || ' 00:00:00.000000'
            ,
            signature_confirmed
            ,
            signature_confirmed_date || ' 00:00:00.000000'
            ,
            payment_received
            ,
            payment_received_date || ' 00:00:00.000000'
            ,
            payment_confirmed
            ,
            payment_confirmed_date || ' 00:00:00.000000'
            ,
            accountant_comment
        from
            shares
        """)
    session.flush()
    session.commit()
    op.drop_table('shares')
    op.rename_table('shares_migrated', 'shares')
