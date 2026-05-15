"""application workflow persistence

Revision ID: 0008_application_workflow
Revises: 0007_workspace_context
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0008_application_workflow"
down_revision = "0007_workspace_context"
branch_labels = None
depends_on = None


def uuid_pk_column() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        server_default=sa.text("gen_random_uuid()"),
        nullable=False,
    )


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


def workflow_state_expression(source: str) -> str:
    return f"""
        CASE
            WHEN {source} = 'found' THEN 'discovered'
            WHEN {source} = 'interested' THEN 'interested'
            WHEN {source} = 'applied' THEN 'applied'
            WHEN {source} = 'archived' THEN 'archived'
            WHEN {source} IN (
                'discovered',
                'interested',
                'applied',
                'interviewing',
                'offer',
                'rejected',
                'withdrawn',
                'archived'
            ) THEN {source}
            ELSE 'discovered'
        END
    """


def upgrade() -> None:
    op.add_column(
        "applications",
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("current_state", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("reactivated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column(
            "workflow_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )

    op.execute(
        f"""
        UPDATE applications
        SET
            workspace_id = roles.workspace_id,
            current_state = {workflow_state_expression("applications.status")},
            archived_at = CASE
                WHEN {workflow_state_expression("applications.status")} = 'archived'
                THEN COALESCE(applications.deleted_at, applications.updated_at, now())
                ELSE applications.archived_at
            END,
            workflow_metadata = COALESCE(applications.workflow_metadata, '{{}}'::jsonb)
        FROM roles
        WHERE applications.role_id = roles.id
        """
    )

    op.execute(
        """
        UPDATE applications
        SET workspace_id = user_workspace.workspace_id
        FROM (
            SELECT DISTINCT ON (user_id) user_id, id AS workspace_id
            FROM workspaces
            ORDER BY user_id, created_at ASC, id ASC
        ) AS user_workspace
        WHERE applications.workspace_id IS NULL
          AND applications.user_id = user_workspace.user_id
        """
    )

    op.execute("UPDATE applications SET current_state = 'discovered' WHERE current_state IS NULL")
    op.execute("UPDATE applications SET status = current_state")

    op.alter_column("applications", "workspace_id", nullable=False)
    op.alter_column("applications", "current_state", nullable=False)
    op.create_foreign_key(
        "fk_applications_workspace_id_workspaces",
        "applications",
        "workspaces",
        ["workspace_id"],
        ["id"],
    )

    op.execute(
        f"""
        INSERT INTO applications (
            user_id,
            workspace_id,
            role_id,
            job_source_id,
            status,
            current_state,
            archived_at,
            workflow_metadata,
            created_at,
            updated_at
        )
        SELECT
            roles.user_id,
            roles.workspace_id,
            roles.id,
            roles.source_id,
            {workflow_state_expression("roles.status")},
            {workflow_state_expression("roles.status")},
            CASE
                WHEN {workflow_state_expression("roles.status")} = 'archived'
                THEN COALESCE(roles.deleted_at, roles.updated_at, now())
                ELSE NULL
            END,
            jsonb_build_object('backfilledFromRole', true),
            roles.created_at,
            roles.updated_at
        FROM roles
        WHERE NOT EXISTS (
            SELECT 1
            FROM applications
            WHERE applications.role_id = roles.id
              AND applications.deleted_at IS NULL
        )
        """
    )

    op.create_index("ix_applications_workspace_id", "applications", ["workspace_id"])
    op.create_index("ix_applications_current_state", "applications", ["current_state"])
    op.create_index(
        "ix_applications_workspace_state",
        "applications",
        ["workspace_id", "current_state"],
    )
    op.create_index("ix_applications_next_action_at", "applications", ["next_action_at"])
    op.create_index("ix_applications_archived_at", "applications", ["archived_at"])
    op.create_index(
        "uq_applications_active_role_id",
        "applications",
        ["role_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "application_state_history",
        uuid_pk_column(),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_state", sa.String(length=100), nullable=True),
        sa.Column("to_state", sa.String(length=100), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("changed_by", sa.String(length=100), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_application_state_history_application_id",
        "application_state_history",
        ["application_id"],
    )
    op.create_index(
        "ix_application_state_history_workspace_id",
        "application_state_history",
        ["workspace_id"],
    )
    op.create_index(
        "ix_application_state_history_changed_at",
        "application_state_history",
        ["changed_at"],
    )
    op.create_index(
        "ix_application_state_history_to_state",
        "application_state_history",
        ["to_state"],
    )

    op.create_table(
        "application_notes",
        uuid_pk_column(),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author", sa.String(length=200), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_application_notes_application_id", "application_notes", ["application_id"])
    op.create_index("ix_application_notes_workspace_id", "application_notes", ["workspace_id"])
    op.create_index("ix_application_notes_created_at", "application_notes", ["created_at"])

    op.create_table(
        "application_reminders",
        uuid_pk_column(),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_application_reminders_application_id", "application_reminders", ["application_id"])
    op.create_index("ix_application_reminders_workspace_id", "application_reminders", ["workspace_id"])
    op.create_index("ix_application_reminders_due_at", "application_reminders", ["due_at"])
    op.create_index("ix_application_reminders_completed_at", "application_reminders", ["completed_at"])

    op.create_table(
        "application_interview_stages",
        uuid_pk_column(),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stage_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_application_interview_stages_application_id",
        "application_interview_stages",
        ["application_id"],
    )
    op.create_index(
        "ix_application_interview_stages_workspace_id",
        "application_interview_stages",
        ["workspace_id"],
    )
    op.create_index(
        "ix_application_interview_stages_scheduled_at",
        "application_interview_stages",
        ["scheduled_at"],
    )
    op.create_index(
        "ix_application_interview_stages_completed_at",
        "application_interview_stages",
        ["completed_at"],
    )

    op.create_table(
        "application_external_links",
        uuid_pk_column(),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("link_type", sa.String(length=100), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_application_external_links_application_id",
        "application_external_links",
        ["application_id"],
    )
    op.create_index(
        "ix_application_external_links_workspace_id",
        "application_external_links",
        ["workspace_id"],
    )
    op.create_index(
        "ix_application_external_links_link_type",
        "application_external_links",
        ["link_type"],
    )

    op.execute(
        """
        INSERT INTO application_state_history (
            application_id,
            user_id,
            workspace_id,
            from_state,
            to_state,
            changed_at,
            changed_by,
            reason,
            metadata
        )
        SELECT
            applications.id,
            applications.user_id,
            applications.workspace_id,
            NULL,
            applications.current_state,
            COALESCE(applications.created_at, now()),
            'system',
            'Initial application workflow state.',
            jsonb_build_object('source', 'migration_backfill')
        FROM applications
        WHERE NOT EXISTS (
            SELECT 1
            FROM application_state_history
            WHERE application_state_history.application_id = applications.id
        )
        """
    )

    op.execute(
        """
        INSERT INTO application_notes (
            application_id,
            user_id,
            workspace_id,
            author,
            body,
            created_at,
            updated_at
        )
        SELECT
            applications.id,
            applications.user_id,
            applications.workspace_id,
            'Local User',
            applications.notes,
            COALESCE(applications.created_at, now()),
            COALESCE(applications.updated_at, now())
        FROM applications
        WHERE applications.notes IS NOT NULL
          AND btrim(applications.notes) <> ''
        """
    )


def downgrade() -> None:
    op.drop_index("ix_application_external_links_link_type", table_name="application_external_links")
    op.drop_index("ix_application_external_links_workspace_id", table_name="application_external_links")
    op.drop_index("ix_application_external_links_application_id", table_name="application_external_links")
    op.drop_table("application_external_links")

    op.drop_index("ix_application_interview_stages_completed_at", table_name="application_interview_stages")
    op.drop_index("ix_application_interview_stages_scheduled_at", table_name="application_interview_stages")
    op.drop_index("ix_application_interview_stages_workspace_id", table_name="application_interview_stages")
    op.drop_index("ix_application_interview_stages_application_id", table_name="application_interview_stages")
    op.drop_table("application_interview_stages")

    op.drop_index("ix_application_reminders_completed_at", table_name="application_reminders")
    op.drop_index("ix_application_reminders_due_at", table_name="application_reminders")
    op.drop_index("ix_application_reminders_workspace_id", table_name="application_reminders")
    op.drop_index("ix_application_reminders_application_id", table_name="application_reminders")
    op.drop_table("application_reminders")

    op.drop_index("ix_application_notes_created_at", table_name="application_notes")
    op.drop_index("ix_application_notes_workspace_id", table_name="application_notes")
    op.drop_index("ix_application_notes_application_id", table_name="application_notes")
    op.drop_table("application_notes")

    op.drop_index("ix_application_state_history_to_state", table_name="application_state_history")
    op.drop_index("ix_application_state_history_changed_at", table_name="application_state_history")
    op.drop_index("ix_application_state_history_workspace_id", table_name="application_state_history")
    op.drop_index("ix_application_state_history_application_id", table_name="application_state_history")
    op.drop_table("application_state_history")

    op.drop_index("uq_applications_active_role_id", table_name="applications")
    op.drop_index("ix_applications_archived_at", table_name="applications")
    op.drop_index("ix_applications_next_action_at", table_name="applications")
    op.drop_index("ix_applications_workspace_state", table_name="applications")
    op.drop_index("ix_applications_current_state", table_name="applications")
    op.drop_index("ix_applications_workspace_id", table_name="applications")
    op.drop_constraint(
        "fk_applications_workspace_id_workspaces",
        "applications",
        type_="foreignkey",
    )
    op.drop_column("applications", "workflow_metadata")
    op.drop_column("applications", "reactivated_at")
    op.drop_column("applications", "archived_at")
    op.drop_column("applications", "current_state")
    op.drop_column("applications", "workspace_id")
