"""role intake fields

Revision ID: 0002_role_intake
Revises: 0001_initial_schema
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_role_intake"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "roles",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("roles", sa.Column("job_url", sa.String(length=2048), nullable=True))
    op.execute("UPDATE roles SET job_url = source_url WHERE source_url IS NOT NULL")
    op.add_column("roles", sa.Column("remote_type", sa.String(length=100), nullable=True))
    op.add_column("roles", sa.Column("compensation_min", sa.Numeric(12, 2), nullable=True))
    op.add_column("roles", sa.Column("compensation_max", sa.Numeric(12, 2), nullable=True))
    op.add_column(
        "roles",
        sa.Column("compensation_currency", sa.String(length=3), nullable=True),
    )
    op.add_column("roles", sa.Column("raw_description", sa.Text(), nullable=True))
    op.execute(
        "UPDATE roles SET raw_description = description WHERE description IS NOT NULL"
    )
    op.add_column("roles", sa.Column("normalized_description", sa.Text(), nullable=True))
    op.add_column(
        "roles",
        sa.Column(
            "status",
            sa.String(length=100),
            server_default="found",
            nullable=False,
        ),
    )
    op.add_column(
        "roles",
        sa.Column(
            "date_found",
            sa.Date(),
            server_default=sa.text("CURRENT_DATE"),
            nullable=False,
        ),
    )
    op.add_column("roles", sa.Column("date_posted", sa.Date(), nullable=True))

    op.create_foreign_key(
        "fk_roles_source_id_job_sources",
        "roles",
        "job_sources",
        ["source_id"],
        ["id"],
    )
    op.create_index("ix_roles_source_id", "roles", ["source_id"])
    op.create_index("ix_roles_status", "roles", ["status"])
    op.create_index("ix_roles_user_status", "roles", ["user_id", "status"])
    op.create_index(
        "uq_job_sources_user_source_type",
        "job_sources",
        ["user_id", "source_type"],
        unique=True,
    )

    op.drop_column("roles", "source_url")
    op.drop_column("roles", "description")
    op.drop_column("roles", "employment_type")


def downgrade() -> None:
    op.add_column(
        "roles",
        sa.Column("employment_type", sa.String(length=100), nullable=True),
    )
    op.add_column("roles", sa.Column("description", sa.Text(), nullable=True))
    op.execute(
        "UPDATE roles SET description = raw_description WHERE raw_description IS NOT NULL"
    )
    op.add_column("roles", sa.Column("source_url", sa.String(length=2048), nullable=True))
    op.execute("UPDATE roles SET source_url = job_url WHERE job_url IS NOT NULL")

    op.drop_index("uq_job_sources_user_source_type", table_name="job_sources")
    op.drop_index("ix_roles_user_status", table_name="roles")
    op.drop_index("ix_roles_status", table_name="roles")
    op.drop_index("ix_roles_source_id", table_name="roles")
    op.drop_constraint("fk_roles_source_id_job_sources", "roles", type_="foreignkey")

    op.drop_column("roles", "date_posted")
    op.drop_column("roles", "date_found")
    op.drop_column("roles", "status")
    op.drop_column("roles", "normalized_description")
    op.drop_column("roles", "raw_description")
    op.drop_column("roles", "compensation_currency")
    op.drop_column("roles", "compensation_max")
    op.drop_column("roles", "compensation_min")
    op.drop_column("roles", "remote_type")
    op.drop_column("roles", "job_url")
    op.drop_column("roles", "source_id")
