"""ensure artifact performance compass alignment

Revision ID: 0015_artifact_alignment
Revises: 0014_merge_11c_11seq
Create Date: 2026-05-27
"""

from alembic import op


revision = "0015_artifact_alignment"
down_revision = "0014_merge_11c_11seq"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'artifact_performance_records'
                  AND column_name = 'compass_alignment'
            ) THEN
                ALTER TABLE artifact_performance_records
                ADD COLUMN compass_alignment jsonb NOT NULL DEFAULT '{}'::jsonb;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE artifact_performance_records
        DROP COLUMN IF EXISTS compass_alignment;
        """
    )
