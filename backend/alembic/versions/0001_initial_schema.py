"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
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


def soft_delete_column() -> sa.Column:
    return sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)


def uuid_pk_column() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        nullable=False,
    )


def user_fk_column(nullable: bool = False) -> sa.Column:
    return sa.Column(
        "user_id",
        postgresql.UUID(as_uuid=True),
        nullable=nullable,
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "users",
        uuid_pk_column(),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        *timestamp_columns(),
        soft_delete_column(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "companies",
        uuid_pk_column(),
        user_fk_column(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("website_url", sa.String(length=2048), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        soft_delete_column(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_companies_user_id", "companies", ["user_id"])

    op.create_table(
        "job_sources",
        uuid_pk_column(),
        user_fk_column(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("website_url", sa.String(length=2048), nullable=True),
        *timestamp_columns(),
        soft_delete_column(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_sources_user_id", "job_sources", ["user_id"])

    op.create_table(
        "roles",
        uuid_pk_column(),
        user_fk_column(),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("employment_type", sa.String(length=100), nullable=True),
        sa.Column("source_url", sa.String(length=2048), nullable=True),
        *timestamp_columns(),
        soft_delete_column(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_roles_company_id", "roles", ["company_id"])
    op.create_index("ix_roles_user_id", "roles", ["user_id"])

    op.create_table(
        "stride_evaluations",
        uuid_pk_column(),
        user_fk_column(),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "scores",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        soft_delete_column(),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stride_evaluations_role_id", "stride_evaluations", ["role_id"])
    op.create_index("ix_stride_evaluations_user_id", "stride_evaluations", ["user_id"])

    op.create_table(
        "applications",
        uuid_pk_column(),
        user_fk_column(),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=100), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_action_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        soft_delete_column(),
        sa.ForeignKeyConstraint(["job_source_id"], ["job_sources.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_applications_job_source_id", "applications", ["job_source_id"])
    op.create_index("ix_applications_role_id", "applications", ["role_id"])
    op.create_index("ix_applications_user_id", "applications", ["user_id"])

    op.create_table(
        "generated_artifacts",
        uuid_pk_column(),
        user_fk_column(),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("artifact_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        *timestamp_columns(),
        soft_delete_column(),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_generated_artifacts_application_id",
        "generated_artifacts",
        ["application_id"],
    )
    op.create_index("ix_generated_artifacts_role_id", "generated_artifacts", ["role_id"])
    op.create_index("ix_generated_artifacts_user_id", "generated_artifacts", ["user_id"])

    op.create_table(
        "activity_log",
        uuid_pk_column(),
        user_fk_column(),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activity_log_entity", "activity_log", ["entity_type", "entity_id"])
    op.create_index("ix_activity_log_user_id", "activity_log", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_activity_log_user_id", table_name="activity_log")
    op.drop_index("ix_activity_log_entity", table_name="activity_log")
    op.drop_table("activity_log")

    op.drop_index("ix_generated_artifacts_user_id", table_name="generated_artifacts")
    op.drop_index("ix_generated_artifacts_role_id", table_name="generated_artifacts")
    op.drop_index(
        "ix_generated_artifacts_application_id",
        table_name="generated_artifacts",
    )
    op.drop_table("generated_artifacts")

    op.drop_index("ix_applications_user_id", table_name="applications")
    op.drop_index("ix_applications_role_id", table_name="applications")
    op.drop_index("ix_applications_job_source_id", table_name="applications")
    op.drop_table("applications")

    op.drop_index("ix_stride_evaluations_user_id", table_name="stride_evaluations")
    op.drop_index("ix_stride_evaluations_role_id", table_name="stride_evaluations")
    op.drop_table("stride_evaluations")

    op.drop_index("ix_roles_user_id", table_name="roles")
    op.drop_index("ix_roles_company_id", table_name="roles")
    op.drop_table("roles")

    op.drop_index("ix_job_sources_user_id", table_name="job_sources")
    op.drop_table("job_sources")

    op.drop_index("ix_companies_user_id", table_name="companies")
    op.drop_table("companies")

    op.drop_table("users")
