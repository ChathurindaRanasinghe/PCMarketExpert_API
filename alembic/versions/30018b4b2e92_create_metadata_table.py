"""create metadata table

Revision ID: 30018b4b2e92
Revises: 
Create Date: 2022-05-29 18:49:12.604750

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30018b4b2e92'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('shop-metadata', sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('name', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_table('shop-metadata')
    pass
