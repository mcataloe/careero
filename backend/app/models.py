import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class User(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)

    companies: Mapped[list["Company"]] = relationship(back_populates="user")
    roles: Mapped[list["Role"]] = relationship(back_populates="user")
    stride_evaluations: Mapped[list["StrideEvaluation"]] = relationship(
        back_populates="user"
    )
    resume_sources: Mapped[list["ResumeSource"]] = relationship(back_populates="user")
    workspaces: Mapped[list["Workspace"]] = relationship(back_populates="user")


class Workspace(TimestampMixin, Base):
    __tablename__ = "workspaces"
    __table_args__ = (
        Index("ix_workspaces_user_id", "user_id"),
        Index("ix_workspaces_status", "status"),
        Index("ix_workspaces_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    workspace_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="active")
    preferences: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    ai_context_summary: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    workspace_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="workspaces")
    roles: Mapped[list["Role"]] = relationship(back_populates="workspace")
    stride_evaluations: Mapped[list["StrideEvaluation"]] = relationship(
        back_populates="workspace"
    )
    applications: Mapped[list["Application"]] = relationship(back_populates="workspace")


class Company(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "companies"
    __table_args__ = (Index("ix_companies_user_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(2048))
    notes: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="companies")
    roles: Mapped[list["Role"]] = relationship(back_populates="company")


class Role(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (
        Index("ix_roles_user_id", "user_id"),
        Index("ix_roles_workspace_id", "workspace_id"),
        Index("ix_roles_company_id", "company_id"),
        Index("ix_roles_source_id", "source_id"),
        Index("ix_roles_status", "status"),
        Index("ix_roles_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=False,
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_sources.id"),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_url: Mapped[str | None] = mapped_column(String(2048))
    location: Mapped[str | None] = mapped_column(String(255))
    remote_type: Mapped[str | None] = mapped_column(String(100))
    compensation_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    compensation_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    compensation_currency: Mapped[str | None] = mapped_column(String(3))
    raw_description: Mapped[str | None] = mapped_column(Text)
    normalized_description: Mapped[str | None] = mapped_column(Text)
    parse_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="found")
    date_found: Mapped[date] = mapped_column(
        Date,
        server_default=func.current_date(),
        nullable=False,
    )
    date_posted: Mapped[date | None] = mapped_column(Date)

    user: Mapped[User] = relationship(back_populates="roles")
    workspace: Mapped[Workspace] = relationship(back_populates="roles")
    company: Mapped[Company] = relationship(back_populates="roles")
    source: Mapped["JobSource | None"] = relationship(back_populates="roles")
    stride_evaluations: Mapped[list["StrideEvaluation"]] = relationship(
        back_populates="role"
    )
    applications: Mapped[list["Application"]] = relationship(back_populates="role")


class JobSource(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "job_sources"
    __table_args__ = (
        Index("ix_job_sources_user_id", "user_id"),
        Index("uq_job_sources_user_source_type", "user_id", "source_type", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(100))
    website_url: Mapped[str | None] = mapped_column(String(2048))

    roles: Mapped[list[Role]] = relationship(back_populates="source")


class ResumeSource(TimestampMixin, Base):
    __tablename__ = "resume_sources"
    __table_args__ = (
        Index("ix_resume_sources_user_id", "user_id"),
        Index("ix_resume_sources_source_type", "source_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)

    user: Mapped[User] = relationship(back_populates="resume_sources")
    versions: Mapped[list["ResumeSourceVersion"]] = relationship(
        back_populates="source"
    )


class ResumeSourceVersion(TimestampMixin, Base):
    __tablename__ = "resume_source_versions"
    __table_args__ = (
        Index("ix_resume_source_versions_user_id", "user_id"),
        Index("ix_resume_source_versions_source_id", "source_id"),
        Index("ix_resume_source_versions_is_active", "is_active"),
        Index(
            "uq_resume_source_versions_active_user",
            "user_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume_sources.id"),
        nullable=False,
    )
    version_label: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_summary: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    source: Mapped[ResumeSource] = relationship(back_populates="versions")


class StrideEvaluation(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "stride_evaluations"
    __table_args__ = (
        Index("ix_stride_evaluations_user_id", "user_id"),
        Index("ix_stride_evaluations_workspace_id", "workspace_id"),
        Index("ix_stride_evaluations_role_id", "role_id"),
        Index("ix_stride_evaluations_status", "evaluation_status"),
        Index("ix_stride_evaluations_role_created_at", "role_id", "created_at"),
        Index(
            "ix_stride_evaluations_role_input_hash",
            "role_id",
            "evaluation_input_hash",
        ),
        Index("ix_stride_evaluations_ai_status", "ai_status"),
        Index("ix_stride_evaluations_ruleset_version", "ruleset_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=False,
    )
    evaluation_status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="completed",
    )
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    recommendation: Mapped[str | None] = mapped_column(String(100))
    confidence_level: Mapped[str | None] = mapped_column(String(100))
    summary: Mapped[str | None] = mapped_column(Text)
    strengths: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    concerns: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    resume_alignment: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    compensation_alignment: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    seniority_alignment: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    remote_alignment: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    technical_alignment: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    company_risk: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    ats_keywords: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    missing_keywords: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    model_used: Mapped[str | None] = mapped_column(String(100))
    prompt_version: Mapped[str | None] = mapped_column(String(100))
    ruleset_version: Mapped[str | None] = mapped_column(String(100))
    input_token_estimate: Mapped[int | None] = mapped_column(Integer)
    output_token_estimate: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ai_status: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
    role_content_hash: Mapped[str | None] = mapped_column(String(64))
    source_hash: Mapped[str | None] = mapped_column(String(64))
    evaluation_input_hash: Mapped[str | None] = mapped_column(String(64))
    raw_evaluation_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    user: Mapped[User] = relationship(back_populates="stride_evaluations")
    workspace: Mapped[Workspace] = relationship(back_populates="stride_evaluations")
    role: Mapped[Role] = relationship(back_populates="stride_evaluations")


class Application(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "applications"
    __table_args__ = (
        Index("ix_applications_user_id", "user_id"),
        Index("ix_applications_workspace_id", "workspace_id"),
        Index("ix_applications_role_id", "role_id"),
        Index("ix_applications_job_source_id", "job_source_id"),
        Index("ix_applications_current_state", "current_state"),
        Index("ix_applications_workspace_state", "workspace_id", "current_state"),
        Index("ix_applications_next_action_at", "next_action_at"),
        Index("ix_applications_archived_at", "archived_at"),
        Index(
            "uq_applications_active_role_id",
            "role_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=False,
    )
    job_source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_sources.id"),
    )
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    current_state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="discovered",
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_action_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    workflow_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    workspace: Mapped[Workspace] = relationship(back_populates="applications")
    role: Mapped[Role] = relationship(back_populates="applications")
    state_history: Mapped[list["ApplicationStateHistory"]] = relationship(
        back_populates="application",
        order_by="ApplicationStateHistory.changed_at",
    )
    note_entries: Mapped[list["ApplicationNote"]] = relationship(
        back_populates="application",
        order_by="ApplicationNote.created_at",
    )
    reminders: Mapped[list["ApplicationReminder"]] = relationship(
        back_populates="application",
        order_by="ApplicationReminder.due_at",
    )
    interview_stages: Mapped[list["ApplicationInterviewStage"]] = relationship(
        back_populates="application",
        order_by="ApplicationInterviewStage.scheduled_at",
    )
    external_links: Mapped[list["ApplicationExternalLink"]] = relationship(
        back_populates="application",
        order_by="ApplicationExternalLink.created_at",
    )


class ApplicationStateHistory(TimestampMixin, Base):
    __tablename__ = "application_state_history"
    __table_args__ = (
        Index("ix_application_state_history_application_id", "application_id"),
        Index("ix_application_state_history_workspace_id", "workspace_id"),
        Index("ix_application_state_history_changed_at", "changed_at"),
        Index("ix_application_state_history_to_state", "to_state"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    from_state: Mapped[str | None] = mapped_column(String(100))
    to_state: Mapped[str] = mapped_column(String(100), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    changed_by: Mapped[str] = mapped_column(String(100), nullable=False, default="user")
    reason: Mapped[str | None] = mapped_column(Text)
    history_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    application: Mapped[Application] = relationship(back_populates="state_history")


class ApplicationNote(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "application_notes"
    __table_args__ = (
        Index("ix_application_notes_application_id", "application_id"),
        Index("ix_application_notes_workspace_id", "workspace_id"),
        Index("ix_application_notes_created_at", "created_at"),
        Index("ix_application_notes_deleted_at", "deleted_at"),
        Index("ix_application_notes_note_type", "note_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    author: Mapped[str | None] = mapped_column(String(200))
    note_type: Mapped[str] = mapped_column(String(100), nullable=False, default="general")
    body: Mapped[str] = mapped_column(Text, nullable=False)

    application: Mapped[Application] = relationship(back_populates="note_entries")


class ApplicationReminder(TimestampMixin, Base):
    __tablename__ = "application_reminders"
    __table_args__ = (
        Index("ix_application_reminders_application_id", "application_id"),
        Index("ix_application_reminders_workspace_id", "workspace_id"),
        Index("ix_application_reminders_due_at", "due_at"),
        Index("ix_application_reminders_completed_at", "completed_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    application: Mapped[Application] = relationship(back_populates="reminders")


class ApplicationInterviewStage(TimestampMixin, Base):
    __tablename__ = "application_interview_stages"
    __table_args__ = (
        Index("ix_application_interview_stages_application_id", "application_id"),
        Index("ix_application_interview_stages_workspace_id", "workspace_id"),
        Index("ix_application_interview_stages_scheduled_at", "scheduled_at"),
        Index("ix_application_interview_stages_completed_at", "completed_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    stage_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    location: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    stage_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    application: Mapped[Application] = relationship(back_populates="interview_stages")


class ApplicationExternalLink(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "application_external_links"
    __table_args__ = (
        Index("ix_application_external_links_application_id", "application_id"),
        Index("ix_application_external_links_workspace_id", "workspace_id"),
        Index("ix_application_external_links_link_type", "link_type"),
        Index("ix_application_external_links_deleted_at", "deleted_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    link_type: Mapped[str | None] = mapped_column(String(100))
    link_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    application: Mapped[Application] = relationship(back_populates="external_links")


class GeneratedArtifact(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "generated_artifacts"
    __table_args__ = (
        Index("ix_generated_artifacts_user_id", "user_id"),
        Index("ix_generated_artifacts_workspace_id", "workspace_id"),
        Index("ix_generated_artifacts_application_id", "application_id"),
        Index("ix_generated_artifacts_role_id", "role_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
    )
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
    )
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    artifact_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )


class ArtifactPerformanceRecord(TimestampMixin, Base):
    __tablename__ = "artifact_performance_records"
    __table_args__ = (
        Index("ix_artifact_performance_records_user_id", "user_id"),
        Index("ix_artifact_performance_records_workspace_id", "workspace_id"),
        Index("ix_artifact_performance_records_role_id", "role_id"),
        Index("ix_artifact_performance_records_application_id", "application_id"),
        Index("ix_artifact_performance_records_artifact_id", "artifact_id"),
        Index("ix_artifact_performance_records_artifact_type", "artifact_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=False,
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
    )
    artifact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generated_artifacts.id"),
        nullable=False,
    )
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False)
    variant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version_label: Mapped[str | None] = mapped_column(String(100))
    targeted_role_category: Mapped[str | None] = mapped_column(String(100))
    application_state_when_used: Mapped[str | None] = mapped_column(String(100))
    response_outcome: Mapped[str | None] = mapped_column(String(100))
    interview_outcome: Mapped[str | None] = mapped_column(String(100))
    recruiter_engagement_outcome: Mapped[str | None] = mapped_column(String(100))
    stride_alignment: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    record_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )


class ActivityLog(Base):
    __tablename__ = "activity_log"
    __table_args__ = (
        Index("ix_activity_log_user_id", "user_id"),
        Index("ix_activity_log_entity", "entity_type", "entity_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
