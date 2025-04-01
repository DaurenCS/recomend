"""init

Revision ID: 164ea5fd68b7
Revises: 9971d4b808cf
Create Date: 2025-03-30 22:32:47.005351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '164ea5fd68b7'
down_revision: Union[str, None] = '9971d4b808cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user_tags',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'tag_id')
    )
   
 


def downgrade() -> None:
   
    op.drop_table('user_tags')
    op.drop_table('tags')
    # ### end Alembic commands ###
