from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.constants import ArtifactLifecycleStatus
from app.models import GeneratedArtifact
from app.services.artifact_lifecycle import (
    ArtifactLifecycleTransitionError,
    can_transition_artifact,
    get_available_artifact_transitions,
    normalize_artifact_lifecycle_status,
    transition_artifact,
)


def _artifact(*, status: str = "draft") -> GeneratedArtifact:
    return GeneratedArtifact(
        id=uuid4(),
        user_id=uuid4(),
        workspace_id=uuid4(),
        role_id=uuid4(),
        artifact_type="cover_letter",
        lifecycle_status=status,
        version_number=1,
        title="Example cover letter",
        content="Employer-facing cover letter only.",
        artifact_metadata={
            "contract": {
                "id": str(uuid4()),
                "lifecycleStatus": status,
                "metadata": {
                    "targetEvaluationId": str(uuid4()),
                    "internalAnalysisSummary": "Private COMPASS rationale.",
                },
            }
        },
    )


def test_artifact_lifecycle_allows_expected_transitions() -> None:
    assert can_transition_artifact("draft", "reviewed")
    assert can_transition_artifact("reviewed", "submitted")
    assert can_transition_artifact("draft", "archived")
    assert can_transition_artifact("reviewed", "archived")
    assert can_transition_artifact("submitted", "archived")
    assert get_available_artifact_transitions("reviewed") == [
        ArtifactLifecycleStatus.SUBMITTED,
        ArtifactLifecycleStatus.ARCHIVED,
    ]


def test_artifact_lifecycle_rejects_invalid_transitions() -> None:
    assert not can_transition_artifact("draft", "submitted")
    assert not can_transition_artifact("submitted", "reviewed")
    assert not can_transition_artifact("archived", "draft")

    with pytest.raises(ArtifactLifecycleTransitionError):
        transition_artifact(_artifact(status="draft"), "submitted")


def test_submitted_and_archived_timestamps_are_preserved() -> None:
    reviewed_at = datetime(2026, 5, 28, 16, 0, tzinfo=timezone.utc)
    submitted_at = datetime(2026, 5, 28, 17, 0, tzinfo=timezone.utc)
    archived_at = datetime(2026, 5, 28, 18, 0, tzinfo=timezone.utc)
    artifact = _artifact(status="draft")

    transition_artifact(artifact, "reviewed", changed_at=reviewed_at)
    transition_artifact(artifact, "submitted", changed_at=submitted_at)
    transition_artifact(artifact, "submitted", changed_at=archived_at)
    transition_artifact(artifact, "archived", changed_at=archived_at)

    assert artifact.reviewed_at == reviewed_at
    assert artifact.submitted_at == submitted_at
    assert artifact.archived_at == archived_at
    assert artifact.artifact_metadata["contract"]["lifecycleStatus"] == "archived"
    assert artifact.artifact_metadata["contract"]["submittedAt"] == submitted_at.isoformat()


def test_legacy_lifecycle_statuses_normalize_to_reviewed() -> None:
    assert normalize_artifact_lifecycle_status("approved") == "reviewed"
    assert normalize_artifact_lifecycle_status("exported") == "reviewed"
    assert normalize_artifact_lifecycle_status("unknown") == "draft"


def test_lifecycle_transition_does_not_merge_internal_analysis_into_content() -> None:
    artifact = _artifact(status="draft")

    transition_artifact(artifact, "reviewed")

    assert artifact.content == "Employer-facing cover letter only."
    assert "Private COMPASS rationale" not in artifact.content
    assert artifact.artifact_metadata["contract"]["metadata"]["internalAnalysisSummary"]
