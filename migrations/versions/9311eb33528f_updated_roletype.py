"""Updated RoleType

Revision ID: 9311eb33528f
Revises: b0786692c626
Create Date: 2020-10-21 00:31:38.630267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9311eb33528f'
down_revision = 'b0786692c626'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('role_type', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('role_type', sa.Column('joinable', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('role_type', 'joinable')
    op.drop_column('role_type', 'description')
    # ### end Alembic commands ###
