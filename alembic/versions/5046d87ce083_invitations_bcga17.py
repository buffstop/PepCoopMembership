"""Invitations BCGA 2017

Revision ID: 5046d87ce083
Revises: 429c3f4db5a3
Create Date: 2017-02-02 15:56:19.698594

"""

# revision identifiers, used by Alembic.
revision = '5046d87ce083'
down_revision = '429c3f4db5a3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('members', sa.Column('email_invite_date_bcgv17', sa.DateTime(), nullable=True))
    op.add_column('members', sa.Column('email_invite_flag_bcgv17', sa.Boolean(), nullable=True))
    op.add_column('members', sa.Column('email_invite_token_bcgv17', sa.Unicode(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('members') as batch_op:
        batch_op.drop_column('email_invite_token_bcgv17')
        batch_op.drop_column('email_invite_flag_bcgv17')
        batch_op.drop_column('email_invite_date_bcgv17')
