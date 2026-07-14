"""add applicant_comment to applications

Revision ID: a1c9e3f7b2d4
Revises: 6316316cb8b6
Create Date: 2026-07-14 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1c9e3f7b2d4"
down_revision: Union[str, Sequence[str], None] = "6316316cb8b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "applications",
        sa.Column("applicant_comment", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("applications", "applicant_comment")
