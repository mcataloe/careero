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
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, synonym


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
    __table_args__ = (
        Index("ix_users_email_normalized", "email_normalized", unique=True),
        Index("ix_users_account_status", "account_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    email_normalized: Mapped[str | None] = mapped_column(String(320))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    salutation: Mapped[str | None] = mapped_column(String(50))
    pronouns: Mapped[str | None] = mapped_column(String(50))
    headshot_url: Mapped[str | None] = mapped_column(String(2048))
    password_hash: Mapped[str | None] = mapped_column(Text)
    password_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    auth_method: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="local_password",
    )
    account_status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="active",
    )
    failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    companies: Mapped[list["Company"]] = relationship(back_populates="user")
    opportunities: Mapped[list["Opportunity"]] = relationship(back_populates="user")
    roles = synonym("opportunities")
    compass_evaluations: Mapped[list["CompassEvaluation"]] = relationship(
        back_populates="user"
    )
    resume_sources: Mapped[list["ResumeSource"]] = relationship(back_populates="user")
    workspaces: Mapped[list["Workspace"]] = relationship(back_populates="user")
    auth_sessions: Mapped[list["AuthSession"]] = relationship(back_populates="user")


class AuthSession(TimestampMixin, Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        Index("ix_auth_sessions_user_id", "user_id"),
        Index("ix_auth_sessions_token_hash", "session_token_hash", unique=True),
        Index("ix_auth_sessions_expires_at", "expires_at"),
        Index("ix_auth_sessions_revoked_at", "revoked_at"),
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
    session_token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_agent: Mapped[str | None] = mapped_column(String(512))
    ip_hint: Mapped[str | None] = mapped_column(String(100))
    session_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    user: Mapped[User] = relationship(back_populates="auth_sessions")


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
    opportunities: Mapped[list["Opportunity"]] = relationship(back_populates="workspace")
    roles = synonym("opportunities")
    compass_evaluations: Mapped[list["CompassEvaluation"]] = relationship(
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
    opportunities: Mapped[list["Opportunity"]] = relationship(back_populates="company")
    roles = synonym("opportunities")


class Opportunity(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "opportunities"
    __table_args__ = (
        Index("ix_opportunities_user_id", "user_id"),
        Index("ix_opportunities_workspace_id", "workspace_id"),
        Index("ix_opportunities_company_id", "company_id"),
        Index("ix_opportunities_source_id", "source_id"),
        Index("ix_opportunities_status", "status"),
        Index("ix_opportunities_user_status", "user_id", "status"),
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

    user: Mapped[User] = relationship(back_populates="opportunities")
    workspace: Mapped[Workspace] = relationship(back_populates="opportunities")
    company: Mapped[Company] = relationship(back_populates="opportunities")
    source: Mapped["JobSource | None"] = relationship(back_populates="opportunities")
    compass_evaluations: Mapped[list["CompassEvaluation"]] = relationship(
        back_populates="opportunity"
    )
    applications: Mapped[list["Application"]] = relationship(back_populates="opportunity")


Role = Opportunity


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

    opportunities: Mapped[list[Opportunity]] = relationship(back_populates="source")
    roles = synonym("opportunities")


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


class CompassEvaluation(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "compass_evaluations"
    __table_args__ = (
        Index("ix_compass_evaluations_user_id", "user_id"),
        Index("ix_compass_evaluations_workspace_id", "workspace_id"),
        Index("ix_compass_evaluations_opportunity_id", "opportunity_id"),
        Index("ix_compass_evaluations_status", "evaluation_status"),
        Index("ix_compass_evaluations_opportunity_created_at", "opportunity_id", "created_at"),
        Index(
            "ix_compass_evaluations_opportunity_input_hash",
            "opportunity_id",
            "evaluation_input_hash",
        ),
        Index("ix_compass_evaluations_ai_status", "ai_status"),
        Index("ix_compass_evaluations_ruleset_version", "ruleset_version"),
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
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id"),
        nullable=False,
    )
    role_id = synonym("opportunity_id")
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

    user: Mapped[User] = relationship(back_populates="compass_evaluations")
    workspace: Mapped[Workspace] = relationship(back_populates="compass_evaluations")
    opportunity: Mapped[Opportunity] = relationship(back_populates="compass_evaluations")
    role = synonym("opportunity")


class Application(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "applications"
    __table_args__ = (
        Index("ix_applications_user_id", "user_id"),
        Index("ix_applications_workspace_id", "workspace_id"),
        Index("ix_applications_opportunity_id", "opportunity_id"),
        Index("ix_applications_job_source_id", "job_source_id"),
        Index("ix_applications_current_state", "current_state"),
        Index("ix_applications_workspace_state", "workspace_id", "current_state"),
        Index("ix_applications_next_action_at", "next_action_at"),
        Index("ix_applications_archived_at", "archived_at"),
        Index(
            "uq_applications_active_opportunity_id",
            "opportunity_id",
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
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id"),
        nullable=False,
    )
    role_id = synonym("opportunity_id")
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
    opportunity: Mapped[Opportunity] = relationship(back_populates="applications")
    role = synonym("opportunity")
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


class ApplicationInterviewStage(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "application_interview_stages"
    __table_args__ = (
        Index("ix_application_interview_stages_application_id", "application_id"),
        Index("ix_application_interview_stages_workspace_id", "workspace_id"),
        Index("ix_application_interview_stages_scheduled_at", "scheduled_at"),
        Index("ix_application_interview_stages_completed_at", "completed_at"),
        Index("ix_application_interview_stages_status", "status"),
        Index("ix_application_interview_stages_deleted_at", "deleted_at"),
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
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="planned")
    interviewer_names: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    location_or_meeting_link: Mapped[str | None] = mapped_column(String(2048))
    notes: Mapped[str | None] = mapped_column(Text)
    preparation_notes: Mapped[str | None] = mapped_column(Text)
    outcome_notes: Mapped[str | None] = mapped_column(Text)
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
        Index("ix_generated_artifacts_opportunity_id", "opportunity_id"),
        Index("ix_generated_artifacts_lifecycle_status", "lifecycle_status"),
        Index("ix_generated_artifacts_evaluation_id", "evaluation_id"),
        Index("ix_generated_artifacts_source_artifact_id", "source_artifact_id"),
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
    opportunity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id"),
    )
    role_id = synonym("opportunity_id")
    source_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generated_artifacts.id"),
    )
    evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("compass_evaluations.id"),
    )
    source_resume_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume_source_versions.id"),
    )
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="draft",
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
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
        Index("ix_artifact_performance_records_opportunity_id", "opportunity_id"),
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
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id"),
        nullable=False,
    )
    role_id = synonym("opportunity_id")
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
    compass_alignment: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    record_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )


class AutomationSuggestion(TimestampMixin, Base):
    __tablename__ = "automation_suggestions"
    __table_args__ = (
        Index("ix_automation_suggestions_user_id", "user_id"),
        Index("ix_automation_suggestions_workspace_id", "workspace_id"),
        Index("ix_automation_suggestions_target", "target_type", "target_id"),
        Index("ix_automation_suggestions_action_type", "action_type"),
        Index("ix_automation_suggestions_status", "status"),
        Index("ix_automation_suggestions_application_id", "application_id"),
        Index("ix_automation_suggestions_opportunity_id", "opportunity_id"),
        Index("ix_automation_suggestions_artifact_id", "artifact_id"),
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
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    opportunity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id"),
    )
    role_id = synonym("opportunity_id")
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
    )
    artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generated_artifacts.id"),
    )
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    basis: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(String(100), nullable=False)
    source_inputs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    preview: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    preview_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="active")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    policy_version: Mapped[str] = mapped_column(String(100), nullable=False)
    suggestion_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    approval_logs: Mapped[list["AutomationApprovalLog"]] = relationship(
        back_populates="suggestion"
    )


class AutomationApprovalLog(Base):
    __tablename__ = "automation_approval_logs"
    __table_args__ = (
        Index("ix_automation_approval_logs_user_id", "user_id"),
        Index("ix_automation_approval_logs_workspace_id", "workspace_id"),
        Index("ix_automation_approval_logs_suggestion_id", "suggestion_id"),
        Index("ix_automation_approval_logs_target", "target_type", "target_id"),
        Index("ix_automation_approval_logs_action_type", "action_type"),
        Index("ix_automation_approval_logs_approval_status", "approval_status"),
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
    suggestion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("automation_suggestions.id"),
        nullable=False,
    )
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    preview: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    preview_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    approval_status: Mapped[str] = mapped_column(String(100), nullable=False)
    dismissal_or_rejection_reason: Mapped[str | None] = mapped_column(Text)
    execution_status: Mapped[str] = mapped_column(String(100), nullable=False)
    execution_result: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    external_mutation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    policy_version: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    suggestion: Mapped[AutomationSuggestion] = relationship(back_populates="approval_logs")


class AccountLifecycleRequest(TimestampMixin, Base):
    __tablename__ = "account_lifecycle_requests"
    __table_args__ = (
        Index("ix_account_lifecycle_requests_user_id", "user_id"),
        Index("ix_account_lifecycle_requests_status", "status"),
        Index("ix_account_lifecycle_requests_user_status", "user_id", "status"),
        Index("ix_account_lifecycle_requests_type", "request_type"),
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
    request_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="requested")
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    request_reason: Mapped[str | None] = mapped_column(Text)
    target_type: Mapped[str | None] = mapped_column(String(100))
    target_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    request_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class AIUsageEvent(Base):
    __tablename__ = "ai_usage_events"
    __table_args__ = (
        Index("ix_ai_usage_events_user_id", "user_id"),
        Index("ix_ai_usage_events_workspace_id", "workspace_id"),
        Index("ix_ai_usage_events_opportunity_id", "opportunity_id"),
        Index("ix_ai_usage_events_feature", "feature"),
        Index("ix_ai_usage_events_event_type", "event_type"),
        Index("ix_ai_usage_events_created_at", "created_at"),
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
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
    )
    opportunity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id"),
    )
    role_id = synonym("opportunity_id")
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
    )
    artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generated_artifacts.id"),
    )
    feature: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(String(100))
    ruleset_version: Mapped[str | None] = mapped_column(String(100))
    input_token_estimate: Mapped[int | None] = mapped_column(Integer)
    output_token_estimate: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    error_class: Mapped[str | None] = mapped_column(String(200))
    content_hash: Mapped[str | None] = mapped_column(String(100))
    event_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
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
