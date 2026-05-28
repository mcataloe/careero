from __future__ import annotations

from datetime import datetime, timezone

from app.constants import ArtifactLifecycleStatus
from app.models import GeneratedArtifact


class ArtifactLifecycleError(Exception):
    pass


class ArtifactLifecycleTransitionError(ArtifactLifecycleError):
    pass


_TRANSITIONS: dict[ArtifactLifecycleStatus, tuple[ArtifactLifecycleStatus, ...]] = {
    ArtifactLifecycleStatus.DRAFT: (
        ArtifactLifecycleStatus.REVIEWED,
        ArtifactLifecycleStatus.ARCHIVED,
    ),
    ArtifactLifecycleStatus.REVIEWED: (
        ArtifactLifecycleStatus.SUBMITTED,
        ArtifactLifecycleStatus.ARCHIVED,
    ),
    ArtifactLifecycleStatus.SUBMITTED: (ArtifactLifecycleStatus.ARCHIVED,),
    ArtifactLifecycleStatus.ARCHIVED: (),
}

_LEGACY_STATUS_MAP = {
    "approved": ArtifactLifecycleStatus.REVIEWED.value,
    "exported": ArtifactLifecycleStatus.REVIEWED.value,
}


def normalize_artifact_lifecycle_status(value: str | None) -> str:
    normalized = (value or ArtifactLifecycleStatus.DRAFT.value).strip().lower()
    normalized = _LEGACY_STATUS_MAP.get(normalized, normalized)
    if normalized not in {status.value for status in ArtifactLifecycleStatus}:
        return ArtifactLifecycleStatus.DRAFT.value
    return normalized


def get_available_artifact_transitions(
    current_status: str | ArtifactLifecycleStatus,
) -> list[ArtifactLifecycleStatus]:
    status = _coerce_status(str(current_status), unknown_as_draft=True)
    return list(_TRANSITIONS[status])


def can_transition_artifact(
    from_status: str | ArtifactLifecycleStatus,
    to_status: str | ArtifactLifecycleStatus,
) -> bool:
    source = _coerce_status(str(from_status), unknown_as_draft=True)
    try:
        target = _coerce_status(str(to_status), unknown_as_draft=False)
    except ArtifactLifecycleTransitionError:
        return False
    if source == target:
        return True
    return target in _TRANSITIONS[source]


def transition_artifact(
    artifact: GeneratedArtifact,
    to_status: str | ArtifactLifecycleStatus,
    *,
    changed_at: datetime | None = None,
) -> GeneratedArtifact:
    current = _coerce_status(artifact.lifecycle_status, unknown_as_draft=True)
    target = _coerce_status(str(to_status), unknown_as_draft=False)
    if current == target:
        return artifact
    if not can_transition_artifact(current, target):
        raise ArtifactLifecycleTransitionError(
            f"Invalid artifact lifecycle transition from '{current.value}' to '{target.value}'"
        )

    occurred_at = changed_at or datetime.now(timezone.utc)
    artifact.lifecycle_status = target.value
    if target == ArtifactLifecycleStatus.REVIEWED and artifact.reviewed_at is None:
        artifact.reviewed_at = occurred_at
    if target == ArtifactLifecycleStatus.SUBMITTED and artifact.submitted_at is None:
        artifact.submitted_at = occurred_at
    if target == ArtifactLifecycleStatus.ARCHIVED and artifact.archived_at is None:
        artifact.archived_at = occurred_at
    _sync_contract_lifecycle(artifact)
    return artifact


def _coerce_status(
    value: str | None,
    *,
    unknown_as_draft: bool,
) -> ArtifactLifecycleStatus:
    normalized = (value or ArtifactLifecycleStatus.DRAFT.value).strip().lower()
    normalized = _LEGACY_STATUS_MAP.get(normalized, normalized)
    if normalized in {status.value for status in ArtifactLifecycleStatus}:
        return ArtifactLifecycleStatus(normalized)
    if unknown_as_draft:
        return ArtifactLifecycleStatus.DRAFT
    raise ArtifactLifecycleTransitionError(f"Unknown artifact lifecycle status: {value}")


def _sync_contract_lifecycle(artifact: GeneratedArtifact) -> None:
    metadata = dict(artifact.artifact_metadata or {})
    contract = metadata.get("contract")
    if isinstance(contract, dict):
        contract = dict(contract)
        contract["lifecycleStatus"] = artifact.lifecycle_status
        contract["reviewedAt"] = _isoformat(artifact.reviewed_at)
        contract["submittedAt"] = _isoformat(artifact.submitted_at)
        contract["archivedAt"] = _isoformat(artifact.archived_at)
        metadata["contract"] = contract
        artifact.artifact_metadata = metadata


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()
