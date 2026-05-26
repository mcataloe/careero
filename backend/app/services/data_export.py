from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.models import (
    ActivityLog,
    Application,
    ApplicationExternalLink,
    ApplicationInterviewStage,
    ApplicationNote,
    ApplicationReminder,
    ApplicationStateHistory,
    ArtifactPerformanceRecord,
    AutomationApprovalLog,
    AutomationSuggestion,
    Company,
    CompassEvaluation,
    GeneratedArtifact,
    JobSource,
    ResumeSource,
    ResumeSourceVersion,
    Role,
    User,
    Workspace,
)
from app.schemas.data_export import LocalDataExportResponse
from app.services.current_user import (
    CurrentUserContext,
    CurrentUserResolutionError,
    get_current_user_context,
    resolve_current_user,
)


class DataExportSeedMissingError(Exception):
    pass


class LocalDataExportService:
    def __init__(
        self,
        db: Session,
        *,
        settings: Settings | None = None,
        current_user_context: CurrentUserContext | None = None,
    ) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.current_user_context = current_user_context or get_current_user_context()

    def build_export(self) -> LocalDataExportResponse:
        user = self._current_user()
        user_filter = lambda model: model.user_id == user.id

        return LocalDataExportResponse(
            metadata={
                "schema_version": "careero.local_data_export.v1",
                "generated_at": _serialize_value(datetime.now(timezone.utc)),
                "readiness_note": (
                    "Local-first JSON export generated for the resolved current "
                    "local user. This does not create cloud storage, public links, "
                    "hosted account export, production auth, or legal compliance "
                    "certification."
                ),
                "current_user": {
                    "id": str(user.id),
                    "email": user.email,
                    "display_name": user.display_name,
                    "mode": self.current_user_context.mode,
                    "environment": self.settings.environment,
                },
                "derived_data_notes": [
                    "Career strategy summaries are omitted because current strategy is derived/read-only.",
                    "Advisor packet previews are omitted unless represented by persisted local records.",
                ],
            },
            workspaces=[
                _workspace(workspace)
                for workspace in self._list(
                    select(Workspace)
                    .where(user_filter(Workspace))
                    .order_by(Workspace.created_at.asc(), Workspace.id.asc())
                )
            ],
            companies=[
                _company(company)
                for company in self._list(
                    select(Company)
                    .where(user_filter(Company), Company.deleted_at.is_(None))
                    .order_by(Company.name.asc(), Company.id.asc())
                )
            ],
            job_sources=[
                _job_source(source)
                for source in self._list(
                    select(JobSource)
                    .where(user_filter(JobSource), JobSource.deleted_at.is_(None))
                    .order_by(JobSource.name.asc(), JobSource.id.asc())
                )
            ],
            opportunities=[
                _role(role)
                for role in self._list(
                    select(Role)
                    .where(user_filter(Role), Role.deleted_at.is_(None))
                    .order_by(Role.created_at.asc(), Role.id.asc())
                )
            ],
            resume_sources=[
                _resume_source(source)
                for source in self._list(
                    select(ResumeSource)
                    .where(user_filter(ResumeSource))
                    .order_by(ResumeSource.created_at.asc(), ResumeSource.id.asc())
                )
            ],
            resume_source_versions=[
                _resume_source_version(version)
                for version in self._list(
                    select(ResumeSourceVersion)
                    .where(user_filter(ResumeSourceVersion))
                    .order_by(
                        ResumeSourceVersion.created_at.asc(),
                        ResumeSourceVersion.id.asc(),
                    )
                )
            ],
            compass_evaluations=[
                _compass_evaluation(evaluation)
                for evaluation in self._list(
                    select(CompassEvaluation)
                    .where(
                        user_filter(CompassEvaluation),
                        CompassEvaluation.deleted_at.is_(None),
                    )
                    .order_by(
                        CompassEvaluation.created_at.asc(),
                        CompassEvaluation.id.asc(),
                    )
                )
            ],
            generated_artifacts=[
                _generated_artifact(artifact)
                for artifact in self._list(
                    select(GeneratedArtifact)
                    .where(
                        user_filter(GeneratedArtifact),
                        GeneratedArtifact.deleted_at.is_(None),
                    )
                    .order_by(
                        GeneratedArtifact.created_at.asc(),
                        GeneratedArtifact.id.asc(),
                    )
                )
            ],
            artifact_performance_records=[
                _artifact_performance(record)
                for record in self._list(
                    select(ArtifactPerformanceRecord)
                    .where(user_filter(ArtifactPerformanceRecord))
                    .order_by(
                        ArtifactPerformanceRecord.created_at.asc(),
                        ArtifactPerformanceRecord.id.asc(),
                    )
                )
            ],
            applications=[
                _application(application)
                for application in self._list(
                    select(Application)
                    .where(user_filter(Application), Application.deleted_at.is_(None))
                    .order_by(Application.created_at.asc(), Application.id.asc())
                )
            ],
            application_state_history=[
                _application_state_history(history)
                for history in self._list(
                    select(ApplicationStateHistory)
                    .where(user_filter(ApplicationStateHistory))
                    .order_by(
                        ApplicationStateHistory.changed_at.asc(),
                        ApplicationStateHistory.id.asc(),
                    )
                )
            ],
            notes=[
                _note(note)
                for note in self._list(
                    select(ApplicationNote)
                    .where(user_filter(ApplicationNote), ApplicationNote.deleted_at.is_(None))
                    .order_by(ApplicationNote.created_at.asc(), ApplicationNote.id.asc())
                )
            ],
            reminders=[
                _reminder(reminder)
                for reminder in self._list(
                    select(ApplicationReminder)
                    .where(user_filter(ApplicationReminder))
                    .order_by(
                        ApplicationReminder.created_at.asc(),
                        ApplicationReminder.id.asc(),
                    )
                )
            ],
            external_links=[
                _external_link(link)
                for link in self._list(
                    select(ApplicationExternalLink)
                    .where(
                        user_filter(ApplicationExternalLink),
                        ApplicationExternalLink.deleted_at.is_(None),
                    )
                    .order_by(
                        ApplicationExternalLink.created_at.asc(),
                        ApplicationExternalLink.id.asc(),
                    )
                )
            ],
            interview_stages=[
                _interview_stage(stage)
                for stage in self._list(
                    select(ApplicationInterviewStage)
                    .where(
                        user_filter(ApplicationInterviewStage),
                        ApplicationInterviewStage.deleted_at.is_(None),
                    )
                    .order_by(
                        ApplicationInterviewStage.created_at.asc(),
                        ApplicationInterviewStage.id.asc(),
                    )
                )
            ],
            activity_logs=[
                _activity_log(log)
                for log in self._list(
                    select(ActivityLog)
                    .where(user_filter(ActivityLog))
                    .order_by(ActivityLog.created_at.asc(), ActivityLog.id.asc())
                )
            ],
            automation_suggestions=[
                _automation_suggestion(suggestion)
                for suggestion in self._list(
                    select(AutomationSuggestion)
                    .where(user_filter(AutomationSuggestion))
                    .order_by(
                        AutomationSuggestion.created_at.asc(),
                        AutomationSuggestion.id.asc(),
                    )
                )
            ],
            automation_approval_logs=[
                _automation_approval_log(log)
                for log in self._list(
                    select(AutomationApprovalLog)
                    .where(user_filter(AutomationApprovalLog))
                    .order_by(
                        AutomationApprovalLog.created_at.asc(),
                        AutomationApprovalLog.id.asc(),
                    )
                )
            ],
        )

    def _current_user(self) -> User:
        try:
            return resolve_current_user(self.db, self.current_user_context)
        except CurrentUserResolutionError as exc:
            raise DataExportSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def _list(self, statement) -> list[Any]:
        return list(self.db.scalars(statement))


def _base(record: Any, fields: list[str]) -> dict[str, Any]:
    return {field: _serialize_value(getattr(record, field)) for field in fields}


def _workspace(record: Workspace) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "user_id",
            "title",
            "description",
            "workspace_type",
            "status",
            "preferences",
            "ai_context_summary",
            "tags",
            "workspace_metadata",
            "archived_at",
            "created_at",
            "updated_at",
        ],
    )


def _company(record: Company) -> dict[str, Any]:
    return _base(
        record,
        ["id", "user_id", "name", "website_url", "notes", "created_at", "updated_at"],
    )


def _job_source(record: JobSource) -> dict[str, Any]:
    return _base(
        record,
        ["id", "user_id", "name", "source_type", "website_url", "created_at", "updated_at"],
    )


def _role(record: Role) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "user_id",
            "workspace_id",
            "company_id",
            "source_id",
            "title",
            "job_url",
            "location",
            "remote_type",
            "compensation_min",
            "compensation_max",
            "compensation_currency",
            "raw_description",
            "normalized_description",
            "parse_metadata",
            "status",
            "date_found",
            "date_posted",
            "created_at",
            "updated_at",
        ],
    )


def _resume_source(record: ResumeSource) -> dict[str, Any]:
    return _base(record, ["id", "user_id", "name", "source_type", "created_at", "updated_at"])


def _resume_source_version(record: ResumeSourceVersion) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "user_id",
            "source_id",
            "version_label",
            "raw_text",
            "normalized_summary",
            "is_active",
            "created_at",
            "updated_at",
        ],
    )


def _compass_evaluation(record: CompassEvaluation) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "user_id",
            "workspace_id",
            "role_id",
            "evaluation_status",
            "overall_score",
            "recommendation",
            "confidence_level",
            "summary",
            "strengths",
            "concerns",
            "resume_alignment",
            "compensation_alignment",
            "seniority_alignment",
            "remote_alignment",
            "technical_alignment",
            "company_risk",
            "ats_keywords",
            "missing_keywords",
            "model_used",
            "prompt_version",
            "ruleset_version",
            "input_token_estimate",
            "output_token_estimate",
            "latency_ms",
            "ai_enabled",
            "ai_status",
            "error_message",
            "role_content_hash",
            "source_hash",
            "evaluation_input_hash",
            "raw_evaluation_json",
            "created_at",
            "updated_at",
        ],
    )


def _generated_artifact(record: GeneratedArtifact) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "user_id",
            "workspace_id",
            "application_id",
            "role_id",
            "artifact_type",
            "title",
            "content",
            "artifact_metadata",
            "created_at",
            "updated_at",
        ],
    )


def _artifact_performance(record: ArtifactPerformanceRecord) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "user_id",
            "workspace_id",
            "role_id",
            "application_id",
            "artifact_id",
            "artifact_type",
            "variant_name",
            "version_label",
            "targeted_role_category",
            "application_state_when_used",
            "response_outcome",
            "interview_outcome",
            "recruiter_engagement_outcome",
            "compass_alignment",
            "generated_at",
            "submitted_at",
            "record_metadata",
            "created_at",
            "updated_at",
        ],
    )


def _application(record: Application) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "user_id",
            "workspace_id",
            "role_id",
            "job_source_id",
            "status",
            "current_state",
            "applied_at",
            "next_action_at",
            "archived_at",
            "reactivated_at",
            "notes",
            "workflow_metadata",
            "created_at",
            "updated_at",
        ],
    )


def _application_state_history(record: ApplicationStateHistory) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "application_id",
            "user_id",
            "workspace_id",
            "from_state",
            "to_state",
            "changed_at",
            "changed_by",
            "reason",
            "history_metadata",
            "created_at",
            "updated_at",
        ],
    )


def _note(record: ApplicationNote) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "application_id",
            "user_id",
            "workspace_id",
            "author",
            "note_type",
            "body",
            "created_at",
            "updated_at",
        ],
    )


def _reminder(record: ApplicationReminder) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "application_id",
            "user_id",
            "workspace_id",
            "due_at",
            "title",
            "notes",
            "completed_at",
            "created_at",
            "updated_at",
        ],
    )


def _external_link(record: ApplicationExternalLink) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "application_id",
            "user_id",
            "workspace_id",
            "label",
            "url",
            "link_type",
            "link_metadata",
            "created_at",
            "updated_at",
        ],
    )


def _interview_stage(record: ApplicationInterviewStage) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "application_id",
            "user_id",
            "workspace_id",
            "stage_type",
            "title",
            "scheduled_at",
            "completed_at",
            "status",
            "interviewer_names",
            "location_or_meeting_link",
            "notes",
            "preparation_notes",
            "outcome_notes",
            "stage_metadata",
            "created_at",
            "updated_at",
        ],
    )


def _activity_log(record: ActivityLog) -> dict[str, Any]:
    return _base(
        record,
        ["id", "user_id", "entity_type", "entity_id", "action", "details", "created_at"],
    )


def _automation_suggestion(record: AutomationSuggestion) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "user_id",
            "workspace_id",
            "target_type",
            "target_id",
            "role_id",
            "application_id",
            "artifact_id",
            "action_type",
            "title",
            "summary",
            "reason",
            "basis",
            "confidence",
            "source_inputs",
            "preview",
            "preview_hash",
            "status",
            "expires_at",
            "policy_version",
            "suggestion_metadata",
            "created_at",
            "updated_at",
        ],
    )


def _automation_approval_log(record: AutomationApprovalLog) -> dict[str, Any]:
    return _base(
        record,
        [
            "id",
            "user_id",
            "workspace_id",
            "suggestion_id",
            "actor",
            "target_type",
            "target_id",
            "action_type",
            "preview",
            "preview_hash",
            "approval_status",
            "dismissal_or_rejection_reason",
            "execution_status",
            "execution_result",
            "external_mutation",
            "policy_version",
            "created_at",
            "decided_at",
            "executed_at",
        ],
    )


def _serialize_value(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        normalized = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return normalized.isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _serialize_value(item) for key, item in value.items()}
    return value
