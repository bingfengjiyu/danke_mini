"""empty message

Revision ID: e047f1cbcd1b
Revises: 2916be9c993c
Create Date: 2018-10-25 16:13:20.774591

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e047f1cbcd1b'
down_revision = '2916be9c993c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dk_goods', 'detail')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dk_goods', sa.Column('detail', mysql.TEXT(), nullable=False))
    # ### end Alembic commands ###
