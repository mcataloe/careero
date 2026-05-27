"""add professional identity fields

Revision ID: 0017_identity_profile_fields
Revises: 0016_compass_repair
Create Date: 2026-05-27
"""

from alembic import op
import sqlalchemy as sa


revision = "0017_identity_profile_fields"
down_revision = "0016_compass_repair"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("salutation", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("pronouns", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("headshot_url", sa.String(length=2048), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "headshot_url")
    op.drop_column("users", "pronouns")
    op.drop_column("users", "salutation")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
