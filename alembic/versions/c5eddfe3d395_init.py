"""init

Revision ID: c5eddfe3d395
Revises: 8e476d6973ba
Create Date: 2025-03-26 16:31:31.154840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c5eddfe3d395'
down_revision: Union[str, None] = '8e476d6973ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     
    op.create_foreign_key(None, 'post_images', 'posts', ['post_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'posts', 'organizations', ['organization_id'], ['id'])
   

def downgrade() -> None:
   
    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.drop_constraint(None, 'post_images', type_='foreignkey')
