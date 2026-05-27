"""deprecate username identity fields

Revision ID: 0018_username_deprecation
Revises: 0017_identity_profile_fields
Create Date: 2026-05-27
"""

from alembic import op
import sqlalchemy as sa


revision = "0018_username_deprecation"
down_revision = "0017_identity_profile_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE users
        SET
            first_name = COALESCE(NULLIF(split_part(display_name, ' ', 1), ''), 'Local'),
            last_name = COALESCE(
                NULLIF(btrim(substr(display_name, length(split_part(display_name, ' ', 1)) + 1)), ''),
                'User'
            )
        WHERE first_name IS NULL OR last_name IS NULL
        """
    )
    op.alter_column("users", "first_name", nullable=False)
    op.alter_column("users", "last_name", nullable=False)

    op.drop_index("ix_users_username_normalized", table_name="users")
    op.drop_column("users", "username_normalized")
    op.drop_column("users", "username")


def downgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=100), nullable=True))
    op.add_column(
        "users",
        sa.Column("username_normalized", sa.String(length=100), nullable=True),
    )
    op.create_index(
        "ix_users_username_normalized",
        "users",
        ["username_normalized"],
        unique=True,
    )
    op.alter_column("users", "last_name", nullable=True)
    op.alter_column("users", "first_name", nullable=True)
