"""add artifact lifecycle fields

Revision ID: 0019_artifact_lifecycle
Revises: 0018_username_deprecation
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0019_artifact_lifecycle"
down_revision = "0018_username_deprecation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "generated_artifacts",
        sa.Column(
            "lifecycle_status",
            sa.String(length=100),
            server_default="draft",
            nullable=False,
        ),
    )
    op.add_column(
        "generated_artifacts",
        sa.Column(
            "version_number",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
    )
    op.add_column(
        "generated_artifacts",
        sa.Column("source_artifact_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "generated_artifacts",
        sa.Column("evaluation_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "generated_artifacts",
        sa.Column(
            "source_resume_version_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "generated_artifacts",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "generated_artifacts",
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "generated_artifacts",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.execute(
        """
        UPDATE generated_artifacts
        SET lifecycle_status = CASE
            WHEN metadata #>> '{contract,lifecycleStatus}' IN ('draft', 'reviewed', 'submitted', 'archived')
                THEN metadata #>> '{contract,lifecycleStatus}'
            WHEN metadata #>> '{contract,lifecycleStatus}' IN ('approved', 'exported')
                THEN 'reviewed'
            ELSE 'draft'
        END
        """
    )
    op.execute(
        """
        UPDATE generated_artifacts
        SET version_number = GREATEST(
            1,
            COALESCE(
                NULLIF(metadata #>> '{contract,revision,revisionNumber}', '')::integer,
                1
            )
        )
        WHERE metadata #>> '{contract,revision,revisionNumber}' ~ '^[0-9]+$'
        """
    )
    op.execute(
        """
        UPDATE generated_artifacts
        SET source_artifact_id = (metadata #>> '{contract,revision,parentArtifactId}')::uuid
        WHERE metadata #>> '{contract,revision,parentArtifactId}'
              ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
          AND EXISTS (
              SELECT 1
              FROM generated_artifacts AS parent_artifact
              WHERE parent_artifact.id = (generated_artifacts.metadata #>> '{contract,revision,parentArtifactId}')::uuid
          )
        """
    )
    op.execute(
        """
        UPDATE generated_artifacts
        SET evaluation_id = (metadata #>> '{target_evaluation_id}')::uuid
        WHERE metadata #>> '{target_evaluation_id}'
              ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
          AND EXISTS (
              SELECT 1
              FROM compass_evaluations
              WHERE compass_evaluations.id = (generated_artifacts.metadata #>> '{target_evaluation_id}')::uuid
          )
        """
    )
    op.execute(
        """
        UPDATE generated_artifacts
        SET source_resume_version_id = (metadata #>> '{source_resume,version_id}')::uuid
        WHERE metadata #>> '{source_resume,version_id}'
              ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
          AND EXISTS (
              SELECT 1
              FROM resume_source_versions
              WHERE resume_source_versions.id = (generated_artifacts.metadata #>> '{source_resume,version_id}')::uuid
          )
        """
    )
    op.execute(
        """
        UPDATE generated_artifacts
        SET submitted_at = (metadata #>> '{contract,submittedAt}')::timestamptz
        WHERE metadata #>> '{contract,submittedAt}' IS NOT NULL
          AND metadata #>> '{contract,submittedAt}' <> ''
        """
    )
    op.execute(
        """
        UPDATE generated_artifacts
        SET archived_at = (metadata #>> '{contract,archivedAt}')::timestamptz
        WHERE metadata #>> '{contract,archivedAt}' IS NOT NULL
          AND metadata #>> '{contract,archivedAt}' <> ''
        """
    )

    op.create_foreign_key(
        "fk_generated_artifacts_source_artifact_id_generated_artifacts",
        "generated_artifacts",
        "generated_artifacts",
        ["source_artifact_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_generated_artifacts_evaluation_id_compass_evaluations",
        "generated_artifacts",
        "compass_evaluations",
        ["evaluation_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_generated_artifacts_source_resume_version_id_resume_source_versions",
        "generated_artifacts",
        "resume_source_versions",
        ["source_resume_version_id"],
        ["id"],
    )
    op.create_index(
        "ix_generated_artifacts_lifecycle_status",
        "generated_artifacts",
        ["lifecycle_status"],
    )
    op.create_index(
        "ix_generated_artifacts_evaluation_id",
        "generated_artifacts",
        ["evaluation_id"],
    )
    op.create_index(
        "ix_generated_artifacts_source_artifact_id",
        "generated_artifacts",
        ["source_artifact_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_generated_artifacts_source_artifact_id",
        table_name="generated_artifacts",
    )
    op.drop_index(
        "ix_generated_artifacts_evaluation_id",
        table_name="generated_artifacts",
    )
    op.drop_index(
        "ix_generated_artifacts_lifecycle_status",
        table_name="generated_artifacts",
    )
    op.drop_constraint(
        "fk_generated_artifacts_source_resume_version_id_resume_source_versions",
        "generated_artifacts",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_generated_artifacts_evaluation_id_compass_evaluations",
        "generated_artifacts",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_generated_artifacts_source_artifact_id_generated_artifacts",
        "generated_artifacts",
        type_="foreignkey",
    )
    op.drop_column("generated_artifacts", "archived_at")
    op.drop_column("generated_artifacts", "submitted_at")
    op.drop_column("generated_artifacts", "reviewed_at")
    op.drop_column("generated_artifacts", "source_resume_version_id")
    op.drop_column("generated_artifacts", "evaluation_id")
    op.drop_column("generated_artifacts", "source_artifact_id")
    op.drop_column("generated_artifacts", "version_number")
    op.drop_column("generated_artifacts", "lifecycle_status")
