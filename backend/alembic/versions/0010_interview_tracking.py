"""structured interview tracking

Revision ID: 0010_interview_tracking
Revises: 0009_application_notes_links
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0010_interview_tracking"
down_revision = "0009_application_notes_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "application_interview_stages",
        sa.Column(
            "status",
            sa.String(length=100),
            server_default="planned",
            nullable=False,
        ),
    )
    op.add_column(
        "application_interview_stages",
        sa.Column(
            "interviewer_names",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "application_interview_stages",
        sa.Column("location_or_meeting_link", sa.String(length=2048), nullable=True),
    )
    op.add_column(
        "application_interview_stages",
        sa.Column("preparation_notes", sa.Text(), nullable=True),
    )
    op.add_column(
        "application_interview_stages",
        sa.Column("outcome_notes", sa.Text(), nullable=True),
    )
    op.add_column(
        "application_interview_stages",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE application_interview_stages
        SET
            stage_type = CASE
                WHEN stage_type IN (
                    'recruiter_screen',
                    'hiring_manager',
                    'technical',
                    'system_design',
                    'behavioral',
                    'panel',
                    'final',
                    'offer_discussion',
                    'other'
                ) THEN stage_type
                ELSE 'other'
            END,
            location_or_meeting_link = location,
            status = CASE
                WHEN completed_at IS NOT NULL THEN 'completed'
                WHEN scheduled_at IS NOT NULL THEN 'scheduled'
                ELSE 'planned'
            END
        """
    )
    op.drop_column("application_interview_stages", "location")
    op.create_index(
        "ix_application_interview_stages_status",
        "application_interview_stages",
        ["status"],
    )
    op.create_index(
        "ix_application_interview_stages_deleted_at",
        "application_interview_stages",
        ["deleted_at"],
    )


def downgrade() -> None:
    op.add_column(
        "application_interview_stages",
        sa.Column("location", sa.String(length=255), nullable=True),
    )
    op.execute(
        """
        UPDATE application_interview_stages
        SET location = left(location_or_meeting_link, 255)
        """
    )
    op.drop_index(
        "ix_application_interview_stages_deleted_at",
        table_name="application_interview_stages",
    )
    op.drop_index(
        "ix_application_interview_stages_status",
        table_name="application_interview_stages",
    )
    op.drop_column("application_interview_stages", "deleted_at")
    op.drop_column("application_interview_stages", "outcome_notes")
    op.drop_column("application_interview_stages", "preparation_notes")
    op.drop_column("application_interview_stages", "location_or_meeting_link")
    op.drop_column("application_interview_stages", "interviewer_names")
    op.drop_column("application_interview_stages", "status")
