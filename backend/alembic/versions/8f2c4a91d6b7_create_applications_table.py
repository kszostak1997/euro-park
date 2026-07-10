"""create applications table

Revision ID: 8f2c4a91d6b7
Revises: 51e17ed64402
Create Date: 2026-07-09 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f2c4a91d6b7'
down_revision: Union[str, Sequence[str], None] = '51e17ed64402'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('applications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('registration_number', sa.String(length=20), nullable=False),
    sa.Column('floor', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'NEEDS_CHANGES', 'APPROVED', 'REJECTED', name='applicationstatus', native_enum=False, length=20), nullable=False),
    sa.Column('comment', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_user_id'), 'applications', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_applications_user_id'), table_name='applications')
    op.drop_table('applications')
