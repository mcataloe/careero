"""repair legacy COMPASS evaluation table compatibility

Revision ID: 0016_compass_repair
Revises: 0015_artifact_alignment
Create Date: 2026-05-27
"""

from alembic import op


revision = "0016_compass_repair"
down_revision = "0015_artifact_alignment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('public.compass_evaluations') IS NULL
               AND to_regclass('public.stride_evaluations') IS NOT NULL THEN
                ALTER TABLE stride_evaluations RENAME TO compass_evaluations;
            END IF;

            ALTER INDEX IF EXISTS ix_stride_evaluations_ai_status
                RENAME TO ix_compass_evaluations_ai_status;
            ALTER INDEX IF EXISTS ix_stride_evaluations_role_created_at
                RENAME TO ix_compass_evaluations_role_created_at;
            ALTER INDEX IF EXISTS ix_stride_evaluations_role_id
                RENAME TO ix_compass_evaluations_role_id;
            ALTER INDEX IF EXISTS ix_stride_evaluations_role_input_hash
                RENAME TO ix_compass_evaluations_role_input_hash;
            ALTER INDEX IF EXISTS ix_stride_evaluations_ruleset_version
                RENAME TO ix_compass_evaluations_ruleset_version;
            ALTER INDEX IF EXISTS ix_stride_evaluations_status
                RENAME TO ix_compass_evaluations_status;
            ALTER INDEX IF EXISTS ix_stride_evaluations_user_id
                RENAME TO ix_compass_evaluations_user_id;
            ALTER INDEX IF EXISTS ix_stride_evaluations_workspace_id
                RENAME TO ix_compass_evaluations_workspace_id;

            IF to_regclass('public.compass_evaluations') IS NOT NULL THEN
                ALTER TABLE compass_evaluations
                    RENAME CONSTRAINT fk_stride_evaluations_workspace_id_workspaces
                    TO fk_compass_evaluations_workspace_id_workspaces;
            END IF;
        EXCEPTION
            WHEN undefined_object THEN
                NULL;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('public.stride_evaluations') IS NULL
               AND to_regclass('public.compass_evaluations') IS NOT NULL THEN
                ALTER TABLE compass_evaluations RENAME TO stride_evaluations;
            END IF;
        END $$;
        """
    )
