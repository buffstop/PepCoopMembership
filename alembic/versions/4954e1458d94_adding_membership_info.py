"""adding membership info

Revision ID: 4954e1458d94
Revises: 39a47edfe661
Create Date: 2014-07-18 16:48:35.383844

"""

# revision identifiers, used by Alembic.
revision = '4954e1458d94'
down_revision = '39a47edfe661'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('members', sa.Column('is_legalentity', sa.Boolean(), nullable=True))
    op.add_column('members', sa.Column('membership_accepted', sa.Boolean(), nullable=True))
    op.add_column('members', sa.Column('membership_date', sa.DateTime(), nullable=True))
    op.add_column('members', sa.Column('membership_number', sa.Unicode(length=255), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('members', 'membership_number')
    op.drop_column('members', 'membership_date')
    op.drop_column('members', 'membership_accepted')
    op.drop_column('members', 'is_legalentity')
    ### end Alembic commands ###