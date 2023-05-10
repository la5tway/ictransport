"""empty message

Revision ID: a5852fc6d4d4
Revises: 
Create Date: 2023-05-10 04:56:01.523853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5852fc6d4d4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('news',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('tag', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('pub_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('parsed_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('preview_url', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'tag', name=op.f('pk_news'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('news')
    # ### end Alembic commands ###
