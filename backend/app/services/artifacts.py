from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import ArtifactLifecycleStatus
from app.models import (
    Application,
    CompassEvaluation,
    GeneratedArtifact,
    ResumeSourceVersion,
    Role,
    User,
)
from app.schemas.artifacts import ArtifactDraftCreate, ArtifactDraftUpdate
from app.services.activity_log import ActivityLogService
from app.services.artifact_lifecycle import (
    ArtifactLifecycleTransitionError,
    get_available_artifact_transitions,
    normalize_artifact_lifecycle_status,
    transition_artifact,
)
from app.services.current_user import CurrentUserResolutionError, resolve_current_user
from app.services.ownership import (
    require_active_user_workspace_for_new_work,
    require_user_application,
    require_user_role,
    require_user_workspace,
)


class ArtifactError(Exception):
    pass


class ArtifactSeedMissingError(ArtifactError):
    pass


class ArtifactNotFoundError(ArtifactError):
    pass


class ArtifactWorkspaceNotFoundError(ArtifactError):
    pass


class ArtifactWorkspaceInactiveError(ArtifactError):
    pass


class ArtifactValidationError(ArtifactError):
    pass


class ArtifactTransitionError(ArtifactError):
    pass


class ArtifactService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.activity_log = ActivityLogService(db)

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise ArtifactSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def create_draft(self, payload: ArtifactDraftCreate) -> dict[str, Any]:
        user = self.get_default_user()
        workspace = require_active_user_workspace_for_new_work(
            self.db,
            user_id=user.id,
            workspace_id=payload.workspace_id,
            not_found_error_cls=ArtifactWorkspaceNotFoundError,
            inactive_error_cls=ArtifactWorkspaceInactiveError,
            not_found_message="Workspace not found",
            inactive_message="Workspace is not active",
        )
        role_id = payload.role_id or payload.opportunity_id
        if (
            payload.role_id is not None
            and payload.opportunity_id is not None
            and payload.role_id != payload.opportunity_id
        ):
            raise ArtifactValidationError("role_id and opportunity_id must match")
        role = self._role(user_id=user.id, role_id=role_id) if role_id else None
        application = self._application(user_id=user.id, application_id=payload.application_id)
        if role is not None and role.workspace_id != workspace.id:
            raise ArtifactValidationError("Role does not belong to workspace")
        if application is not None:
            if application.workspace_id != workspace.id:
                raise ArtifactValidationError("Application does not belong to workspace")
            if role is None:
                role = application.role
            elif application.role_id != role.id:
                raise ArtifactValidationError("Application does not belong to role")
        evaluation = self._evaluation(
            user_id=user.id,
            workspace_id=workspace.id,
            role_id=role.id if role is not None else None,
            evaluation_id=payload.evaluation_id,
        )
        source_version = self._source_version(
            user_id=user.id,
            source_resume_version_id=payload.source_resume_version_id,
        )
        source_artifact = self._optional_artifact(
            user_id=user.id,
            artifact_id=payload.source_artifact_id,
        )
        if source_artifact is not None and source_artifact.workspace_id != workspace.id:
            raise ArtifactValidationError("Source artifact does not belong to workspace")
        version_number = (source_artifact.version_number + 1) if source_artifact else 1
        artifact = GeneratedArtifact(
            user_id=user.id,
            workspace_id=workspace.id,
            application_id=application.id if application is not None else None,
            role_id=role.id if role is not None else None,
            source_artifact_id=source_artifact.id if source_artifact is not None else None,
            evaluation_id=evaluation.id if evaluation is not None else None,
            source_resume_version_id=(
                source_version.id if source_version is not None else None
            ),
            artifact_type=payload.artifact_type,
            lifecycle_status=ArtifactLifecycleStatus.DRAFT.value,
            version_number=version_number,
            title=payload.title.strip(),
            content=payload.content.strip(),
            artifact_metadata=_draft_metadata(
                artifact_id=None,
                workspace_id=workspace.id,
                role_id=role.id if role is not None else None,
                artifact_type=payload.artifact_type,
                title=payload.title.strip(),
                content=payload.content.strip(),
                version_number=version_number,
                parent_artifact_id=source_artifact.id if source_artifact is not None else None,
                evaluation_id=evaluation.id if evaluation is not None else None,
                source_resume_version_id=(
                    source_version.id if source_version is not None else None
                ),
                change_summary=payload.change_summary or "Created artifact draft.",
            ),
        )
        self.db.add(artifact)
        self.db.flush()
        _sync_contract_identity(artifact)
        self._log(artifact, "artifact.draft_created", {"version_number": version_number})
        self.db.commit()
        return self.get_artifact(artifact.id)

    def list_artifacts(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
        opportunity_id: uuid.UUID | None = None,
        application_id: uuid.UUID | None = None,
        include_archived: bool = False,
    ) -> list[dict[str, Any]]:
        user = self.get_default_user()
        filters = [GeneratedArtifact.user_id == user.id, GeneratedArtifact.deleted_at.is_(None)]
        if workspace_id is not None:
            require_user_workspace(
                self.db,
                user_id=user.id,
                workspace_id=workspace_id,
                include_inactive=True,
                error_cls=ArtifactWorkspaceNotFoundError,
                error_message="Workspace not found",
            )
            filters.append(GeneratedArtifact.workspace_id == workspace_id)
        if opportunity_id is not None:
            require_user_role(
                self.db,
                user_id=user.id,
                role_id=opportunity_id,
                include_archived=True,
                error_cls=ArtifactNotFoundError,
                error_message="Opportunity not found",
            )
            filters.append(GeneratedArtifact.role_id == opportunity_id)
        if application_id is not None:
            application = require_user_application(
                self.db,
                user_id=user.id,
                application_id=application_id,
                error_cls=ArtifactNotFoundError,
                error_message="Application workflow not found",
            )
            filters.append(GeneratedArtifact.role_id == application.role_id)
            filters.append(GeneratedArtifact.workspace_id == application.workspace_id)
        if not include_archived:
            filters.append(
                GeneratedArtifact.lifecycle_status != ArtifactLifecycleStatus.ARCHIVED.value
            )
        statement = (
            select(GeneratedArtifact)
            .where(*filters)
            .order_by(
                GeneratedArtifact.updated_at.desc(),
                GeneratedArtifact.created_at.desc(),
                GeneratedArtifact.id.desc(),
            )
        )
        return [self._response(artifact) for artifact in self.db.scalars(statement)]

    def get_artifact(self, artifact_id: uuid.UUID) -> dict[str, Any]:
        artifact = self._require_artifact(artifact_id)
        return self._response(artifact)

    def update_draft(
        self,
        artifact_id: uuid.UUID,
        payload: ArtifactDraftUpdate,
    ) -> dict[str, Any]:
        artifact = self._require_artifact(artifact_id)
        updates = payload.model_dump(exclude_unset=True)
        if not updates or ("title" not in updates and "content" not in updates):
            return self._response(artifact)
        if artifact.lifecycle_status == ArtifactLifecycleStatus.SUBMITTED.value:
            new_artifact = self._new_draft_from_submitted(artifact, payload)
            self.db.add(new_artifact)
            self.db.flush()
            _sync_contract_identity(new_artifact)
            self._log(
                new_artifact,
                "artifact.new_version_created",
                {"source_artifact_id": str(artifact.id)},
            )
            self.db.commit()
            response = self.get_artifact(new_artifact.id)
            response["new_version_created"] = True
            response["source_submitted_artifact_id"] = artifact.id
            return response
        if artifact.lifecycle_status != ArtifactLifecycleStatus.DRAFT.value:
            raise ArtifactValidationError("Only draft artifacts can be edited directly")

        if payload.title is not None:
            artifact.title = payload.title.strip()
        if payload.content is not None:
            artifact.content = payload.content.strip()
        artifact.version_number += 1
        _sync_contract_content(
            artifact,
            change_summary=payload.change_summary or "Updated draft artifact.",
        )
        self._log(artifact, "artifact.draft_updated", {"version_number": artifact.version_number})
        self.db.commit()
        return self.get_artifact(artifact.id)

    def mark_reviewed(self, artifact_id: uuid.UUID) -> dict[str, Any]:
        return self._transition(artifact_id, ArtifactLifecycleStatus.REVIEWED)

    def mark_submitted(self, artifact_id: uuid.UUID) -> dict[str, Any]:
        artifact = self._require_artifact(artifact_id)
        if artifact.application_id is None and artifact.role_id is not None:
            application = self._application_for_role(artifact)
            if application is not None:
                artifact.application_id = application.id
        return self._transition_loaded(artifact, ArtifactLifecycleStatus.SUBMITTED)

    def archive(self, artifact_id: uuid.UUID) -> dict[str, Any]:
        return self._transition(artifact_id, ArtifactLifecycleStatus.ARCHIVED)

    def _transition(
        self,
        artifact_id: uuid.UUID,
        status: ArtifactLifecycleStatus,
    ) -> dict[str, Any]:
        artifact = self._require_artifact(artifact_id)
        return self._transition_loaded(artifact, status)

    def _transition_loaded(
        self,
        artifact: GeneratedArtifact,
        status: ArtifactLifecycleStatus,
    ) -> dict[str, Any]:
        previous = normalize_artifact_lifecycle_status(artifact.lifecycle_status)
        try:
            transition_artifact(artifact, status)
        except ArtifactLifecycleTransitionError as exc:
            raise ArtifactTransitionError(str(exc)) from exc
        if previous != artifact.lifecycle_status:
            self._log(
                artifact,
                f"artifact.{artifact.lifecycle_status}",
                {"from_status": previous, "to_status": artifact.lifecycle_status},
            )
            self.db.commit()
        else:
            self.db.rollback()
        return self.get_artifact(artifact.id)

    def _new_draft_from_submitted(
        self,
        artifact: GeneratedArtifact,
        payload: ArtifactDraftUpdate,
    ) -> GeneratedArtifact:
        metadata = copy.deepcopy(artifact.artifact_metadata or {})
        contract = metadata.get("contract")
        if isinstance(contract, dict):
            contract["id"] = None
            contract["title"] = (payload.title or artifact.title).strip()
            contract["content"] = (payload.content or artifact.content).strip()
            contract["lifecycleStatus"] = ArtifactLifecycleStatus.DRAFT.value
            contract["reviewedAt"] = None
            contract["submittedAt"] = None
            contract["archivedAt"] = None
            revision = dict(contract.get("revision") or {})
            revision["revisionId"] = str(uuid.uuid4())
            revision["parentArtifactId"] = str(artifact.id)
            revision["revisionNumber"] = artifact.version_number + 1
            revision["changeSummary"] = (
                payload.change_summary
                or "Created a new draft version from submitted artifact."
            )
            revision["createdAt"] = _iso_now()
            contract["revision"] = revision
            metadata["contract"] = contract
        return GeneratedArtifact(
            user_id=artifact.user_id,
            workspace_id=artifact.workspace_id,
            application_id=artifact.application_id,
            role_id=artifact.role_id,
            source_artifact_id=artifact.id,
            evaluation_id=artifact.evaluation_id,
            source_resume_version_id=artifact.source_resume_version_id,
            artifact_type=artifact.artifact_type,
            lifecycle_status=ArtifactLifecycleStatus.DRAFT.value,
            version_number=artifact.version_number + 1,
            title=(payload.title or artifact.title).strip(),
            content=(payload.content or artifact.content).strip(),
            artifact_metadata=metadata,
        )

    def _require_artifact(self, artifact_id: uuid.UUID) -> GeneratedArtifact:
        user = self.get_default_user()
        artifact = self.db.get(GeneratedArtifact, artifact_id)
        if (
            artifact is None
            or artifact.user_id != user.id
            or artifact.deleted_at is not None
        ):
            raise ArtifactNotFoundError("Artifact not found")
        artifact.lifecycle_status = normalize_artifact_lifecycle_status(
            artifact.lifecycle_status
        )
        return artifact

    def _optional_artifact(
        self,
        *,
        user_id: uuid.UUID,
        artifact_id: uuid.UUID | None,
    ) -> GeneratedArtifact | None:
        if artifact_id is None:
            return None
        artifact = self.db.get(GeneratedArtifact, artifact_id)
        if artifact is None or artifact.user_id != user_id or artifact.deleted_at is not None:
            raise ArtifactNotFoundError("Source artifact not found")
        return artifact

    def _role(self, *, user_id: uuid.UUID, role_id: uuid.UUID | None) -> Role | None:
        if role_id is None:
            return None
        return require_user_role(
            self.db,
            user_id=user_id,
            role_id=role_id,
            include_archived=True,
            error_cls=ArtifactNotFoundError,
            error_message="Opportunity not found",
        )

    def _application(
        self,
        *,
        user_id: uuid.UUID,
        application_id: uuid.UUID | None,
    ) -> Application | None:
        if application_id is None:
            return None
        return require_user_application(
            self.db,
            user_id=user_id,
            application_id=application_id,
            error_cls=ArtifactNotFoundError,
            error_message="Application workflow not found",
        )

    def _evaluation(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        role_id: uuid.UUID | None,
        evaluation_id: uuid.UUID | None,
    ) -> CompassEvaluation | None:
        if evaluation_id is None:
            return None
        filters = [
            CompassEvaluation.id == evaluation_id,
            CompassEvaluation.user_id == user_id,
            CompassEvaluation.workspace_id == workspace_id,
            CompassEvaluation.deleted_at.is_(None),
        ]
        if role_id is not None:
            filters.append(CompassEvaluation.role_id == role_id)
        evaluation = self.db.scalar(select(CompassEvaluation).where(*filters))
        if evaluation is None:
            raise ArtifactNotFoundError("COMPASS evaluation not found")
        return evaluation

    def _source_version(
        self,
        *,
        user_id: uuid.UUID,
        source_resume_version_id: uuid.UUID | None,
    ) -> ResumeSourceVersion | None:
        if source_resume_version_id is None:
            return None
        source_version = self.db.scalar(
            select(ResumeSourceVersion).where(
                ResumeSourceVersion.id == source_resume_version_id,
                ResumeSourceVersion.user_id == user_id,
            )
        )
        if source_version is None:
            raise ArtifactNotFoundError("Resume source version not found")
        return source_version

    def _application_for_role(self, artifact: GeneratedArtifact) -> Application | None:
        return self.db.scalar(
            select(Application)
            .where(
                Application.user_id == artifact.user_id,
                Application.workspace_id == artifact.workspace_id,
                Application.role_id == artifact.role_id,
                Application.deleted_at.is_(None),
            )
            .order_by(Application.created_at.desc(), Application.id.desc())
            .limit(1)
        )

    def _response(self, artifact: GeneratedArtifact) -> dict[str, Any]:
        contract = (
            artifact.artifact_metadata.get("contract")
            if artifact.artifact_metadata
            else None
        )
        revision = contract.get("revision", {}) if isinstance(contract, dict) else {}
        generation = (
            contract.get("generationMetadata", {}) if isinstance(contract, dict) else {}
        )
        format_metadata = (
            contract.get("formatMetadata", {}) if isinstance(contract, dict) else {}
        )
        export_metadata = (
            contract.get("exportMetadata", []) if isinstance(contract, dict) else []
        )
        lifecycle_status = normalize_artifact_lifecycle_status(
            artifact.lifecycle_status
        )
        return {
            "id": artifact.id,
            "workspace_id": artifact.workspace_id,
            "application_id": artifact.application_id,
            "role_id": artifact.role_id,
            "opportunity_id": artifact.role_id,
            "artifact_type": artifact.artifact_type,
            "lifecycle_status": lifecycle_status,
            "version_number": artifact.version_number,
            "title": artifact.title,
            "content": artifact.content,
            "reviewed_at": artifact.reviewed_at,
            "submitted_at": artifact.submitted_at,
            "archived_at": artifact.archived_at,
            "created_at": artifact.created_at,
            "updated_at": artifact.updated_at,
            "traceability": {
                "workspace_id": artifact.workspace_id,
                "role_id": artifact.role_id,
                "opportunity_id": artifact.role_id,
                "application_id": artifact.application_id,
                "evaluation_id": artifact.evaluation_id,
                "source_resume_version_id": artifact.source_resume_version_id,
                "source_artifact_id": artifact.source_artifact_id,
                "parent_artifact_id": _uuid_or_none(revision.get("parentArtifactId")),
                "generation_warnings": _string_list(generation.get("warnings")),
                "export_formats": _export_formats(
                    format_metadata=format_metadata,
                    export_metadata=export_metadata,
                ),
            },
            "available_transitions": [
                status.value for status in get_available_artifact_transitions(lifecycle_status)
            ],
            "new_version_created": False,
            "source_submitted_artifact_id": None,
            "metadata": {
                "revision_id": revision.get("revisionId"),
                "change_summary": revision.get("changeSummary"),
            },
        }

    def _log(
        self,
        artifact: GeneratedArtifact,
        action: str,
        details: dict[str, Any],
    ) -> None:
        self.activity_log.append(
            user_id=artifact.user_id,
            entity_type="generated_artifact",
            entity_id=artifact.id,
            action=action,
            details={
                **details,
                "workspace_id": str(artifact.workspace_id),
                "role_id": str(artifact.role_id) if artifact.role_id else None,
                "application_id": (
                    str(artifact.application_id) if artifact.application_id else None
                ),
                "artifact_type": artifact.artifact_type,
                "lifecycle_status": artifact.lifecycle_status,
            },
        )


def _draft_metadata(
    *,
    artifact_id: uuid.UUID | None,
    workspace_id: uuid.UUID,
    role_id: uuid.UUID | None,
    artifact_type: str,
    title: str,
    content: str,
    version_number: int,
    parent_artifact_id: uuid.UUID | None,
    evaluation_id: uuid.UUID | None,
    source_resume_version_id: uuid.UUID | None,
    change_summary: str,
) -> dict[str, Any]:
    now = _iso_now()
    return {
        "contract": {
            "contractVersion": "careero.contracts.v1",
            "id": str(artifact_id) if artifact_id is not None else None,
            "workspaceId": str(workspace_id),
            "opportunityId": str(role_id) if role_id is not None else None,
            "sourceArtifactId": str(parent_artifact_id) if parent_artifact_id else None,
            "artifactType": artifact_type,
            "lifecycleStatus": ArtifactLifecycleStatus.DRAFT.value,
            "title": title,
            "content": content,
            "generationMetadata": {
                "generatedBy": "user",
                "modelMetadata": None,
                "promptVersion": None,
                "inputHash": None,
                "groundingSourceIds": [
                    str(source_resume_version_id)
                ] if source_resume_version_id else [],
                "warnings": [],
            },
            "exportMetadata": [],
            "revision": {
                "revisionId": str(uuid.uuid4()),
                "parentArtifactId": str(parent_artifact_id) if parent_artifact_id else None,
                "revisionNumber": version_number,
                "changeSummary": change_summary,
                "createdAt": now,
            },
            "reviewedAt": None,
            "submittedAt": None,
            "archivedAt": None,
            "metadata": {
                "targetEvaluationId": str(evaluation_id) if evaluation_id else None,
                "sourceResumeVersionId": (
                    str(source_resume_version_id) if source_resume_version_id else None
                ),
                "employerFacingContentOnly": True,
            },
            "createdAt": now,
            "updatedAt": now,
        },
        "target_evaluation_id": str(evaluation_id) if evaluation_id else None,
        "source_resume": {
            "version_id": str(source_resume_version_id)
        } if source_resume_version_id else None,
        "workspace_id": str(workspace_id),
    }


def _sync_contract_identity(artifact: GeneratedArtifact) -> None:
    metadata = dict(artifact.artifact_metadata or {})
    contract = metadata.get("contract")
    if isinstance(contract, dict):
        contract = dict(contract)
        contract["id"] = str(artifact.id)
        contract["createdAt"] = _isoformat(artifact.created_at)
        contract["updatedAt"] = _isoformat(artifact.updated_at)
        metadata["contract"] = contract
        artifact.artifact_metadata = metadata


def _sync_contract_content(
    artifact: GeneratedArtifact,
    *,
    change_summary: str,
) -> None:
    metadata = dict(artifact.artifact_metadata or {})
    contract = metadata.get("contract")
    if isinstance(contract, dict):
        contract = dict(contract)
        contract["title"] = artifact.title
        contract["content"] = artifact.content
        contract["lifecycleStatus"] = artifact.lifecycle_status
        contract["updatedAt"] = _iso_now()
        revision = dict(contract.get("revision") or {})
        revision["revisionNumber"] = artifact.version_number
        revision["changeSummary"] = change_summary
        contract["revision"] = revision
        metadata["contract"] = contract
        artifact.artifact_metadata = metadata


def _export_formats(
    *,
    format_metadata: dict[str, Any],
    export_metadata: list[Any],
) -> list[str]:
    formats = set()
    if isinstance(format_metadata, dict):
        formats.update(str(item) for item in format_metadata.get("availableFormats") or [])
    for item in export_metadata:
        if isinstance(item, dict) and item.get("format"):
            formats.add(str(item["format"]))
    return sorted(formats)


def _uuid_or_none(value: Any) -> uuid.UUID | None:
    if value is None:
        return None
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()
