import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, Text, func
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
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="found")
    date_found: Mapped[date] = mapped_column(
        Date,
        server_default=func.current_date(),
        nullable=False,
    )
    date_posted: Mapped[date | None] = mapped_column(Date)

    user: Mapped[User] = relationship(back_populates="roles")
    company: Mapped[Company] = relationship(back_populates="roles")
    source: Mapped["JobSource | None"] = relationship(back_populates="roles")
    stride_evaluations: Mapped[list["StrideEvaluation"]] = relationship(
        back_populates="role"
    )


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


class StrideEvaluation(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "stride_evaluations"
    __table_args__ = (
        Index("ix_stride_evaluations_user_id", "user_id"),
        Index("ix_stride_evaluations_role_id", "role_id"),
        Index("ix_stride_evaluations_status", "evaluation_status"),
        Index("ix_stride_evaluations_role_created_at", "role_id", "created_at"),
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
    raw_evaluation_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    user: Mapped[User] = relationship(back_populates="stride_evaluations")
    role: Mapped[Role] = relationship(back_populates="stride_evaluations")


class Application(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "applications"
    __table_args__ = (
        Index("ix_applications_user_id", "user_id"),
        Index("ix_applications_role_id", "role_id"),
        Index("ix_applications_job_source_id", "job_source_id"),
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
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_action_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)


class GeneratedArtifact(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "generated_artifacts"
    __table_args__ = (
        Index("ix_generated_artifacts_user_id", "user_id"),
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
