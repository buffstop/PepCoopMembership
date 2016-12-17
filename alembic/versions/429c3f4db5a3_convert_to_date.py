# pylint: disable=invalid-name
"""Convert membership date and loss date from DateTime to Date.

Revision ID: 429c3f4db5a3
Revises: 422952c27a95
Create Date: 2016-12-05 14:38:39.240429
"""

from datetime import (
    date,
    datetime,
)

import sqlalchemy as sa
from sqlalchemy.orm import Session

from alembic import op

# pylint: disable=invalid-name
revision = '429c3f4db5a3'
# pylint: disable=invalid-name
down_revision = '422952c27a95'


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    # 1. copy data to temporary columns with old specification
    op.add_column('members', sa.Column(
        'membership_date_tmp',
        sa.DateTime(),
        default=datetime(1970, 1, 1)))
    op.add_column('members', sa.Column(
        'membership_loss_date_tmp',
        sa.DateTime()))

    session.execute("""
        update
            members
        set
            membership_date_tmp = membership_date
            ,
            membership_loss_date_tmp = membership_loss_date
        """)

    session.flush()
    session.commit()

    # 2. remove old columns
    with op.batch_alter_table('members') as batch_op:
        batch_op.drop_column('membership_date')
        batch_op.drop_column('membership_loss_date')

    # 3. create columns with new specification
    op.add_column('members', sa.Column(
        'membership_date',
        sa.Date(),
        default=date(1970, 1, 1)))
    op.add_column('members', sa.Column('membership_loss_date', sa.Date()))

    # 4. copy data from temporary to columns with new specification
    # TODO: Use CAST if possible with SQLite
    session.execute("""
        update
            members
        set
            membership_date = substr(membership_date_tmp, 1, 10)
            ,
            membership_loss_date = substr(membership_loss_date_tmp, 1, 10)
        """)
    session.flush()
    session.commit()

    # 5. remove temporary columns
    with op.batch_alter_table('members') as batch_op:
        batch_op.drop_column('membership_date_tmp')
        batch_op.drop_column('membership_loss_date_tmp')


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    # 1. copy data to temporary columns with old specification
    op.add_column('members', sa.Column(
        'membership_date_tmp',
        sa.Date(),
        default=date(1970, 1, 1)))
    op.add_column('members', sa.Column('membership_loss_date_tmp', sa.Date()))

    session.execute("""
        update
            members
        set
            membership_date_tmp = membership_date
            ,
            membership_loss_date_tmp = membership_loss_date
        """)
    session.flush()
    session.commit()

    # 2. remove old columns
    with op.batch_alter_table('members') as batch_op:
        batch_op.drop_column('membership_date')
        batch_op.drop_column('membership_loss_date')

    # 3. create columns with new specification
    op.add_column('members', sa.Column(
        'membership_date',
        sa.DateTime(),
        default=datetime(1970, 1, 1)))
    op.add_column('members', sa.Column('membership_loss_date', sa.DateTime()))

    # 4. copy data from temporary to columns with new specification
    # TODO: Use CAST if possible with SQLite
    session.execute("""
        update
            members
        set
            membership_date = membership_date_tmp || ' 00:00:00.000000'
            ,
            membership_loss_date = membership_loss_date_tmp || ' 00:00:00.000000'
        """)
    session.flush()
    session.commit()

    # 5. remove temporary columns
    with op.batch_alter_table('members') as batch_op:
        batch_op.drop_column('membership_date_tmp')
        batch_op.drop_column('membership_loss_date_tmp')
