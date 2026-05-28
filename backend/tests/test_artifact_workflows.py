from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import ArtifactLifecycleStatus
from app.database import get_db
from app.main import create_app
from app.models import ActivityLog, GeneratedArtifact
from app.schemas.artifacts import ArtifactDraftCreate, ArtifactDraftUpdate
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.seed import DEFAULT_WORKSPACE_ID, seed_local_data
from app.services.applications import ApplicationWorkflowService
from app.services.artifacts import (
    ArtifactNotFoundError,
    ArtifactService,
    ArtifactTransitionError,
)
from app.services.roles import RoleService


@pytest.fixture
def artifact_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def create_role(db_session: Session):
    return RoleService(db_session).create_role(
        RoleCreate(
            workspace_id=DEFAULT_WORKSPACE_ID,
            title="Senior Platform Engineer",
            company=CompanyLookup(name="Artifact Workflow Co"),
            source=SourceLookup(source_type="manual"),
            job_url="https://example.com/jobs/artifact-workflow",
            location="Chicago, IL",
            remote_type="hybrid",
            raw_description="Build workflow-aware platforms.",
            status="interested",
        )
    )


def draft_payload(db_session: Session, *, artifact_type: str = "tailored_resume"):
    role = create_role(db_session)
    application = ApplicationWorkflowService(db_session).get_or_create_for_role(role.id)
    return ArtifactDraftCreate(
        workspace_id=DEFAULT_WORKSPACE_ID,
        opportunity_id=role.id,
        application_id=UUID(application["id"]),
        artifact_type=artifact_type,
        title="Targeted artifact",
        content="Employer-facing artifact content.",
        change_summary="Initial local draft.",
    )


def test_create_and_update_draft_artifact_preserves_traceability(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    service = ArtifactService(db_session)

    created = service.create_draft(draft_payload(db_session))
    updated = service.update_draft(
        created["id"],
        ArtifactDraftUpdate(
            title="Updated targeted resume",
            content="Updated employer-facing content.",
            change_summary="Tightened platform narrative.",
        ),
    )

    assert created["lifecycle_status"] == ArtifactLifecycleStatus.DRAFT.value
    assert updated["version_number"] == 2
    assert updated["title"] == "Updated targeted resume"
    assert updated["traceability"]["workspace_id"] == DEFAULT_WORKSPACE_ID
    assert updated["traceability"]["opportunity_id"] == created["opportunity_id"]
    assert updated["traceability"]["application_id"] == created["application_id"]


def test_review_submit_archive_transitions_and_activity_log(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    service = ArtifactService(db_session)
    created = service.create_draft(draft_payload(db_session, artifact_type="cover_letter"))

    reviewed = service.mark_reviewed(created["id"])
    submitted = service.mark_submitted(created["id"])
    archived = service.archive(created["id"])

    assert reviewed["lifecycle_status"] == ArtifactLifecycleStatus.REVIEWED.value
    assert reviewed["reviewed_at"] is not None
    assert submitted["lifecycle_status"] == ArtifactLifecycleStatus.SUBMITTED.value
    assert submitted["submitted_at"] is not None
    assert archived["lifecycle_status"] == ArtifactLifecycleStatus.ARCHIVED.value
    assert archived["archived_at"] is not None
    actions = list(
        db_session.scalars(
            select(ActivityLog.action).where(ActivityLog.entity_id == created["id"])
        )
    )
    assert "artifact.reviewed" in actions
    assert "artifact.submitted" in actions
    assert "artifact.archived" in actions


def test_rejects_direct_submit_from_draft(db_session: Session) -> None:
    seed_local_data(db_session)
    service = ArtifactService(db_session)
    created = service.create_draft(draft_payload(db_session))

    with pytest.raises(ArtifactTransitionError):
        service.mark_submitted(created["id"])

    artifact = db_session.get(GeneratedArtifact, created["id"])
    assert artifact is not None
    assert artifact.lifecycle_status == ArtifactLifecycleStatus.DRAFT.value
    assert artifact.submitted_at is None


def test_editing_submitted_artifact_creates_new_draft_revision(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    service = ArtifactService(db_session)
    created = service.create_draft(draft_payload(db_session))
    service.mark_reviewed(created["id"])
    submitted = service.mark_submitted(created["id"])

    edited = service.update_draft(
        submitted["id"],
        ArtifactDraftUpdate(
            content="New employer-facing draft content.",
            change_summary="Follow-up edit after submission.",
        ),
    )

    original = db_session.get(GeneratedArtifact, submitted["id"])
    assert original is not None
    assert original.lifecycle_status == ArtifactLifecycleStatus.SUBMITTED.value
    assert original.content == "Employer-facing artifact content."
    assert edited["id"] != submitted["id"]
    assert edited["lifecycle_status"] == ArtifactLifecycleStatus.DRAFT.value
    assert edited["version_number"] == submitted["version_number"] + 1
    assert edited["traceability"]["source_artifact_id"] == submitted["id"]
    assert edited["new_version_created"] is True
    assert edited["source_submitted_artifact_id"] == submitted["id"]


def test_listing_excludes_archived_artifacts_by_default(db_session: Session) -> None:
    seed_local_data(db_session)
    service = ArtifactService(db_session)
    active = service.create_draft(draft_payload(db_session))
    archived = service.create_draft(draft_payload(db_session, artifact_type="cover_letter"))
    service.archive(archived["id"])

    default_items = service.list_artifacts(workspace_id=DEFAULT_WORKSPACE_ID)
    all_items = service.list_artifacts(
        workspace_id=DEFAULT_WORKSPACE_ID,
        include_archived=True,
    )

    assert [item["id"] for item in default_items] == [active["id"]]
    assert {item["id"] for item in all_items} == {active["id"], archived["id"]}


def test_artifact_response_keeps_internal_metadata_out_of_employer_content(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    service = ArtifactService(db_session)
    created = service.create_draft(draft_payload(db_session))
    artifact = db_session.get(GeneratedArtifact, created["id"])
    assert artifact is not None
    artifact.artifact_metadata = {
        **artifact.artifact_metadata,
        "internal_compass_analysis": "ATS risk notes and private strategy.",
        "compensation_strategy": "Private negotiation rationale.",
    }
    db_session.commit()

    detail = service.get_artifact(created["id"])

    assert detail["content"] == "Employer-facing artifact content."
    assert "ATS risk notes" not in str(detail["metadata"])
    assert "compensation_strategy" not in str(detail["traceability"])


def test_api_artifact_lifecycle_and_scoped_lists(
    artifact_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(db_session)
    application = ApplicationWorkflowService(db_session).get_or_create_for_role(role.id)

    create_response = artifact_client.post(
        "/api/artifacts",
        json={
            "workspace_id": str(DEFAULT_WORKSPACE_ID),
            "opportunity_id": str(role.id),
            "application_id": application["id"],
            "artifact_type": "tailored_resume",
            "title": "API resume draft",
            "content": "API employer-facing content.",
        },
    )
    assert create_response.status_code == 201
    artifact_id = create_response.json()["id"]

    review_response = artifact_client.post(f"/api/artifacts/{artifact_id}/review")
    submit_response = artifact_client.post(f"/api/artifacts/{artifact_id}/submit")
    list_response = artifact_client.get(f"/api/opportunities/{role.id}/artifacts")
    workspace_response = artifact_client.get(
        f"/api/workspaces/{DEFAULT_WORKSPACE_ID}/artifacts"
    )
    application_response = artifact_client.get(
        f"/api/applications/{application['id']}/artifacts"
    )

    assert review_response.status_code == 200
    assert submit_response.status_code == 200
    assert submit_response.json()["lifecycle_status"] == "submitted"
    assert [item["id"] for item in list_response.json()] == [artifact_id]
    assert [item["id"] for item in workspace_response.json()] == [artifact_id]
    assert [item["id"] for item in application_response.json()] == [artifact_id]


def test_application_timeline_includes_lifecycle_events(db_session: Session) -> None:
    seed_local_data(db_session)
    service = ArtifactService(db_session)
    created = service.create_draft(draft_payload(db_session))
    service.mark_reviewed(created["id"])
    submitted = service.mark_submitted(created["id"])

    timeline = ApplicationWorkflowService(db_session).get_timeline(
        submitted["application_id"]
    )
    by_type = {event["event_type"]: event for event in timeline}

    assert "artifact.resume.created" in by_type
    assert "artifact.reviewed" in by_type
    assert "artifact.submitted" in by_type
    assert "content" not in by_type["artifact.submitted"]["metadata"]


def test_artifact_not_found_for_wrong_scope(db_session: Session) -> None:
    seed_local_data(db_session)
    service = ArtifactService(db_session)

    with pytest.raises(ArtifactNotFoundError):
        service.get_artifact(uuid4())
