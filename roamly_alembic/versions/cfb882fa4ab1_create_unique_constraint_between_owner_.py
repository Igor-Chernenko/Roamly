"""Create unique constraint between owner_id and title

Revision ID: cfb882fa4ab1
Revises: dede0e256f31
Create Date: 2025-05-17 18:47:27.496228

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfb882fa4ab1'
down_revision: Union[str, None] = 'dede0e256f31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uq_owner_title', 'adventures', ['title', 'owner_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_owner_title', 'adventures', type_='unique')
    # ### end Alembic commands ###
