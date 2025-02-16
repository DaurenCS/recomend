"""add_index_column

Revision ID: 8de5620059fe
Revises: 2f49cd1ef13b
Create Date: 2025-02-16 00:25:10.783280

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8de5620059fe'
down_revision: Union[str, None] = '2f49cd1ef13b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profile_vectors', sa.Column('faiss_index_position', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('profile_vectors', 'faiss_index_position')
