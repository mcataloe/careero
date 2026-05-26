"""local password authentication

Revision ID: 0012_password_auth
Revises: 0011_automation_guardrails
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0012_password_auth"
down_revision = "0011_automation_guardrails"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_normalized", sa.String(length=320), nullable=True))
    op.add_column("users", sa.Column("username", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("username_normalized", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("password_hash", sa.Text(), nullable=True))
    op.add_column(
        "users",
        sa.Column("password_updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "auth_method",
            sa.String(length=100),
            server_default="local_password",
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "account_status",
            sa.String(length=100),
            server_default="active",
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column("failed_login_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE users SET email_normalized = lower(email) WHERE email_normalized IS NULL")
    op.create_index(
        "ix_users_username_normalized",
        "users",
        ["username_normalized"],
        unique=True,
    )
    op.create_index(
        "ix_users_email_normalized",
        "users",
        ["email_normalized"],
        unique=True,
    )
    op.create_index("ix_users_account_status", "users", ["account_status"])

    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("ip_hint", sa.String(length=100), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index(
        "ix_auth_sessions_token_hash",
        "auth_sessions",
        ["session_token_hash"],
        unique=True,
    )
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
    op.create_index("ix_auth_sessions_revoked_at", "auth_sessions", ["revoked_at"])


def downgrade() -> None:
    op.drop_index("ix_auth_sessions_revoked_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_token_hash", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_index("ix_users_account_status", table_name="users")
    op.drop_index("ix_users_email_normalized", table_name="users")
    op.drop_index("ix_users_username_normalized", table_name="users")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_count")
    op.drop_column("users", "account_status")
    op.drop_column("users", "auth_method")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "password_updated_at")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "username_normalized")
    op.drop_column("users", "username")
    op.drop_column("users", "email_normalized")
