"""role parse metadata

Revision ID: 0006_role_parse_metadata
Revises: 0005_compass_evaluation_metadata
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0006_role_parse_metadata"
down_revision = "0005_compass_evaluation_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "roles",
        sa.Column(
            "parse_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.alter_column("roles", "parse_metadata", server_default=None)


def downgrade() -> None:
    op.drop_column("roles", "parse_metadata")
