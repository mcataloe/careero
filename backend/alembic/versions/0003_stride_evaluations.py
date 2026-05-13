"""stride evaluation foundation

Revision ID: 0003_stride_evaluations
Revises: 0002_role_intake
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_stride_evaluations"
down_revision = "0002_role_intake"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "stride_evaluations",
        sa.Column(
            "evaluation_status",
            sa.String(length=100),
            server_default="completed",
            nullable=False,
        ),
    )
    op.add_column(
        "stride_evaluations",
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=True),
    )
    op.add_column(
        "stride_evaluations",
        sa.Column("recommendation", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "stride_evaluations",
        sa.Column("confidence_level", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "stride_evaluations",
        sa.Column(
            "strengths",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "stride_evaluations",
        sa.Column(
            "concerns",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    for column_name in (
        "resume_alignment",
        "compensation_alignment",
        "seniority_alignment",
        "remote_alignment",
        "technical_alignment",
        "company_risk",
    ):
        op.add_column(
            "stride_evaluations",
            sa.Column(
                column_name,
                postgresql.JSONB(astext_type=sa.Text()),
                server_default=sa.text("'{}'::jsonb"),
                nullable=False,
            ),
        )
    op.add_column(
        "stride_evaluations",
        sa.Column(
            "ats_keywords",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "stride_evaluations",
        sa.Column(
            "missing_keywords",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "stride_evaluations",
        sa.Column(
            "raw_evaluation_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )

    op.execute(
        """
        UPDATE stride_evaluations
        SET raw_evaluation_json = jsonb_strip_nulls(
            jsonb_build_object(
                'legacy_scores', scores,
                'legacy_notes', notes
            )
        )
        """
    )

    op.create_index(
        "ix_stride_evaluations_status",
        "stride_evaluations",
        ["evaluation_status"],
    )
    op.create_index(
        "ix_stride_evaluations_role_created_at",
        "stride_evaluations",
        ["role_id", sa.text("created_at DESC")],
    )

    op.drop_column("stride_evaluations", "notes")
    op.drop_column("stride_evaluations", "scores")


def downgrade() -> None:
    op.add_column(
        "stride_evaluations",
        sa.Column(
            "scores",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "stride_evaluations",
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.execute(
        """
        UPDATE stride_evaluations
        SET
            scores = COALESCE(raw_evaluation_json->'legacy_scores', '{}'::jsonb),
            notes = raw_evaluation_json->>'legacy_notes'
        """
    )

    op.drop_index("ix_stride_evaluations_role_created_at", table_name="stride_evaluations")
    op.drop_index("ix_stride_evaluations_status", table_name="stride_evaluations")
    op.drop_column("stride_evaluations", "raw_evaluation_json")
    op.drop_column("stride_evaluations", "missing_keywords")
    op.drop_column("stride_evaluations", "ats_keywords")
    op.drop_column("stride_evaluations", "company_risk")
    op.drop_column("stride_evaluations", "technical_alignment")
    op.drop_column("stride_evaluations", "remote_alignment")
    op.drop_column("stride_evaluations", "seniority_alignment")
    op.drop_column("stride_evaluations", "compensation_alignment")
    op.drop_column("stride_evaluations", "resume_alignment")
    op.drop_column("stride_evaluations", "concerns")
    op.drop_column("stride_evaluations", "strengths")
    op.drop_column("stride_evaluations", "confidence_level")
    op.drop_column("stride_evaluations", "recommendation")
    op.drop_column("stride_evaluations", "overall_score")
    op.drop_column("stride_evaluations", "evaluation_status")
