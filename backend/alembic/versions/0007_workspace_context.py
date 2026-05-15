"""workspace context

Revision ID: 0007_workspace_context
Revises: 0006_role_parse_metadata
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0007_workspace_context"
down_revision = "0006_role_parse_metadata"
branch_labels = None
depends_on = None

DEFAULT_LOCAL_USER_ID = "00000000-0000-4000-8000-000000000001"
DEFAULT_WORKSPACE_ID = "00000000-0000-4000-8000-000000000101"


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


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("workspace_type", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.String(length=100),
            server_default="active",
            nullable=False,
        ),
        sa.Column(
            "preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("ai_context_summary", sa.Text(), nullable=True),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workspaces_user_id", "workspaces", ["user_id"])
    op.create_index("ix_workspaces_status", "workspaces", ["status"])
    op.create_index("ix_workspaces_user_status", "workspaces", ["user_id", "status"])

    op.execute(
        f"""
        INSERT INTO workspaces (
            id,
            user_id,
            title,
            description,
            workspace_type,
            status,
            preferences,
            ai_context_summary,
            tags,
            metadata
        )
        SELECT
            CASE
                WHEN users.id = '{DEFAULT_LOCAL_USER_ID}'::uuid
                THEN '{DEFAULT_WORKSPACE_ID}'::uuid
                ELSE gen_random_uuid()
            END,
            users.id,
            'Default workspace',
            'Default local workspace for existing Careero records.',
            'full_time_individual_contributor',
            'active',
            '{{}}'::jsonb,
            NULL,
            '[]'::jsonb,
            jsonb_build_object('isDefault', true)
        FROM users
        WHERE NOT EXISTS (
            SELECT 1 FROM workspaces WHERE workspaces.user_id = users.id
        )
        """
    )

    op.add_column(
        "roles",
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "stride_evaluations",
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "generated_artifacts",
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.execute(
        """
        UPDATE roles
        SET workspace_id = user_workspace.workspace_id
        FROM (
            SELECT DISTINCT ON (user_id) user_id, id AS workspace_id
            FROM workspaces
            ORDER BY user_id, created_at ASC, id ASC
        ) AS user_workspace
        WHERE roles.user_id = user_workspace.user_id
        """
    )
    op.execute(
        """
        UPDATE stride_evaluations
        SET workspace_id = roles.workspace_id
        FROM roles
        WHERE stride_evaluations.role_id = roles.id
        """
    )
    op.execute(
        """
        UPDATE stride_evaluations
        SET workspace_id = user_workspace.workspace_id
        FROM (
            SELECT DISTINCT ON (user_id) user_id, id AS workspace_id
            FROM workspaces
            ORDER BY user_id, created_at ASC, id ASC
        ) AS user_workspace
        WHERE stride_evaluations.workspace_id IS NULL
          AND stride_evaluations.user_id = user_workspace.user_id
        """
    )
    op.execute(
        """
        UPDATE generated_artifacts
        SET workspace_id = artifact_workspace.id
        FROM workspaces AS artifact_workspace
        WHERE generated_artifacts.metadata #>> '{contract,workspaceId}'
              ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
          AND (generated_artifacts.metadata #>> '{contract,workspaceId}')::uuid
              = artifact_workspace.id
        """
    )
    op.execute(
        """
        UPDATE generated_artifacts
        SET workspace_id = roles.workspace_id
        FROM roles
        WHERE generated_artifacts.workspace_id IS NULL
          AND generated_artifacts.role_id = roles.id
        """
    )
    op.execute(
        """
        UPDATE generated_artifacts
        SET workspace_id = user_workspace.workspace_id
        FROM (
            SELECT DISTINCT ON (user_id) user_id, id AS workspace_id
            FROM workspaces
            ORDER BY user_id, created_at ASC, id ASC
        ) AS user_workspace
        WHERE generated_artifacts.workspace_id IS NULL
          AND generated_artifacts.user_id = user_workspace.user_id
        """
    )

    op.alter_column("roles", "workspace_id", nullable=False)
    op.alter_column("stride_evaluations", "workspace_id", nullable=False)
    op.alter_column("generated_artifacts", "workspace_id", nullable=False)

    op.create_foreign_key(
        "fk_roles_workspace_id_workspaces",
        "roles",
        "workspaces",
        ["workspace_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_stride_evaluations_workspace_id_workspaces",
        "stride_evaluations",
        "workspaces",
        ["workspace_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_generated_artifacts_workspace_id_workspaces",
        "generated_artifacts",
        "workspaces",
        ["workspace_id"],
        ["id"],
    )
    op.create_index("ix_roles_workspace_id", "roles", ["workspace_id"])
    op.create_index(
        "ix_stride_evaluations_workspace_id",
        "stride_evaluations",
        ["workspace_id"],
    )
    op.create_index(
        "ix_generated_artifacts_workspace_id",
        "generated_artifacts",
        ["workspace_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_generated_artifacts_workspace_id", table_name="generated_artifacts")
    op.drop_index("ix_stride_evaluations_workspace_id", table_name="stride_evaluations")
    op.drop_index("ix_roles_workspace_id", table_name="roles")
    op.drop_constraint(
        "fk_generated_artifacts_workspace_id_workspaces",
        "generated_artifacts",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_stride_evaluations_workspace_id_workspaces",
        "stride_evaluations",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_roles_workspace_id_workspaces",
        "roles",
        type_="foreignkey",
    )
    op.drop_column("generated_artifacts", "workspace_id")
    op.drop_column("stride_evaluations", "workspace_id")
    op.drop_column("roles", "workspace_id")
    op.drop_index("ix_workspaces_user_status", table_name="workspaces")
    op.drop_index("ix_workspaces_status", table_name="workspaces")
    op.drop_index("ix_workspaces_user_id", table_name="workspaces")
    op.drop_table("workspaces")
