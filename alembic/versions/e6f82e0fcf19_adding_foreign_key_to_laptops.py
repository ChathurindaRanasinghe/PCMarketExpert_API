"""adding foreign key to laptops

Revision ID: e6f82e0fcf19
Revises: 
Create Date: 2022-06-13 20:40:37.930900

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6f82e0fcf19'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key('id_fk', source_table="laptops",referent_table="products",local_cols=['id'],remote_cols=['id'],ondelete="CASCADE")
    pass


def downgrade():
    op.drop_constraint('id_fk',table_name="laptops")
    pass
