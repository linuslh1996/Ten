"""Added Country Column

Revision ID: 8ce9af0afb90
Revises: 
Create Date: 2020-09-03 12:09:02.931835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ce9af0afb90'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('restaurants', sa.Column('country', sa.String(), nullable=True))
    op.add_column('restaurants', sa.Column('town', sa.String(), nullable=True))
    op.drop_column('restaurants', 'stadt')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('restaurants', sa.Column('stadt', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('restaurants', 'town')
    op.drop_column('restaurants', 'country')
    # ### end Alembic commands ###