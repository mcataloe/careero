from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.constants import (
    ApplicationWorkflowState,
    AutomationActionType,
    AutomationApprovalStatus,
    AutomationExecutionStatus,
    AutomationSuggestionStatus,
    AutomationTargetType,
)
from app.models import (
    ActivityLog,
    Application,
    ApplicationInterviewStage,
    AutomationApprovalLog,
    AutomationSuggestion,
    GeneratedArtifact,
    Role,
    User,
    Workspace,
)
from app.schemas.automation import AutomationPreferencesUpdate
from app.services.activity_log import ActivityLogService
from app.services.artifact_lifecycle import normalize_artifact_lifecycle_status
from app.services.current_user import CurrentUserResolutionError, resolve_current_user


POLICY_VERSION = "automation_policy_v1"

DEFAULT_SUGGESTION_CATEGORIES = [
    AutomationActionType.FOLLOW_UP_SUGGESTION.value,
    AutomationActionType.REMINDER_SUGGESTION.value,
    AutomationActionType.ARTIFACT_READINESS_CHECK.value,
    AutomationActionType.COMMUNICATION_DRAFT.value,
    AutomationActionType.WORKFLOW_STATE_SUGGESTION.value,
    AutomationActionType.OPPORTUNITY_REVIEW_SUGGESTION.value,
    AutomationActionType.FUTURE_EXTERNAL_ACTION_DISABLED.value,
]

TERMINAL_APPLICATION_STATES = {
    ApplicationWorkflowState.INTERVIEWING.value,
    ApplicationWorkflowState.OFFER.value,
    ApplicationWorkflowState.REJECTED.value,
    ApplicationWorkflowState.WITHDRAWN.value,
    ApplicationWorkflowState.ARCHIVED.value,
}


class AutomationError(Exception):
    pass


class AutomationSeedMissingError(AutomationError):
    pass


class AutomationNotFoundError(AutomationError):
    pass


class AutomationWorkspaceNotFoundError(AutomationError):
    pass


class AutomationValidationError(AutomationError):
    pass


class AutomationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.activity_log = ActivityLogService(db)

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise AutomationSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def list_suggestions(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
        target_type: str | None = None,
        target_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        self._generate_suggestions(user=user, workspace_id=workspace_id)
        filters = [AutomationSuggestion.user_id == user.id]
        if workspace_id is not None:
            workspace = self._workspace_for_user(workspace_id, user.id)
            if workspace is None:
                raise AutomationWorkspaceNotFoundError("Workspace not found")
            filters.append(AutomationSuggestion.workspace_id == workspace.id)
        if target_type is not None:
            filters.append(AutomationSuggestion.target_type == target_type)
        if target_id is not None:
            filters.append(AutomationSuggestion.target_id == target_id)

        statement = (
            select(AutomationSuggestion)
            .where(*filters)
            .order_by(
                AutomationSuggestion.status.asc(),
                AutomationSuggestion.created_at.desc(),
                AutomationSuggestion.id.desc(),
            )
        )
        return {
            "workspace_id": workspace_id,
            "target_type": target_type,
            "target_id": target_id,
            "suggestions": [
                _suggestion_response(suggestion)
                for suggestion in self.db.scalars(statement)
            ],
            "external_actions_enabled": False,
        }

    def approve_suggestion(
        self,
        suggestion_id: uuid.UUID,
        *,
        actor: str = "user",
    ) -> dict[str, Any]:
        return self._record_decision(
            suggestion_id,
            approval_status=AutomationApprovalStatus.APPROVED.value,
            suggestion_status=AutomationSuggestionStatus.APPROVED.value,
            reason=None,
            actor=actor,
        )

    def reject_suggestion(
        self,
        suggestion_id: uuid.UUID,
        *,
        reason: str | None,
        actor: str = "user",
    ) -> dict[str, Any]:
        return self._record_decision(
            suggestion_id,
            approval_status=AutomationApprovalStatus.REJECTED.value,
            suggestion_status=AutomationSuggestionStatus.REJECTED.value,
            reason=reason,
            actor=actor,
        )

    def dismiss_suggestion(
        self,
        suggestion_id: uuid.UUID,
        *,
        reason: str | None,
        actor: str = "user",
    ) -> dict[str, Any]:
        return self._record_decision(
            suggestion_id,
            approval_status=AutomationApprovalStatus.DISMISSED.value,
            suggestion_status=AutomationSuggestionStatus.DISMISSED.value,
            reason=reason,
            actor=actor,
        )

    def list_approval_logs(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        filters = [AutomationApprovalLog.user_id == user.id]
        if workspace_id is not None:
            workspace = self._workspace_for_user(workspace_id, user.id)
            if workspace is None:
                raise AutomationWorkspaceNotFoundError("Workspace not found")
            filters.append(AutomationApprovalLog.workspace_id == workspace.id)
        statement = (
            select(AutomationApprovalLog)
            .where(*filters)
            .order_by(
                AutomationApprovalLog.created_at.desc(),
                AutomationApprovalLog.id.desc(),
            )
        )
        return {
            "workspace_id": workspace_id,
            "logs": [_approval_log_response(log) for log in self.db.scalars(statement)],
        }

    def get_preferences(self, workspace_id: uuid.UUID) -> dict[str, Any]:
        user = self.get_default_user()
        workspace = self._workspace_for_user(workspace_id, user.id)
        if workspace is None:
            raise AutomationWorkspaceNotFoundError("Workspace not found")
        return _preferences_response(workspace)

    def update_preferences(
        self,
        workspace_id: uuid.UUID,
        payload: AutomationPreferencesUpdate,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        workspace = self._workspace_for_user(workspace_id, user.id)
        if workspace is None:
            raise AutomationWorkspaceNotFoundError("Workspace not found")
        updates = payload.model_dump(exclude_unset=True)
        if updates.get("future_external_actions_enabled") is True:
            raise AutomationValidationError(
                "External automation actions are disabled in the Layer 9 MVP"
            )
        preferences = dict(workspace.preferences or {})
        automation = _automation_preferences_dict(workspace)
        for key, value in updates.items():
            if value is not None:
                automation[key] = value
        automation["future_external_actions_enabled"] = False
        automation["policy_version"] = POLICY_VERSION
        preferences["automation"] = automation
        workspace.preferences = preferences
        self.activity_log.append(
            user_id=user.id,
            entity_type="workspace",
            entity_id=workspace.id,
            action="workspace.automation_preferences.updated",
            details={
                "workspace_id": str(workspace.id),
                "changed_fields": sorted(updates.keys()),
                "external_actions_enabled": False,
            },
        )
        self.db.commit()
        return _preferences_response(workspace)

    def _record_decision(
        self,
        suggestion_id: uuid.UUID,
        *,
        approval_status: str,
        suggestion_status: str,
        reason: str | None,
        actor: str,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        suggestion = self.db.get(AutomationSuggestion, suggestion_id)
        if suggestion is None or suggestion.user_id != user.id:
            raise AutomationNotFoundError("Automation suggestion not found")
        if suggestion.status != AutomationSuggestionStatus.ACTIVE.value:
            raise AutomationValidationError("Automation suggestion is no longer active")
        now = datetime.now(timezone.utc)
        suggestion.status = suggestion_status
        log = AutomationApprovalLog(
            user_id=user.id,
            workspace_id=suggestion.workspace_id,
            suggestion_id=suggestion.id,
            actor=actor,
            target_type=suggestion.target_type,
            target_id=suggestion.target_id,
            action_type=suggestion.action_type,
            preview=suggestion.preview,
            preview_hash=suggestion.preview_hash,
            approval_status=approval_status,
            dismissal_or_rejection_reason=reason,
            execution_status=AutomationExecutionStatus.NOT_APPLICABLE.value,
            execution_result={
                "message": "Layer 9 MVP records the decision without executing an external or workflow mutation."
            },
            external_mutation=False,
            policy_version=suggestion.policy_version,
            decided_at=now,
            executed_at=None,
        )
        self.db.add(log)
        self.db.flush()
        self.activity_log.append(
            user_id=user.id,
            entity_type="automation_suggestion",
            entity_id=suggestion.id,
            action=f"automation.{approval_status}",
            details={
                "workspace_id": str(suggestion.workspace_id),
                "target_type": suggestion.target_type,
                "target_id": str(suggestion.target_id),
                "action_type": suggestion.action_type,
                "external_mutation": False,
                "execution_status": log.execution_status,
            },
        )
        self.db.commit()
        return _approval_log_response(log)

    def _generate_suggestions(
        self,
        *,
        user: User,
        workspace_id: uuid.UUID | None,
    ) -> None:
        workspaces = self._workspaces(user_id=user.id, workspace_id=workspace_id)
        for workspace in workspaces:
            preferences = _automation_preferences_dict(workspace)
            if not preferences["enabled"]:
                continue
            self._generate_application_suggestions(user=user, workspace=workspace, preferences=preferences)
            self._generate_opportunity_suggestions(user=user, workspace=workspace, preferences=preferences)
            self._generate_artifact_suggestions(user=user, workspace=workspace, preferences=preferences)
        self.db.commit()

    def _generate_application_suggestions(
        self,
        *,
        user: User,
        workspace: Workspace,
        preferences: dict[str, Any],
    ) -> None:
        applications = self.db.scalars(
            select(Application)
            .where(
                Application.user_id == user.id,
                Application.workspace_id == workspace.id,
                Application.deleted_at.is_(None),
            )
            .options(
                joinedload(Application.role).joinedload(Role.company),
                selectinload(Application.interview_stages),
            )
        )
        now = datetime.now(timezone.utc)
        threshold_days = preferences["follow_up_suggestion_days"]
        for application in applications:
            if (
                AutomationActionType.FOLLOW_UP_SUGGESTION.value
                in preferences["suggestion_categories"]
                and _needs_follow_up(application, now, threshold_days)
            ):
                self._add_suggestion(
                    user=user,
                    workspace=workspace,
                    target_type=AutomationTargetType.APPLICATION.value,
                    target_id=application.id,
                    role_id=application.role_id,
                    application_id=application.id,
                    artifact_id=None,
                    action_type=AutomationActionType.FOLLOW_UP_SUGGESTION.value,
                    title="Review follow-up timing",
                    summary=f"{application.role.title} has been applied without a recorded response.",
                    reason="A follow-up may be useful if you still want to pursue this application.",
                    basis=f"Application applied date is older than {threshold_days} days and no interview or offer is recorded.",
                    confidence="Weak Signal",
                    source_inputs={
                        "applied_at": _isoformat(application.applied_at),
                        "threshold_days": threshold_days,
                        "current_state": application.current_state,
                    },
                    preview_body="Consider whether a short, professional follow-up is appropriate before taking any action.",
                )
                if (
                    preferences["communication_drafts_enabled"]
                    and AutomationActionType.COMMUNICATION_DRAFT.value
                    in preferences["suggestion_categories"]
                ):
                    self._add_suggestion(
                        user=user,
                        workspace=workspace,
                        target_type=AutomationTargetType.APPLICATION.value,
                        target_id=application.id,
                        role_id=application.role_id,
                        application_id=application.id,
                        artifact_id=None,
                        action_type=AutomationActionType.COMMUNICATION_DRAFT.value,
                        title="Prepare follow-up draft",
                        summary="A local-only follow-up draft can be reviewed before any external action.",
                        reason="Careero can prepare review text, but it cannot send email in this MVP.",
                        basis="Generated from stored application timing and opportunity metadata only.",
                        confidence="Draft Only",
                        source_inputs={
                            "company": application.role.company.name,
                            "title": application.role.title,
                            "external_mutation": False,
                        },
                        preview_body=(
                            f"Hi, I wanted to briefly follow up on my application for "
                            f"{application.role.title}. I remain interested and would "
                            "welcome any update when convenient."
                        ),
                    )
            if (
                preferences["internal_state_change_suggestions_enabled"]
                and AutomationActionType.WORKFLOW_STATE_SUGGESTION.value
                in preferences["suggestion_categories"]
                and application.current_state != ApplicationWorkflowState.INTERVIEWING.value
                and _has_active_interview(application)
            ):
                self._add_suggestion(
                    user=user,
                    workspace=workspace,
                    target_type=AutomationTargetType.APPLICATION.value,
                    target_id=application.id,
                    role_id=application.role_id,
                    application_id=application.id,
                    artifact_id=None,
                    action_type=AutomationActionType.WORKFLOW_STATE_SUGGESTION.value,
                    title="Review application state",
                    summary="This application has an active interview record while the workflow state is not interviewing.",
                    reason="The application state may need a user-approved update.",
                    basis="Structured interview stage exists; no state change has been made automatically.",
                    confidence="Moderate Confidence",
                    source_inputs={"suggested_state": ApplicationWorkflowState.INTERVIEWING.value},
                    preview_body="Review whether this application should move to interviewing.",
                )

    def _generate_opportunity_suggestions(
        self,
        *,
        user: User,
        workspace: Workspace,
        preferences: dict[str, Any],
    ) -> None:
        if AutomationActionType.OPPORTUNITY_REVIEW_SUGGESTION.value not in preferences["suggestion_categories"]:
            return
        roles = self.db.scalars(
            select(Role).where(
                Role.user_id == user.id,
                Role.workspace_id == workspace.id,
                Role.deleted_at.is_(None),
            )
        )
        for role in roles:
            intelligence = (role.parse_metadata or {}).get("opportunityIntelligence")
            categories = intelligence.get("categories", []) if isinstance(intelligence, dict) else []
            if "Duplicate / Overlap" in categories:
                title = "Review possible duplicate opportunity"
                reason = "Opportunity intelligence found duplicate or overlap signals."
            elif "Archive Candidate" in categories:
                title = "Review low-priority opportunity"
                reason = "Opportunity intelligence found several caution signals."
            else:
                continue
            self._add_suggestion(
                user=user,
                workspace=workspace,
                target_type=AutomationTargetType.OPPORTUNITY.value,
                target_id=role.id,
                role_id=role.id,
                application_id=None,
                artifact_id=None,
                action_type=AutomationActionType.OPPORTUNITY_REVIEW_SUGGESTION.value,
                title=title,
                summary=f"{role.title} may need a review decision.",
                reason=reason,
                basis="Deterministic opportunity intelligence categories are advisory only.",
                confidence="Moderate Confidence",
                source_inputs={"categories": categories},
                preview_body="Review this opportunity before archiving, deprioritizing, or keeping it active.",
            )

    def _generate_artifact_suggestions(
        self,
        *,
        user: User,
        workspace: Workspace,
        preferences: dict[str, Any],
    ) -> None:
        if (
            not preferences["artifact_readiness_checks_enabled"]
            or AutomationActionType.ARTIFACT_READINESS_CHECK.value
            not in preferences["suggestion_categories"]
        ):
            return
        artifacts = self.db.scalars(
            select(GeneratedArtifact).where(
                GeneratedArtifact.user_id == user.id,
                GeneratedArtifact.workspace_id == workspace.id,
                GeneratedArtifact.deleted_at.is_(None),
            )
        )
        for artifact in artifacts:
            metadata = artifact.artifact_metadata or {}
            contract = metadata.get("contract") if isinstance(metadata, dict) else None
            warnings = _artifact_warnings(contract)
            lifecycle = normalize_artifact_lifecycle_status(artifact.lifecycle_status)
            export_metadata = contract.get("exportMetadata", []) if isinstance(contract, dict) else []
            if warnings:
                summary = "This artifact has generation warnings that should be reviewed."
                preview = "Review generation warnings before using or exporting this artifact."
                confidence = "Moderate Confidence"
            elif lifecycle == "draft":
                summary = "This artifact is still a draft and should be reviewed before use."
                preview = "Review this draft before treating it as ready."
                confidence = "Draft Only"
            elif not export_metadata:
                summary = "This artifact has no recorded local export metadata."
                preview = "Consider exporting only after reviewing the stored artifact content."
                confidence = "Weak Signal"
            else:
                continue
            self._add_suggestion(
                user=user,
                workspace=workspace,
                target_type=AutomationTargetType.ARTIFACT.value,
                target_id=artifact.id,
                role_id=artifact.role_id,
                application_id=artifact.application_id,
                artifact_id=artifact.id,
                action_type=AutomationActionType.ARTIFACT_READINESS_CHECK.value,
                title="Review artifact readiness",
                summary=summary,
                reason="Artifact readiness checks do not mark artifacts reviewed, submitted, or archived.",
                basis="Stored artifact metadata and generation warnings only.",
                confidence=confidence,
                source_inputs={
                    "artifact_type": artifact.artifact_type,
                    "warnings": warnings,
                    "lifecycle_status": lifecycle,
                },
                preview_body=preview,
            )

    def _add_suggestion(
        self,
        *,
        user: User,
        workspace: Workspace,
        target_type: str,
        target_id: uuid.UUID,
        role_id: uuid.UUID | None,
        application_id: uuid.UUID | None,
        artifact_id: uuid.UUID | None,
        action_type: str,
        title: str,
        summary: str,
        reason: str,
        basis: str,
        confidence: str,
        source_inputs: dict[str, Any],
        preview_body: str,
    ) -> None:
        if self._existing_suggestion(
            user_id=user.id,
            target_type=target_type,
            target_id=target_id,
            action_type=action_type,
        ):
            return
        preview = {
            "title": title,
            "body": preview_body,
            "external_mutation": False,
        }
        preview_hash = _content_hash(preview)
        preview["content_hash"] = preview_hash
        self.db.add(
            AutomationSuggestion(
                user_id=user.id,
                workspace_id=workspace.id,
                target_type=target_type,
                target_id=target_id,
                role_id=role_id,
                application_id=application_id,
                artifact_id=artifact_id,
                action_type=action_type,
                title=title,
                summary=summary,
                reason=reason,
                basis=basis,
                confidence=confidence,
                source_inputs=source_inputs,
                preview=preview,
                preview_hash=preview_hash,
                status=AutomationSuggestionStatus.ACTIVE.value,
                policy_version=POLICY_VERSION,
                suggestion_metadata={"generated_by": "deterministic_policy"},
            )
        )

    def _existing_suggestion(
        self,
        *,
        user_id: uuid.UUID,
        target_type: str,
        target_id: uuid.UUID,
        action_type: str,
    ) -> bool:
        return (
            self.db.scalar(
                select(AutomationSuggestion.id)
                .where(
                    AutomationSuggestion.user_id == user_id,
                    AutomationSuggestion.target_type == target_type,
                    AutomationSuggestion.target_id == target_id,
                    AutomationSuggestion.action_type == action_type,
                    AutomationSuggestion.status.in_(
                        [
                            AutomationSuggestionStatus.ACTIVE.value,
                            AutomationSuggestionStatus.DISMISSED.value,
                            AutomationSuggestionStatus.REJECTED.value,
                            AutomationSuggestionStatus.APPROVED.value,
                        ]
                    ),
                )
                .limit(1)
            )
            is not None
        )

    def _workspaces(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> list[Workspace]:
        filters = [Workspace.user_id == user_id]
        if workspace_id is not None:
            filters.append(Workspace.id == workspace_id)
        return list(self.db.scalars(select(Workspace).where(*filters)))

    def _workspace_for_user(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Workspace | None:
        return self.db.scalar(
            select(Workspace).where(Workspace.id == workspace_id, Workspace.user_id == user_id)
        )


def _automation_preferences_dict(workspace: Workspace) -> dict[str, Any]:
    stored = {}
    if isinstance(workspace.preferences, dict):
        stored = workspace.preferences.get("automation") or {}
    return {
        "enabled": stored.get("enabled", True),
        "suggestion_categories": stored.get(
            "suggestion_categories",
            DEFAULT_SUGGESTION_CATEGORIES,
        ),
        "follow_up_suggestion_days": stored.get("follow_up_suggestion_days", 7),
        "artifact_readiness_checks_enabled": stored.get("artifact_readiness_checks_enabled", True),
        "communication_drafts_enabled": stored.get("communication_drafts_enabled", True),
        "internal_state_change_suggestions_enabled": stored.get(
            "internal_state_change_suggestions_enabled",
            True,
        ),
        "future_external_actions_enabled": False,
        "quiet_mode": stored.get("quiet_mode", False),
        "policy_version": stored.get("policy_version", POLICY_VERSION),
        "metadata": stored.get("metadata", {}),
    }


def _preferences_response(workspace: Workspace) -> dict[str, Any]:
    preferences = _automation_preferences_dict(workspace)
    return {
        "id": workspace.id,
        "workspace_id": workspace.id,
        **preferences,
        "created_at": workspace.created_at,
        "updated_at": workspace.updated_at,
    }


def _needs_follow_up(
    application: Application,
    now: datetime,
    threshold_days: int,
) -> bool:
    if application.applied_at is None:
        return False
    if application.current_state in TERMINAL_APPLICATION_STATES:
        return False
    return application.applied_at < now - timedelta(days=threshold_days)


def _has_active_interview(application: Application) -> bool:
    return any(
        stage.deleted_at is None and stage.status in {"planned", "scheduled"}
        for stage in application.interview_stages
    )


def _artifact_warnings(contract: Any) -> list[str]:
    if not isinstance(contract, dict):
        return []
    generation = contract.get("generationMetadata")
    if not isinstance(generation, dict):
        return []
    warnings = generation.get("warnings") or []
    return [str(warning) for warning in warnings if str(warning).strip()]


def _content_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, default=str).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _suggestion_response(suggestion: AutomationSuggestion) -> dict[str, Any]:
    return {
        "id": suggestion.id,
        "workspace_id": suggestion.workspace_id,
        "target_type": suggestion.target_type,
        "target_id": suggestion.target_id,
        "role_id": suggestion.role_id,
        "application_id": suggestion.application_id,
        "artifact_id": suggestion.artifact_id,
        "action_type": suggestion.action_type,
        "title": suggestion.title,
        "summary": suggestion.summary,
        "reason": suggestion.reason,
        "basis": suggestion.basis,
        "confidence": suggestion.confidence,
        "source_inputs": suggestion.source_inputs or {},
        "preview": _preview_response(suggestion.preview, suggestion.preview_hash),
        "preview_hash": suggestion.preview_hash,
        "status": suggestion.status,
        "expires_at": suggestion.expires_at,
        "policy_version": suggestion.policy_version,
        "metadata": suggestion.suggestion_metadata or {},
        "created_at": suggestion.created_at,
        "updated_at": suggestion.updated_at,
    }


def _approval_log_response(log: AutomationApprovalLog) -> dict[str, Any]:
    return {
        "id": log.id,
        "workspace_id": log.workspace_id,
        "suggestion_id": log.suggestion_id,
        "actor": log.actor,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "action_type": log.action_type,
        "preview": _preview_response(log.preview, log.preview_hash),
        "preview_hash": log.preview_hash,
        "approval_status": log.approval_status,
        "dismissal_or_rejection_reason": log.dismissal_or_rejection_reason,
        "execution_status": log.execution_status,
        "execution_result": log.execution_result or {},
        "external_mutation": False,
        "policy_version": log.policy_version,
        "created_at": log.created_at,
        "decided_at": log.decided_at,
        "executed_at": log.executed_at,
    }


def _preview_response(preview: dict[str, Any], preview_hash: str) -> dict[str, Any]:
    return {
        "title": str(preview.get("title") or "Review suggestion"),
        "body": str(preview.get("body") or ""),
        "content_hash": str(preview.get("content_hash") or preview_hash),
        "external_mutation": False,
    }


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()
