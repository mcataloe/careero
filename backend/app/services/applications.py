from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, FormatChecker
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.constants import (
    ApplicationInterviewStatus,
    ApplicationWorkflowState,
    RoleStatus,
)
from app.models import (
    ActivityLog,
    Application,
    ApplicationExternalLink,
    ApplicationInterviewStage,
    ApplicationNote,
    ApplicationReminder,
    ApplicationStateHistory,
    GeneratedArtifact,
    Role,
    CompassEvaluation,
    User,
    Workspace,
)
from app.schemas.applications import (
    ApplicationExternalLinkCreate,
    ApplicationExternalLinkUpdate,
    ApplicationInterviewCancelRequest,
    ApplicationInterviewCompleteRequest,
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
from app.services.application_state_machine import (
    can_transition,
    get_available_transitions,
)
from app.services.workspace_context import is_workspace_active_for_new_work


CONTRACT_VERSION = "careero.contracts.v1"

_TIMELINE_APPLICATION_ACTIVITY = {
    "application.updated",
    "application.note.updated",
    "application.note.deleted",
    "application.reminder.updated",
    "application.interview_stage.updated",
    "application.interview_stage.canceled",
    "application.interview_stage.deleted",
    "application.external_link.updated",
    "application.external_link.deleted",
}

_TIMELINE_ROLE_ACTIVITY = {
    "role.created",
    "role.updated",
    "role.archived",
}


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


class ApplicationWorkflowTransitionError(ApplicationWorkflowError):
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

    def get_pipeline(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
        include_inactive: bool = False,
    ) -> dict[str, Any]:
        items = self.list_applications(
            workspace_id=workspace_id,
            include_inactive=include_inactive,
        )
        states = {
            state.value: []
            for state in _pipeline_states(include_inactive=include_inactive)
        }
        for item in items:
            current_state = item["current_state"]
            states.setdefault(current_state, []).append(item)
        return {
            "workspace_id": workspace_id,
            "include_inactive": include_inactive,
            "states": states,
        }

    def get_application(self, application_id: uuid.UUID) -> dict[str, Any]:
        application = self._get_application(application_id)
        if application is None:
            raise ApplicationWorkflowNotFoundError("Application workflow not found")
        return self.detail(application)

    def get_timeline(self, application_id: uuid.UUID) -> list[dict[str, Any]]:
        application = self._require_application(application_id)
        events: list[dict[str, Any]] = [
            _timeline_event(
                application=application,
                event_id=f"application-created-{application.id}",
                event_type="application.created",
                title="Application tracked",
                description=f"Started tracking {application.role.title}.",
                occurred_at=application.created_at,
                actor="system",
                source_type="application",
                source_id=str(application.id),
                metadata={"state": application.current_state},
            )
        ]

        for history in application.state_history:
            event_type = _state_history_event_type(history)
            events.append(
                _timeline_event(
                    application=application,
                    event_id=f"state-history-{history.id}",
                    event_type=event_type,
                    title=_state_history_title(history),
                    description=history.reason,
                    occurred_at=history.changed_at,
                    actor=history.changed_by,
                    source_type="application_state_history",
                    source_id=str(history.id),
                    metadata={
                        "from_state": history.from_state,
                        "to_state": history.to_state,
                        **(history.history_metadata or {}),
                    },
                )
            )

        for note in _active_notes(application):
            events.append(
                _timeline_event(
                    application=application,
                    event_id=f"note-created-{note.id}",
                    event_type="note.created",
                    title="Note added",
                    description=_truncate(note.body),
                    occurred_at=note.created_at,
                    actor=note.author or "user",
                    source_type="application_note",
                    source_id=str(note.id),
                    metadata={},
                )
            )

        for link in _active_external_links(application):
            events.append(
                _timeline_event(
                    application=application,
                    event_id=f"external-link-created-{link.id}",
                    event_type="external_link.created",
                    title=f"External link added: {link.label}",
                    description=link.url,
                    occurred_at=link.created_at,
                    actor="user",
                    source_type="application_external_link",
                    source_id=str(link.id),
                    metadata={"link_type": link.link_type},
                )
            )

        for reminder in application.reminders:
            events.append(
                _timeline_event(
                    application=application,
                    event_id=f"reminder-created-{reminder.id}",
                    event_type="reminder.created",
                    title=f"Reminder added: {reminder.title}",
                    description=reminder.notes,
                    occurred_at=reminder.created_at,
                    actor="user",
                    source_type="application_reminder",
                    source_id=str(reminder.id),
                    metadata={"due_at": _isoformat(reminder.due_at)},
                )
            )
            if reminder.completed_at is not None:
                events.append(
                    _timeline_event(
                        application=application,
                        event_id=f"reminder-completed-{reminder.id}",
                        event_type="reminder.completed",
                        title=f"Reminder completed: {reminder.title}",
                        description=None,
                        occurred_at=reminder.completed_at,
                        actor="user",
                        source_type="application_reminder",
                        source_id=str(reminder.id),
                        metadata={"due_at": _isoformat(reminder.due_at)},
                    )
                )

        for stage in _active_interview_stages(application):
            events.append(
                _timeline_event(
                    application=application,
                    event_id=f"interview-created-{stage.id}",
                    event_type="interview.created",
                    title=f"Interview stage added: {stage.title}",
                    description=stage.notes,
                    occurred_at=stage.created_at,
                    actor="user",
                    source_type="application_interview_stage",
                    source_id=str(stage.id),
                    metadata={
                        "stage_type": stage.stage_type,
                        "status": stage.status,
                        "scheduled_at": _isoformat(stage.scheduled_at),
                    },
                )
            )
            if stage.completed_at is not None:
                events.append(
                    _timeline_event(
                        application=application,
                        event_id=f"interview-completed-{stage.id}",
                        event_type="interview.completed",
                        title=f"Interview stage completed: {stage.title}",
                        description=None,
                        occurred_at=stage.completed_at,
                        actor="user",
                        source_type="application_interview_stage",
                        source_id=str(stage.id),
                        metadata={"stage_type": stage.stage_type, "status": stage.status},
                    )
                )

        events.extend(self._timeline_evaluations(application))
        events.extend(self._timeline_artifacts(application))
        events.extend(self._timeline_activity(application))
        events.sort(key=lambda event: (event["occurred_at"], event["id"]), reverse=True)
        return events

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
        if not can_transition(
            previous_state,
            next_state,
            reactivate=payload.reactivate,
        ):
            raise ApplicationWorkflowTransitionError(
                f"Invalid application state transition from "
                f"'{previous_state}' to '{next_state}'"
            )

        now = datetime.now(timezone.utc)
        application.current_state = next_state
        application.status = next_state
        if next_state == ApplicationWorkflowState.ARCHIVED.value:
            application.archived_at = now
        elif (
            previous_state == ApplicationWorkflowState.ARCHIVED.value
            and payload.reactivate
        ):
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
                "changed_by": payload.changed_by,
                "reason": payload.reason,
                "reactivate": payload.reactivate,
            },
        )
        self.db.commit()
        return self.get_application(application.id)

    def summary(self, application: Application) -> dict[str, Any]:
        role = application.role
        company = role.company
        latest_compass = self._latest_compass_summary(application)
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
            "available_next_states": get_available_transitions(
                application.current_state,
                include_reactivation=True,
            ),
            "compass": latest_compass,
            "resume_artifact": self._latest_artifact_summary(
                application,
                artifact_type="tailored_resume",
            ),
            "cover_letter_artifact": self._latest_artifact_summary(
                application,
                artifact_type="cover_letter",
            ),
            "counts": {
                "notes": len(_active_notes(application)),
                "reminders": len(application.reminders),
                "interviews": len(_active_interview_stages(application)),
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
            note_type=payload.note_type,
            body=payload.body,
        )
        self.db.add(note)
        self.db.flush()
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.note.created",
            details={"note_id": str(note.id), "note_type": note.note_type},
        )
        self.db.commit()
        return _note_response(note)

    def list_notes(self, application_id: uuid.UUID) -> list[dict[str, Any]]:
        application = self._require_application(application_id)
        notes = self.db.scalars(
            select(ApplicationNote)
            .where(
                ApplicationNote.application_id == application.id,
                ApplicationNote.deleted_at.is_(None),
            )
            .order_by(ApplicationNote.created_at.desc(), ApplicationNote.id.desc())
        )
        return [_note_response(note) for note in notes]

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
        if "note_type" in updates and updates["note_type"] is not None:
            note.note_type = updates["note_type"]
        if "body" in updates:
            note.body = updates["body"]
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.note.updated",
            details={"note_id": str(note.id), "note_type": note.note_type},
        )
        self.db.commit()
        return _note_response(note)

    def delete_note(self, application_id: uuid.UUID, note_id: uuid.UUID) -> None:
        application = self._require_application(application_id)
        note = self._require_child(ApplicationNote, application, note_id)
        note.deleted_at = datetime.now(timezone.utc)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.note.deleted",
            details={"note_id": str(note.id), "note_type": note.note_type},
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

    def list_interview_stages(
        self,
        application_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        application = self._require_application(application_id)
        stages = self.db.scalars(
            select(ApplicationInterviewStage).where(
                ApplicationInterviewStage.application_id == application.id,
                ApplicationInterviewStage.deleted_at.is_(None),
            )
        )
        return [_interview_stage_response(stage, application) for stage in _sort_interview_stages(stages)]

    def create_interview_stage(
        self,
        application_id: uuid.UUID,
        payload: ApplicationInterviewStageCreate,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        status_value = (payload.status or _default_interview_status(payload.scheduled_at, payload.completed_at)).value
        _validate_interview_status(status_value)
        completed_at = payload.completed_at
        if status_value == ApplicationInterviewStatus.COMPLETED.value and completed_at is None:
            completed_at = datetime.now(timezone.utc)
        stage = ApplicationInterviewStage(
            application_id=application.id,
            user_id=application.user_id,
            workspace_id=application.workspace_id,
            stage_type=payload.stage_type.value,
            title=payload.title,
            scheduled_at=payload.scheduled_at,
            completed_at=completed_at,
            status=status_value,
            interviewer_names=_clean_names(payload.interviewer_names),
            location_or_meeting_link=payload.location_or_meeting_link,
            notes=payload.notes,
            preparation_notes=payload.preparation_notes,
            outcome_notes=payload.outcome_notes,
            stage_metadata=payload.metadata,
        )
        self.db.add(stage)
        self.db.flush()
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.interview_stage.created",
            details={
                "stage_id": str(stage.id),
                "stage_type": stage.stage_type,
                "status": stage.status,
                "state_transition_suggestion": _interview_state_suggestion(application),
            },
        )
        self.db.commit()
        return _interview_stage_response(stage, application)

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
        if "stage_type" in updates and updates["stage_type"] is not None:
            updates["stage_type"] = updates["stage_type"].value
        if "status" in updates and updates["status"] is not None:
            updates["status"] = updates["status"].value
            _validate_interview_status(updates["status"])
        if "interviewer_names" in updates and updates["interviewer_names"] is not None:
            updates["interviewer_names"] = _clean_names(updates["interviewer_names"])
        for field_name, value in updates.items():
            setattr(stage, field_name, value)
        if stage.status == ApplicationInterviewStatus.COMPLETED.value and stage.completed_at is None:
            stage.completed_at = datetime.now(timezone.utc)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.interview_stage.updated",
            details={"stage_id": str(stage.id), "stage_type": stage.stage_type, "status": stage.status},
        )
        self.db.commit()
        return _interview_stage_response(stage, application)

    def complete_interview_stage(
        self,
        application_id: uuid.UUID,
        stage_id: uuid.UUID,
        payload: ApplicationInterviewCompleteRequest | None = None,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        stage = self._require_child(ApplicationInterviewStage, application, stage_id)
        payload = payload or ApplicationInterviewCompleteRequest()
        if payload.status not in {ApplicationInterviewStatus.COMPLETED, ApplicationInterviewStatus.NO_SHOW}:
            raise ApplicationWorkflowValidationError("Complete status must be completed or no_show")
        stage.status = payload.status.value
        stage.completed_at = payload.completed_at or datetime.now(timezone.utc)
        if payload.outcome_notes is not None:
            stage.outcome_notes = payload.outcome_notes
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.interview_stage.completed",
            details={"stage_id": str(stage.id), "stage_type": stage.stage_type, "status": stage.status},
        )
        self.db.commit()
        return _interview_stage_response(stage, application)

    def cancel_interview_stage(
        self,
        application_id: uuid.UUID,
        stage_id: uuid.UUID,
        payload: ApplicationInterviewCancelRequest | None = None,
    ) -> dict[str, Any]:
        application = self._require_application(application_id)
        stage = self._require_child(ApplicationInterviewStage, application, stage_id)
        payload = payload or ApplicationInterviewCancelRequest()
        if payload.status not in {ApplicationInterviewStatus.CANCELED, ApplicationInterviewStatus.NO_SHOW}:
            raise ApplicationWorkflowValidationError("Cancel status must be canceled or no_show")
        stage.status = payload.status.value
        if payload.outcome_notes is not None:
            stage.outcome_notes = payload.outcome_notes
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.interview_stage.canceled",
            details={"stage_id": str(stage.id), "stage_type": stage.stage_type, "status": stage.status},
        )
        self.db.commit()
        return _interview_stage_response(stage, application)

    def delete_interview_stage(self, application_id: uuid.UUID, stage_id: uuid.UUID) -> None:
        application = self._require_application(application_id)
        stage = self._require_child(ApplicationInterviewStage, application, stage_id)
        stage.deleted_at = datetime.now(timezone.utc)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.interview_stage.deleted",
            details={"stage_id": str(stage.id), "stage_type": stage.stage_type, "status": stage.status},
        )
        self.db.commit()

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
            link_metadata=payload.metadata or {},
        )
        self.db.add(link)
        self.db.flush()
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.external_link.created",
            details={"link_id": str(link.id), "link_type": link.link_type},
        )
        self.db.commit()
        return _external_link_response(link)

    def list_external_links(self, application_id: uuid.UUID) -> list[dict[str, Any]]:
        application = self._require_application(application_id)
        links = self.db.scalars(
            select(ApplicationExternalLink)
            .where(
                ApplicationExternalLink.application_id == application.id,
                ApplicationExternalLink.deleted_at.is_(None),
            )
            .order_by(
                ApplicationExternalLink.created_at.desc(),
                ApplicationExternalLink.id.desc(),
            )
        )
        return [_external_link_response(link) for link in links]

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
            details={"link_id": str(link.id), "link_type": link.link_type},
        )
        self.db.commit()
        return _external_link_response(link)

    def delete_external_link(self, application_id: uuid.UUID, link_id: uuid.UUID) -> None:
        application = self._require_application(application_id)
        link = self._require_child(ApplicationExternalLink, application, link_id)
        link.deleted_at = datetime.now(timezone.utc)
        self._log_activity(
            user_id=application.user_id,
            application=application,
            action="application.external_link.deleted",
            details={"link_id": str(link.id), "link_type": link.link_type},
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
                for note in _active_notes(application)
            ],
            "interviewStages": [
                {
                    "id": str(stage.id),
                    "stageType": stage.stage_type,
                    "title": stage.title,
                    "scheduledAt": _isoformat(stage.scheduled_at),
                    "completedAt": _isoformat(stage.completed_at),
                    "status": stage.status,
                    "interviewerNames": stage.interviewer_names or [],
                    "locationOrMeetingLink": stage.location_or_meeting_link,
                    "notes": stage.notes,
                    "preparationNotes": stage.preparation_notes,
                    "outcomeNotes": stage.outcome_notes,
                    "metadata": stage.stage_metadata or {},
                }
                for stage in _active_interview_stages(application)
            ],
            "externalLinks": [
                {
                    "label": link.label,
                    "url": link.url,
                    "type": link.link_type,
                }
                for link in _active_external_links(application)
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
        if (
            child is None
            or child.application_id != application.id
            or getattr(child, "deleted_at", None) is not None
        ):
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

    def _timeline_evaluations(self, application: Application) -> list[dict[str, Any]]:
        evaluations = self.db.scalars(
            select(CompassEvaluation)
            .where(
                CompassEvaluation.user_id == application.user_id,
                CompassEvaluation.workspace_id == application.workspace_id,
                CompassEvaluation.role_id == application.role_id,
                CompassEvaluation.deleted_at.is_(None),
                CompassEvaluation.evaluation_status == "completed",
            )
            .order_by(CompassEvaluation.updated_at.desc(), CompassEvaluation.id.desc())
        )
        return [
            _timeline_event(
                application=application,
                event_id=f"compass-completed-{evaluation.id}",
                event_type="compass.completed",
                title="COMPASS evaluation completed",
                description=evaluation.summary,
                occurred_at=evaluation.updated_at,
                actor="ai" if evaluation.ai_enabled else "system",
                source_type="compass_evaluation",
                source_id=str(evaluation.id),
                metadata={
                    "recommendation": evaluation.recommendation,
                    "overall_score": (
                        str(evaluation.overall_score)
                        if evaluation.overall_score is not None
                        else None
                    ),
                    "confidence_level": evaluation.confidence_level,
                },
            )
            for evaluation in evaluations
        ]

    def _timeline_artifacts(self, application: Application) -> list[dict[str, Any]]:
        artifacts = self.db.scalars(
            select(GeneratedArtifact)
            .where(
                GeneratedArtifact.user_id == application.user_id,
                GeneratedArtifact.workspace_id == application.workspace_id,
                GeneratedArtifact.role_id == application.role_id,
                GeneratedArtifact.deleted_at.is_(None),
                GeneratedArtifact.artifact_type.in_(
                    ["tailored_resume", "cover_letter"]
                ),
            )
            .order_by(GeneratedArtifact.created_at.desc(), GeneratedArtifact.id.desc())
        )
        events: list[dict[str, Any]] = []
        for artifact in artifacts:
            if artifact.artifact_type == "tailored_resume":
                event_type = "artifact.resume.created"
                title = "Resume artifact generated"
            else:
                event_type = "artifact.cover_letter.created"
                title = "Cover letter artifact generated"
            contract = (
                artifact.artifact_metadata.get("contract")
                if artifact.artifact_metadata
                else None
            )
            revision = contract.get("revision", {}) if isinstance(contract, dict) else {}
            events.append(
                _timeline_event(
                    application=application,
                    event_id=f"{event_type}-{artifact.id}",
                    event_type=event_type,
                    title=title,
                    description=artifact.title,
                    occurred_at=artifact.created_at,
                    actor="ai",
                    source_type="generated_artifact",
                    source_id=str(artifact.id),
                    metadata={
                        "artifact_type": artifact.artifact_type,
                        "revision_number": revision.get("revisionNumber"),
                    },
                )
            )
        return events

    def _timeline_activity(self, application: Application) -> list[dict[str, Any]]:
        logs = self.db.scalars(
            select(ActivityLog)
            .where(
                ActivityLog.user_id == application.user_id,
                or_(
                    and_(
                        ActivityLog.entity_type == "application",
                        ActivityLog.entity_id == application.id,
                        ActivityLog.action.in_(_TIMELINE_APPLICATION_ACTIVITY),
                    ),
                    and_(
                        ActivityLog.entity_type == "role",
                        ActivityLog.entity_id == application.role_id,
                        ActivityLog.action.in_(_TIMELINE_ROLE_ACTIVITY),
                    ),
                ),
            )
            .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
        )
        return [
            _timeline_event(
                application=application,
                event_id=f"activity-{log.id}",
                event_type=_activity_event_type(log),
                title=_activity_title(log),
                description=None,
                occurred_at=log.created_at,
                actor=_activity_actor(log),
                source_type="activity_log",
                source_id=str(log.id),
                metadata=_safe_activity_metadata(log),
            )
            for log in logs
        ]

    def _latest_compass_summary(self, application: Application) -> dict[str, Any] | None:
        evaluation = self.db.scalar(
            select(CompassEvaluation)
            .where(
                CompassEvaluation.user_id == application.user_id,
                CompassEvaluation.workspace_id == application.workspace_id,
                CompassEvaluation.role_id == application.role_id,
                CompassEvaluation.deleted_at.is_(None),
            )
            .order_by(CompassEvaluation.created_at.desc(), CompassEvaluation.id.desc())
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


def _pipeline_states(*, include_inactive: bool) -> tuple[ApplicationWorkflowState, ...]:
    states = tuple(ApplicationWorkflowState)
    if include_inactive:
        return states
    return tuple(
        state for state in states if state != ApplicationWorkflowState.ARCHIVED
    )


def _active_notes(application: Application) -> list[ApplicationNote]:
    return [note for note in application.note_entries if note.deleted_at is None]


def _active_external_links(application: Application) -> list[ApplicationExternalLink]:
    return [link for link in application.external_links if link.deleted_at is None]


def _active_interview_stages(application: Application) -> list[ApplicationInterviewStage]:
    return [stage for stage in application.interview_stages if stage.deleted_at is None]


def _default_interview_status(
    scheduled_at: datetime | None,
    completed_at: datetime | None,
) -> ApplicationInterviewStatus:
    if completed_at is not None:
        return ApplicationInterviewStatus.COMPLETED
    if scheduled_at is not None:
        return ApplicationInterviewStatus.SCHEDULED
    return ApplicationInterviewStatus.PLANNED


def _validate_interview_status(status: str) -> None:
    if status not in {item.value for item in ApplicationInterviewStatus}:
        raise ApplicationWorkflowValidationError(f"Invalid interview status: {status}")


def _clean_names(names: list[str]) -> list[str]:
    return [name.strip() for name in names if name.strip()]


def _interview_state_suggestion(application: Application) -> str | None:
    if application.current_state != ApplicationWorkflowState.INTERVIEWING.value and can_transition(
        application.current_state,
        ApplicationWorkflowState.INTERVIEWING,
    ):
        return ApplicationWorkflowState.INTERVIEWING.value
    return None


def _sort_interview_stages(stages) -> list[ApplicationInterviewStage]:
    active_statuses = {
        ApplicationInterviewStatus.PLANNED.value,
        ApplicationInterviewStatus.SCHEDULED.value,
    }
    active = [stage for stage in stages if stage.status in active_statuses]
    inactive = [stage for stage in stages if stage.status not in active_statuses]
    distant_future = datetime.max.replace(tzinfo=timezone.utc)
    distant_past = datetime.min.replace(tzinfo=timezone.utc)
    active.sort(key=lambda stage: (stage.scheduled_at or distant_future, stage.created_at, stage.id))
    inactive.sort(
        key=lambda stage: (stage.completed_at or stage.scheduled_at or stage.updated_at or distant_past, stage.id),
        reverse=True,
    )
    return [*active, *inactive]


def _interview_stage_response(
    stage: ApplicationInterviewStage,
    application: Application,
) -> dict[str, Any]:
    return {
        "id": stage.id,
        "application_id": stage.application_id,
        "workspace_id": stage.workspace_id,
        "stage_type": stage.stage_type,
        "title": stage.title,
        "scheduled_at": stage.scheduled_at,
        "completed_at": stage.completed_at,
        "status": stage.status,
        "interviewer_names": stage.interviewer_names or [],
        "location_or_meeting_link": stage.location_or_meeting_link,
        "notes": stage.notes,
        "preparation_notes": stage.preparation_notes,
        "outcome_notes": stage.outcome_notes,
        "metadata": stage.stage_metadata or {},
        "state_transition_suggestion": _interview_state_suggestion(application),
        "created_at": stage.created_at,
        "updated_at": stage.updated_at,
    }


def _note_response(note: ApplicationNote) -> dict[str, Any]:
    return {
        "id": note.id,
        "application_id": note.application_id,
        "workspace_id": note.workspace_id,
        "author": note.author,
        "note_type": note.note_type,
        "body": note.body,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }


def _external_link_response(link: ApplicationExternalLink) -> dict[str, Any]:
    return {
        "id": link.id,
        "application_id": link.application_id,
        "workspace_id": link.workspace_id,
        "label": link.label,
        "url": link.url,
        "type": link.link_type,
        "metadata": link.link_metadata or {},
        "created_at": link.created_at,
        "updated_at": link.updated_at,
    }


def _timeline_event(
    *,
    application: Application,
    event_id: str,
    event_type: str,
    title: str,
    description: str | None,
    occurred_at: datetime,
    actor: str,
    source_type: str,
    source_id: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": event_id,
        "application_id": application.id,
        "event_type": event_type,
        "title": title,
        "description": description,
        "occurred_at": occurred_at,
        "actor": actor,
        "source_type": source_type,
        "source_id": source_id,
        "metadata": {key: value for key, value in metadata.items() if value is not None},
    }


def _state_history_event_type(history: ApplicationStateHistory) -> str:
    if history.to_state == ApplicationWorkflowState.ARCHIVED.value:
        return "application.archived"
    if history.from_state == ApplicationWorkflowState.ARCHIVED.value:
        return "application.reactivated"
    return "application.state_changed"


def _state_history_title(history: ApplicationStateHistory) -> str:
    if history.from_state is None:
        return f"Initial state: {history.to_state}"
    if history.to_state == ApplicationWorkflowState.ARCHIVED.value:
        return "Application archived"
    if history.from_state == ApplicationWorkflowState.ARCHIVED.value:
        return f"Application reactivated to {history.to_state}"
    return f"State changed to {history.to_state}"


def _activity_event_type(log: ActivityLog) -> str:
    mapping = {
        "application.note.updated": "note.updated",
        "application.note.deleted": "note.deleted",
        "application.reminder.updated": "reminder.updated",
        "application.interview_stage.updated": "interview.updated",
        "application.interview_stage.canceled": "interview.canceled",
        "application.interview_stage.deleted": "interview.deleted",
        "application.external_link.created": "external_link.created",
        "application.external_link.updated": "external_link.updated",
        "application.external_link.deleted": "external_link.deleted",
    }
    return mapping.get(log.action, log.action)


def _activity_title(log: ActivityLog) -> str:
    titles = {
        "application.updated": "Application details updated",
        "application.note.updated": "Note updated",
        "application.note.deleted": "Note deleted",
        "application.reminder.updated": "Reminder updated",
        "application.interview_stage.updated": "Interview stage updated",
        "application.interview_stage.canceled": "Interview stage canceled",
        "application.interview_stage.deleted": "Interview stage deleted",
        "application.external_link.created": "External link added",
        "application.external_link.updated": "External link updated",
        "application.external_link.deleted": "External link deleted",
        "role.created": "Role captured",
        "role.updated": "Role updated",
        "role.archived": "Role archived",
    }
    return titles.get(log.action, log.action.replace(".", " "))


def _activity_actor(log: ActivityLog) -> str:
    changed_by = log.details.get("changed_by") if log.details else None
    return str(changed_by) if changed_by else "user"


def _safe_activity_metadata(log: ActivityLog) -> dict[str, Any]:
    if not log.details:
        return {"action": log.action}
    allowed_keys = {
        "action",
        "changed_fields",
        "from_state",
        "to_state",
        "reactivate",
        "role_id",
        "workspace_id",
        "note_id",
        "note_type",
        "reminder_id",
        "stage_id",
        "stage_type",
        "status",
        "state_transition_suggestion",
        "link_id",
        "link_type",
    }
    metadata = {
        key: value
        for key, value in log.details.items()
        if key in allowed_keys and isinstance(value, (str, int, float, bool, list, type(None)))
    }
    metadata["action"] = log.action
    return metadata


def _truncate(value: str, limit: int = 240) -> str:
    if len(value) <= limit:
        return value
    return f"{value[: limit - 3].rstrip()}..."


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
