"""Loss of membership.

Revision ID: 1de26724691f
Revises: 11986603bcd9
Create Date: 2016-01-11 20:54:54.127903

"""

# revision identifiers, used by Alembic.
revision = '1de26724691f'
down_revision = '11986603bcd9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('members', sa.Column('membership_loss_date', sa.DateTime(), nullable=True))
    op.add_column('members', sa.Column('membership_loss_type', sa.Unicode(length=255), nullable=True))


def downgrade():
    op.drop_column('members', 'membership_loss_type')
    op.drop_column('members', 'membership_loss_date')
