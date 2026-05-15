from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, FormatChecker
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.constants import ApplicationWorkflowState, RoleStatus
from app.models import (
    Application,
    ApplicationExternalLink,
    ApplicationInterviewStage,
    ApplicationNote,
    ApplicationReminder,
    ApplicationStateHistory,
    GeneratedArtifact,
    Role,
    StrideEvaluation,
    User,
    Workspace,
)
from app.schemas.applications import (
    ApplicationExternalLinkCreate,
    ApplicationExternalLinkUpdate,
    ApplicationInterviewStageCreate,
    ApplicationInterviewStageUpdate,
    ApplicationNoteCreate,
    ApplicationNoteUpdate,
    ApplicationReminderCreate,
    ApplicationReminderUpdate,
    ApplicationMetadataUpdate,
    ApplicationStateTransitionRequest,
)
from app.seed import DEFAULT_LOCAL_USER_ID, DEFAULT_LOCAL_USER_DISPLAY_NAME
from app.services.activity_log import ActivityLogService
from app.services.workspace_context import is_workspace_active_for_new_work


CONTRACT_VERSION = "careero.contracts.v1"


class ApplicationWorkflowError(Exception):
    pass


class ApplicationWorkflowSeedMissingError(ApplicationWorkflowError):
    pass


class ApplicationWorkflowNotFoundError(ApplicationWorkflowError):
    pass


class ApplicationWorkflowWorkspaceInactiveError(ApplicationWorkflowError):
    pass


class ApplicationWorkflowWorkspaceNotFoundError(ApplicationWorkflowError):
    pass


class ApplicationWorkflowValidationError(ApplicationWorkflowError):
    pass


class ApplicationWorkflowService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.activity_log = ActivityLogService(db)
        self._schema_validator = _application_state_validator()

    def get_default_user(self) -> User:
        user = self.db.get(User, DEFAULT_LOCAL_USER_ID)
        if user is None or user.deleted_at is not None:
            raise ApplicationWorkflowSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            )
        return user

    def get_or_create_for_role(self, role_id: uuid.UUID) -> dict[str, Any]:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise ApplicationWorkflowNotFoundError("Role not found")

        existing = self._get_active_application_for_role(
            role_id=role.id,
            user_id=user.id,
        )
        if existing is not None:
            return self.detail(existing)

        if not is_workspace_active_for_new_work(role.workspace):
            raise ApplicationWorkflowWorkspaceInactiveError(
                "Workspace is not active for new application workflows"
            )

        state = _workflow_state_for_role_status(role.status)
        now = datetime.now(timezone.utc)
        application = Application(
            user_id=user.id,
            workspace_id=role.workspace_id,
            role_id=role.id,
            job_source_id=role.source_id,
            status=state.value,
            current_state=state.value,
            archived_at=now if state == ApplicationWorkflowState.ARCHIVED else None,
            workflow_metadata={"createdFromRole": True},
        )
        self.db.add(application)
        self.db.flush()
        self._append_history(
            application,
            from_state=None,
            to_state=state.value,
            changed_by="system",
            reason="Initial application workflow state.",
            metadata={"source": "role"},
        )
        self._log_activity(
            user_id=user.id,
            application=application,
            action="application.created",
            details={"role_id": str(role.id), "state": state.value},
        )
        self.db.commit()
        return self.get_application(application.id)

    def list_applications(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
        include_inactive: bool = False,
    ) -> list[dict[str, Any]]:
        user = self.get_default_user()
        filters = [Application.user_id == user.id, Application.deleted_at.is_(None)]
        if workspace_id is not None:
            workspace = self._get_workspace_for_user(
                workspace_id=workspace_id,
                user_id=user.id,
            )
            if workspace is None:
                raise ApplicationWorkflowWorkspaceNotFoundError("Workspace not found")
            filters.append(Application.workspace_id == workspace.id)
        if not include_inactive:
            filters.extend(
                [
                    Application.archived_at.is_(None),
                    Application.current_state != ApplicationWorkflowState.ARCHIVED.value,
                ]
            )
        statement = (
            select(Application)
            .where(*filters)
            .options(*_application_load_options())
            .order_by(Application.updated_at.desc(), Application.created_at.desc())
        )
        return [self.summary(application) for application in self.db.scalars(statement)]

    def get_application(self, application_id: uuid.UUID) -> dict[str, Any]:
        application = self._get_application(application_id)
        if application is None:
            raise ApplicationWorkflowNotFoundError("Application workflow not found")
        return self.detail(application)

    def update_application(
        self,
        application_id: uuid.UUID,
        payload: ApplicationMetadataUpdate,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        updates = payload.model_dump(exclude_unset=True)
        changed_fields: list[str] = []
        if "workflow_metadata" in updates and updates["workflow_metadata"] is not None:
            application.workflow_metadata = {
                **(application.workflow_metadata or {}),
                **updates["workflow_metadata"],
            }
            changed_fields.append("workflow_metadata")
        if "applied_at" in updates:
            application.applied_at = updates["applied_at"]
            changed_fields.append("applied_at")
        if "next_action_at" in updates:
            application.next_action_at = updates["next_action_at"]
            changed_fields.append("next_action_at")

        if changed_fields:
            self._log_activity(
                user_id=application.user_id,
                application=application,
                action="application.updated",
                details={"changed_fields": sorted(changed_fields)},
            )
            self.db.commit()
        else:
            self.db.rollback()
        return self.get_application(application.id)

    def transition_state(
        self,
        application_id: uuid.UUID,
        payload: ApplicationStateTransitionRequest,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        previous_state = application.current_state
        next_state = payload.state.value
        if previous_state == next_state:
            self.db.rollback()
            return self.detail(application)

        now = datetime.now(timezone.utc)
        application.current_state = next_state
        application.status = next_state
        if next_state == ApplicationWorkflowState.ARCHIVED.value:
            application.archived_at = now
        elif previous_state == ApplicationWorkflowState.ARCHIVED.value:
            application.archived_at = None
            application.reactivated_at = now
        if next_state == ApplicationWorkflowState.APPLIED.value and application.applied_at is None:
            application.applied_at = now

        self._append_history(
            application,
            from_state=previous_state,
            to_state=next_state,
            changed_by=payload.changed_by,
            reason=payload.reason,
            metadata=payload.metadata,
        )
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.state_changed",
            details={
                "from_state": previous_state,
                "to_state": next_state,
            },
        )
        self.db.commit()
        return self.get_application(application.id)

    def summary(self, application: Application) -> dict[str, Any]:
        role = application.role
        company = role.company
        latest_stride = self._latest_stride_summary(application)
        return {
            "id": application.id,
            "role_id": application.role_id,
            "workspace_id": application.workspace_id,
            "title": role.title,
            "company": {
                "id": company.id,
                "name": company.name,
                "website_url": company.website_url,
            },
            "current_state": application.current_state,
            "applied_at": application.applied_at,
            "next_action_at": application.next_action_at,
            "updated_at": application.updated_at,
            "archived_at": application.archived_at,
            "stride": latest_stride,
            "resume_artifact": self._latest_artifact_summary(
                application,
                artifact_type="tailored_resume",
            ),
            "cover_letter_artifact": self._latest_artifact_summary(
                application,
                artifact_type="cover_letter",
            ),
            "counts": {
                "notes": len(application.note_entries),
                "reminders": len(application.reminders),
                "interviews": len(application.interview_stages),
            },
        }

    def detail(self, application: Application) -> dict[str, Any]:
        role = application.role
        company = role.company
        application_state = self.serialize(application)
        return {
            **self.summary(application),
            "workflow_metadata": application.workflow_metadata or {},
            "application_state": application_state,
            "state_history": application_state["stateHistory"],
            "role": {
                "id": role.id,
                "workspace_id": role.workspace_id,
                "title": role.title,
                "status": role.status,
                "company": {
                    "id": company.id,
                    "name": company.name,
                    "website_url": company.website_url,
                },
                "job_url": role.job_url,
                "location": role.location,
                "remote_type": role.remote_type,
            },
        }

    def create_note(
        self,
        application_id: uuid.UUID,
        payload: ApplicationNoteCreate,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        note = ApplicationNote(
            application_id=application.id,
            user_id=application.user_id,
            workspace_id=application.workspace_id,
            author=payload.author or DEFAULT_LOCAL_USER_DISPLAY_NAME,
            body=payload.body,
        )
        self.db.add(note)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.note.created",
            details={},
        )
        self.db.commit()
        return self.get_application(application.id)

    def update_note(
        self,
        application_id: uuid.UUID,
        note_id: uuid.UUID,
        payload: ApplicationNoteUpdate,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        note = self._require_child(ApplicationNote, application, note_id)
        updates = payload.model_dump(exclude_unset=True)
        if "author" in updates:
            note.author = updates["author"]
        if "body" in updates:
            note.body = updates["body"]
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.note.updated",
            details={"note_id": str(note.id)},
        )
        self.db.commit()
        return self.get_application(application.id)

    def delete_note(self, application_id: uuid.UUID, note_id: uuid.UUID) -> None:
        application = self._require_application(application_id)
        note = self._require_child(ApplicationNote, application, note_id)
        self.db.delete(note)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.note.deleted",
            details={"note_id": str(note.id)},
        )
        self.db.commit()

    def create_reminder(
        self,
        application_id: uuid.UUID,
        payload: ApplicationReminderCreate,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        reminder = ApplicationReminder(
            application_id=application.id,
            user_id=application.user_id,
            workspace_id=application.workspace_id,
            due_at=payload.due_at,
            title=payload.title,
            notes=payload.notes,
        )
        self.db.add(reminder)
        self.db.flush()
        self._sync_next_action(application)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.reminder.created",
            details={"reminder_id": str(reminder.id)},
        )
        self.db.commit()
        return self.get_application(application.id)

    def update_reminder(
        self,
        application_id: uuid.UUID,
        reminder_id: uuid.UUID,
        payload: ApplicationReminderUpdate,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        reminder = self._require_child(ApplicationReminder, application, reminder_id)
        for field_name, value in payload.model_dump(exclude_unset=True).items():
            setattr(reminder, field_name, value)
        self.db.flush()
        self._sync_next_action(application)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.reminder.updated",
            details={"reminder_id": str(reminder.id)},
        )
        self.db.commit()
        return self.get_application(application.id)

    def complete_reminder(
        self,
        application_id: uuid.UUID,
        reminder_id: uuid.UUID,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        reminder = self._require_child(ApplicationReminder, application, reminder_id)
        reminder.completed_at = datetime.now(timezone.utc)
        self.db.flush()
        self._sync_next_action(application)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.reminder.completed",
            details={"reminder_id": str(reminder.id)},
        )
        self.db.commit()
        return self.get_application(application.id)

    def create_interview_stage(
        self,
        application_id: uuid.UUID,
        payload: ApplicationInterviewStageCreate,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        stage = ApplicationInterviewStage(
            application_id=application.id,
            user_id=application.user_id,
            workspace_id=application.workspace_id,
            stage_type=payload.stage_type,
            title=payload.title,
            scheduled_at=payload.scheduled_at,
            location=payload.location,
            notes=payload.notes,
            stage_metadata=payload.metadata,
        )
        self.db.add(stage)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.interview_stage.created",
            details={"stage_type": stage.stage_type},
        )
        self.db.commit()
        return self.get_application(application.id)

    def update_interview_stage(
        self,
        application_id: uuid.UUID,
        stage_id: uuid.UUID,
        payload: ApplicationInterviewStageUpdate,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        stage = self._require_child(ApplicationInterviewStage, application, stage_id)
        updates = payload.model_dump(exclude_unset=True)
        if "metadata" in updates:
            stage.stage_metadata = updates.pop("metadata") or {}
        for field_name, value in updates.items():
            setattr(stage, field_name, value)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.interview_stage.updated",
            details={"stage_id": str(stage.id)},
        )
        self.db.commit()
        return self.get_application(application.id)

    def complete_interview_stage(
        self,
        application_id: uuid.UUID,
        stage_id: uuid.UUID,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        stage = self._require_child(ApplicationInterviewStage, application, stage_id)
        stage.completed_at = datetime.now(timezone.utc)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.interview_stage.completed",
            details={"stage_id": str(stage.id)},
        )
        self.db.commit()
        return self.get_application(application.id)

    def create_external_link(
        self,
        application_id: uuid.UUID,
        payload: ApplicationExternalLinkCreate,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        link = ApplicationExternalLink(
            application_id=application.id,
            user_id=application.user_id,
            workspace_id=application.workspace_id,
            label=payload.label,
            url=str(payload.url),
            link_type=payload.type,
            link_metadata=payload.metadata,
        )
        self.db.add(link)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.external_link.created",
            details={"link_type": link.link_type},
        )
        self.db.commit()
        return self.get_application(application.id)

    def update_external_link(
        self,
        application_id: uuid.UUID,
        link_id: uuid.UUID,
        payload: ApplicationExternalLinkUpdate,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        link = self._require_child(ApplicationExternalLink, application, link_id)
        updates = payload.model_dump(exclude_unset=True)
        if "type" in updates:
            link.link_type = updates.pop("type")
        if "url" in updates and updates["url"] is not None:
            updates["url"] = str(updates["url"])
        if "metadata" in updates:
            link.link_metadata = updates.pop("metadata") or {}
        for field_name, value in updates.items():
            setattr(link, field_name, value)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.external_link.updated",
            details={"link_id": str(link.id)},
        )
        self.db.commit()
        return self.get_application(application.id)

    def delete_external_link(self, application_id: uuid.UUID, link_id: uuid.UUID) -> None:
        application = self._require_application(application_id)
        link = self._require_child(ApplicationExternalLink, application, link_id)
        self.db.delete(link)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.external_link.deleted",
            details={"link_id": str(link.id)},
        )
        self.db.commit()

    def serialize(self, application: Application) -> dict[str, Any]:
        state_history = [
            {
                "state": history.to_state,
                "changedAt": _isoformat(history.changed_at),
                "changedBy": history.changed_by,
                "reason": history.reason,
                "metadata": history.history_metadata or {},
            }
            for history in application.state_history
        ]
        if not state_history:
            state_history = [
                {
                    "state": application.current_state,
                    "changedAt": _isoformat(application.created_at),
                    "changedBy": "system",
                    "reason": "Initial application workflow state.",
                    "metadata": {"source": "serializer_fallback"},
                }
            ]

        contract = {
            "contractVersion": CONTRACT_VERSION,
            "id": str(application.id),
            "workspaceId": str(application.workspace_id),
            "opportunityId": str(application.role_id),
            "currentState": application.current_state,
            "stateHistory": state_history,
            "reminders": [
                {
                    "id": str(reminder.id),
                    "dueAt": _isoformat(reminder.due_at),
                    "title": reminder.title,
                    "notes": reminder.notes,
                    "completedAt": _isoformat(reminder.completed_at),
                }
                for reminder in application.reminders
            ],
            "notes": [
                {
                    "id": str(note.id),
                    "createdAt": _isoformat(note.created_at),
                    "author": note.author,
                    "body": note.body,
                }
                for note in application.note_entries
            ],
            "interviewStages": [
                {
                    "id": str(stage.id),
                    "stageType": stage.stage_type,
                    "title": stage.title,
                    "scheduledAt": _isoformat(stage.scheduled_at),
                    "completedAt": _isoformat(stage.completed_at),
                    "location": stage.location,
                    "notes": stage.notes,
                    "metadata": stage.stage_metadata or {},
                }
                for stage in application.interview_stages
            ],
            "externalLinks": [
                {
                    "label": link.label,
                    "url": link.url,
                    "type": link.link_type,
                }
                for link in application.external_links
            ],
            "metadata": {
                **(application.workflow_metadata or {}),
                "appliedAt": _isoformat(application.applied_at),
                "nextActionAt": _isoformat(application.next_action_at),
                "archivedAt": _isoformat(application.archived_at),
                "reactivatedAt": _isoformat(application.reactivated_at),
                "legacyStatus": application.status,
            },
            "createdAt": _isoformat(application.created_at),
            "updatedAt": _isoformat(application.updated_at),
        }
        try:
            self._schema_validator.validate(contract)
        except JsonSchemaValidationError as exc:
            raise ApplicationWorkflowValidationError(
                f"ApplicationState contract validation failed: {exc.message}"
            ) from exc
        return contract

    def _get_active_role(self, *, role_id: uuid.UUID, user_id: uuid.UUID) -> Role | None:
        statement = (
            select(Role)
            .where(
                Role.id == role_id,
                Role.user_id == user_id,
                Role.deleted_at.is_(None),
                Role.status != RoleStatus.ARCHIVED.value,
            )
            .options(joinedload(Role.company), selectinload(Role.workspace))
        )
        return self.db.scalar(statement)

    def _get_active_application_for_role(
        self,
        *,
        role_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Application | None:
        statement = (
            select(Application)
            .where(
                Application.role_id == role_id,
                Application.user_id == user_id,
                Application.deleted_at.is_(None),
            )
            .options(*_application_load_options())
        )
        return self.db.scalar(statement)

    def _get_workspace_for_user(
        self,
        *,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Workspace | None:
        statement = select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.user_id == user_id,
        )
        return self.db.scalar(statement)

    def _get_application(self, application_id: uuid.UUID) -> Application | None:
        user = self.get_default_user()
        statement = (
            select(Application)
            .where(
                Application.id == application_id,
                Application.user_id == user.id,
                Application.deleted_at.is_(None),
            )
            .options(*_application_load_options())
        )
        return self.db.scalar(statement)

    def _require_application(self, application_id: uuid.UUID) -> Application:
        application = self._get_application(application_id)
        if application is None:
            raise ApplicationWorkflowNotFoundError("Application workflow not found")
        return application

    def _require_child(self, model, application: Application, child_id: uuid.UUID):
        child = self.db.get(model, child_id)
        if child is None or child.application_id != application.id:
            raise ApplicationWorkflowNotFoundError("Application workflow child not found")
        return child

    def _append_history(
        self,
        application: Application,
        *,
        from_state: str | None,
        to_state: str,
        changed_by: str,
        reason: str | None,
        metadata: dict[str, Any],
    ) -> None:
        self.db.add(
            ApplicationStateHistory(
                application_id=application.id,
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                from_state=from_state,
                to_state=to_state,
                changed_by=changed_by,
                reason=reason,
                history_metadata=metadata or {},
            )
        )

    def _sync_next_action(self, application: Application) -> None:
        application.next_action_at = self.db.scalar(
            select(func.min(ApplicationReminder.due_at)).where(
                ApplicationReminder.application_id == application.id,
                ApplicationReminder.completed_at.is_(None),
            )
        )

    def _log_activity(
        self,
        *,
        user_id: uuid.UUID,
        application: Application,
        action: str,
        details: dict[str, Any],
    ) -> None:
        self.activity_log.append(
            user_id=user_id,
            entity_type="application",
            entity_id=application.id,
            action=action,
            details={
                **details,
                "workspace_id": str(application.workspace_id),
                "role_id": str(application.role_id),
            },
        )

    def _latest_stride_summary(self, application: Application) -> dict[str, Any] | None:
        evaluation = self.db.scalar(
            select(StrideEvaluation)
            .where(
                StrideEvaluation.user_id == application.user_id,
                StrideEvaluation.workspace_id == application.workspace_id,
                StrideEvaluation.role_id == application.role_id,
                StrideEvaluation.deleted_at.is_(None),
            )
            .order_by(StrideEvaluation.created_at.desc(), StrideEvaluation.id.desc())
            .limit(1)
        )
        if evaluation is None:
            return None
        return {
            "id": evaluation.id,
            "evaluation_status": evaluation.evaluation_status,
            "recommendation": evaluation.recommendation,
            "overall_score": evaluation.overall_score,
            "summary": evaluation.summary,
            "updated_at": evaluation.updated_at,
        }

    def _latest_artifact_summary(
        self,
        application: Application,
        *,
        artifact_type: str,
    ) -> dict[str, Any] | None:
        artifact = self.db.scalar(
            select(GeneratedArtifact)
            .where(
                GeneratedArtifact.user_id == application.user_id,
                GeneratedArtifact.workspace_id == application.workspace_id,
                GeneratedArtifact.role_id == application.role_id,
                GeneratedArtifact.artifact_type == artifact_type,
                GeneratedArtifact.deleted_at.is_(None),
            )
            .order_by(GeneratedArtifact.created_at.desc(), GeneratedArtifact.id.desc())
            .limit(1)
        )
        if artifact is None:
            return None
        contract = (
            artifact.artifact_metadata.get("contract")
            if artifact.artifact_metadata
            else None
        )
        revision = contract.get("revision", {}) if isinstance(contract, dict) else {}
        return {
            "id": artifact.id,
            "artifact_type": artifact.artifact_type,
            "title": artifact.title,
            "status": (
                contract.get("lifecycleStatus")
                if isinstance(contract, dict)
                else None
            ),
            "revision_number": revision.get("revisionNumber"),
            "updated_at": artifact.updated_at,
        }


def _application_load_options():
    return (
        joinedload(Application.role).joinedload(Role.company),
        selectinload(Application.state_history),
        selectinload(Application.note_entries),
        selectinload(Application.reminders),
        selectinload(Application.interview_stages),
        selectinload(Application.external_links),
    )


def _workflow_state_for_role_status(status: str) -> ApplicationWorkflowState:
    mapping = {
        RoleStatus.FOUND.value: ApplicationWorkflowState.DISCOVERED,
        RoleStatus.INTERESTED.value: ApplicationWorkflowState.INTERESTED,
        RoleStatus.APPLIED.value: ApplicationWorkflowState.APPLIED,
        RoleStatus.ARCHIVED.value: ApplicationWorkflowState.ARCHIVED,
    }
    if status in {state.value for state in ApplicationWorkflowState}:
        return ApplicationWorkflowState(status)
    return mapping.get(status, ApplicationWorkflowState.DISCOVERED)


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


@lru_cache(maxsize=1)
def _application_state_validator() -> Draft7Validator:
    schema_path = (
        Path(__file__).resolve().parents[3]
        / "packages"
        / "contracts"
        / "generated"
        / "json-schema"
        / "application-state.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema, format_checker=FormatChecker())
