"""resume source grounding

Revision ID: 0004_resume_sources
Revises: 0003_compass_evaluations
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_resume_sources"
down_revision = "0003_compass_evaluations"
branch_labels = None
depends_on = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    ]


def uuid_pk_column() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        nullable=False,
    )


def upgrade() -> None:
    op.create_table(
        "resume_sources",
        uuid_pk_column(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resume_sources_user_id", "resume_sources", ["user_id"])
    op.create_index("ix_resume_sources_source_type", "resume_sources", ["source_type"])

    op.create_table(
        "resume_source_versions",
        uuid_pk_column(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_label", sa.String(length=100), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("normalized_summary", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["source_id"], ["resume_sources.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_resume_source_versions_user_id",
        "resume_source_versions",
        ["user_id"],
    )
    op.create_index(
        "ix_resume_source_versions_source_id",
        "resume_source_versions",
        ["source_id"],
    )
    op.create_index(
        "ix_resume_source_versions_is_active",
        "resume_source_versions",
        ["is_active"],
    )
    op.create_index(
        "uq_resume_source_versions_active_user",
        "resume_source_versions",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_active"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_resume_source_versions_active_user",
        table_name="resume_source_versions",
    )
    op.drop_index(
        "ix_resume_source_versions_is_active",
        table_name="resume_source_versions",
    )
    op.drop_index(
        "ix_resume_source_versions_source_id",
        table_name="resume_source_versions",
    )
    op.drop_index(
        "ix_resume_source_versions_user_id",
        table_name="resume_source_versions",
    )
    op.drop_table("resume_source_versions")

    op.drop_index("ix_resume_sources_source_type", table_name="resume_sources")
    op.drop_index("ix_resume_sources_user_id", table_name="resume_sources")
    op.drop_table("resume_sources")
