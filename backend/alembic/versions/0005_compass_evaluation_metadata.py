"""compass evaluation metadata

Revision ID: 0005_compass_evaluation_metadata
Revises: 0004_resume_sources
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_compass_evaluation_metadata"
down_revision = "0004_resume_sources"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "compass_evaluations",
        sa.Column("model_used", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column("prompt_version", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column("ruleset_version", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column("input_token_estimate", sa.Integer(), nullable=True),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column("output_token_estimate", sa.Integer(), nullable=True),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column("latency_ms", sa.Integer(), nullable=True),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column(
            "ai_enabled",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column("ai_status", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column("role_content_hash", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column("source_hash", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "compass_evaluations",
        sa.Column("evaluation_input_hash", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_compass_evaluations_role_input_hash",
        "compass_evaluations",
        ["role_id", "evaluation_input_hash"],
    )
    op.create_index(
        "ix_compass_evaluations_ai_status",
        "compass_evaluations",
        ["ai_status"],
    )
    op.create_index(
        "ix_compass_evaluations_ruleset_version",
        "compass_evaluations",
        ["ruleset_version"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_compass_evaluations_ruleset_version",
        table_name="compass_evaluations",
    )
    op.drop_index("ix_compass_evaluations_ai_status", table_name="compass_evaluations")
    op.drop_index(
        "ix_compass_evaluations_role_input_hash",
        table_name="compass_evaluations",
    )
    op.drop_column("compass_evaluations", "evaluation_input_hash")
    op.drop_column("compass_evaluations", "source_hash")
    op.drop_column("compass_evaluations", "role_content_hash")
    op.drop_column("compass_evaluations", "error_message")
    op.drop_column("compass_evaluations", "ai_status")
    op.drop_column("compass_evaluations", "ai_enabled")
    op.drop_column("compass_evaluations", "latency_ms")
    op.drop_column("compass_evaluations", "output_token_estimate")
    op.drop_column("compass_evaluations", "input_token_estimate")
    op.drop_column("compass_evaluations", "ruleset_version")
    op.drop_column("compass_evaluations", "prompt_version")
    op.drop_column("compass_evaluations", "model_used")
