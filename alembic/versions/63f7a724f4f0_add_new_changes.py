"""Add new changes

Revision ID: 63f7a724f4f0
Revises: 25d814bc83ed
Create Date: 2024-12-17 02:09:05.378155
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '63f7a724f4f0'
down_revision: Union[str, None] = '25d814bc83ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add new columns or modify existing ones
    op.add_column('users', sa.Column('profile_picture_url', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('linkedin_profile_url', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('github_profile_url', sa.String(length=255), nullable=True))
    
    # Handle enum updates if needed (for example, adding new roles)
    op.execute("ALTER TYPE \"UserRole\" ADD VALUE IF NOT EXISTS 'MANAGER'")

def downgrade() -> None:
    # Drop the newly added columns
    op.drop_column('users', 'profile_picture_url')
    op.drop_column('users', 'linkedin_profile_url')
    op.drop_column('users', 'github_profile_url')
    
    # Rollback any enum changes
    op.execute("ALTER TYPE \"UserRole\" REMOVE VALUE 'MANAGER'")
