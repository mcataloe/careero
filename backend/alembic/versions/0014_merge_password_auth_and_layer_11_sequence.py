"""merge password auth and layer 11 sequence heads

Revision ID: 0014_merge_11c_11seq
Revises: 0012_password_auth, 0013_ai_usage_events
Create Date: 2026-05-26
"""

revision = "0014_merge_11c_11seq"
down_revision = ("0012_password_auth", "0013_ai_usage_events")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
