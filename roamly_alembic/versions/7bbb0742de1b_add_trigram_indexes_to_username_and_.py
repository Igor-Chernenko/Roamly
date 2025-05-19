"""add trigram indexes to username and adventure title

Revision ID: 7bbb0742de1b
Revises: 1db0c869e739
Create Date: 2025-05-19 10:17:49.064299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7bbb0742de1b'
down_revision: Union[str, None] = '1db0c869e739'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE INDEX IF NOT EXISTS username_trgm_idx ON users USING gin (username gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS adventure_title_trgm_idx ON adventures USING gin (title gin_trgm_ops)")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS username_trgm_idx")
    op.execute("DROP INDEX IF EXISTS adventure_title_trgm_idx")
