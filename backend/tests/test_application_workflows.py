from collections.abc import Generator
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import ApplicationWorkflowState, CompassEvaluationStatus
from app.database import get_db
from app.main import create_app
from app.models import (
    ActivityLog,
    Application,
    ApplicationExternalLink,
    ApplicationInterviewStage,
    ApplicationNote,
    ApplicationReminder,
    GeneratedArtifact,
    CompassEvaluation,
    User,
)
from app.schemas.applications import (
    ApplicationExternalLinkCreate,
    ApplicationExternalLinkUpdate,
    ApplicationInterviewCancelRequest,
    ApplicationInterviewCompleteRequest,
    ApplicationInterviewStageCreate,
    ApplicationInterviewStageUpdate,
    ApplicationMetadataUpdate,
    ApplicationNoteCreate,
    ApplicationNoteUpdate,
    ApplicationStateTransitionRequest,
)
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.schemas.workspaces import WorkspaceCreate
from app.seed import DEFAULT_LOCAL_USER_ID, DEFAULT_WORKSPACE_ID, seed_local_data
from app.services.applications import (
    ApplicationWorkflowNotFoundError,
    ApplicationWorkflowSeedMissingError,
    ApplicationWorkflowService,
    ApplicationWorkflowTransitionError,
    ApplicationWorkflowWorkspaceInactiveError,
)
from app.services.roles import RoleService
from app.services.workspaces import WorkspaceService


@pytest.fixture
def application_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def create_role(
    db_session: Session,
    *,
    company_name: str = "Workflow Co",
    title: str = "Senior Platform Engineer",
    status: str = "found",
    workspace_id=None,
):
    return RoleService(db_session).create_role(
        RoleCreate(
            workspace_id=workspace_id,
            title=title,
            company=CompanyLookup(name=company_name, website_url="https://example.com"),
            source=SourceLookup(source_type="manual"),
            job_url="https://example.com/jobs/platform",
            location="Chicago, IL",
            remote_type="hybrid",
            raw_description="Build Python platforms.",
            status=status,
        )
    )


def add_workflow_children(db_session: Session, application: Application) -> None:
    db_session.add_all(
        [
            ApplicationNote(
                application_id=application.id,
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                author="Local User",
                body="Follow up on platform ownership.",
            ),
            ApplicationReminder(
                application_id=application.id,
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                due_at=application.created_at,
                title="Follow up",
            ),
            ApplicationInterviewStage(
                application_id=application.id,
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                stage_type="recruiter_screen",
                title="Recruiter screen",
            ),
        ]
    )
    db_session.commit()


def add_summary_sources(db_session: Session, application: Application) -> None:
    db_session.add(
        CompassEvaluation(
            user_id=application.user_id,
            workspace_id=application.workspace_id,
            role_id=application.role_id,
            evaluation_status=CompassEvaluationStatus.COMPLETED.value,
            overall_score=Decimal("82.50"),
            recommendation="apply",
            confidence_level="high",
            summary="Strong platform fit.",
        )
    )
    db_session.add_all(
        [
            GeneratedArtifact(
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                role_id=application.role_id,
                artifact_type="tailored_resume",
                title="Tailored resume",
                content="resume",
                artifact_metadata={
                    "contract": {
                        "revision": {"revisionNumber": 2},
                    }
                },
            ),
            GeneratedArtifact(
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                role_id=application.role_id,
                artifact_type="cover_letter",
                title="Cover letter",
                content="letter",
                artifact_metadata={
                    "contract": {
                        "revision": {"revisionNumber": 1},
                    }
                },
            ),
        ]
    )
    db_session.commit()


def test_service_ensures_workflow_and_prevents_duplicate(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session, status="interested")
    service = ApplicationWorkflowService(db_session)

    first = service.get_or_create_for_role(role.id)
    second = service.get_or_create_for_role(role.id)

    assert first["id"] == second["id"]
    assert first["current_state"] == "interested"
    assert first["role"]["id"] == role.id
    applications = list(db_session.scalars(select(Application).where(Application.role_id == role.id)))
    assert len(applications) == 1
    assert applications[0].status == applications[0].current_state


def test_service_lists_by_workspace_and_aggregates_summaries(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    other_workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(title="Contract Search")
    )
    default_role = create_role(db_session, company_name="Default Co")
    other_role = create_role(
        db_session,
        company_name="Other Co",
        workspace_id=other_workspace.id,
    )
    service = ApplicationWorkflowService(db_session)
    default_detail = service.get_or_create_for_role(default_role.id)
    service.get_or_create_for_role(other_role.id)
    default_application = db_session.get(Application, UUID(default_detail["id"]))
    assert default_application is not None
    add_workflow_children(db_session, default_application)
    add_summary_sources(db_session, default_application)

    all_items = service.list_applications()
    default_items = service.list_applications(workspace_id=DEFAULT_WORKSPACE_ID)
    other_items = service.list_applications(workspace_id=other_workspace.id)

    assert {item["workspace_id"] for item in all_items} == {
        DEFAULT_WORKSPACE_ID,
        other_workspace.id,
    }
    assert [item["role_id"] for item in default_items] == [default_role.id]
    assert [item["role_id"] for item in other_items] == [other_role.id]
    item = default_items[0]
    assert item["title"] == "Senior Platform Engineer"
    assert item["company"]["name"] == "Default Co"
    assert item["compass"]["summary"] == "Strong platform fit."
    assert item["resume_artifact"]["revision_number"] == 2
    assert item["cover_letter_artifact"]["revision_number"] == 1
    assert item["counts"] == {"notes": 1, "reminders": 1, "interviews": 1}


def test_service_detail_and_metadata_update(db_session: Session) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)

    updated = service.update_application(
        UUID(detail["id"]),
        ApplicationMetadataUpdate(
            workflow_metadata={"priority": "high"},
            applied_at="2026-05-16T15:00:00Z",
        ),
    )

    assert updated["workflow_metadata"]["createdFromRole"] is True
    assert updated["workflow_metadata"]["priority"] == "high"
    assert updated["current_state"] == "discovered"
    assert updated["application_state"]["currentState"] == "discovered"
    assert updated["state_history"][0]["state"] == "discovered"

    actions = list(
        db_session.scalars(
            select(ActivityLog.action).where(ActivityLog.entity_id == UUID(detail["id"]))
        )
    )
    assert "application.updated" in actions


@pytest.mark.parametrize(
    ("from_state", "to_state"),
    [
        ("discovered", "interested"),
        ("discovered", "withdrawn"),
        ("discovered", "archived"),
        ("interested", "applied"),
        ("interested", "withdrawn"),
        ("interested", "archived"),
        ("applied", "interviewing"),
        ("applied", "rejected"),
        ("applied", "withdrawn"),
        ("applied", "archived"),
        ("interviewing", "offer"),
        ("interviewing", "rejected"),
        ("interviewing", "withdrawn"),
        ("interviewing", "archived"),
        ("offer", "withdrawn"),
        ("offer", "archived"),
        ("rejected", "archived"),
        ("withdrawn", "archived"),
    ],
)
def test_service_allows_explicit_transition_matrix(
    db_session: Session,
    from_state: str,
    to_state: str,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)
    application = db_session.get(Application, UUID(detail["id"]))
    assert application is not None
    application.current_state = from_state
    application.status = from_state
    application.archived_at = (
        datetime.now(timezone.utc)
        if from_state == ApplicationWorkflowState.ARCHIVED.value
        else None
    )
    db_session.commit()

    updated = service.transition_state(
        application.id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState(to_state)),
    )

    assert updated["current_state"] == to_state
    db_session.refresh(application)
    assert application.status == to_state
    assert application.role.status == "found"
    history = application.state_history[-1]
    assert history.from_state == from_state
    assert history.to_state == to_state
    assert "application.state_changed" in list(
        db_session.scalars(
            select(ActivityLog.action).where(ActivityLog.entity_id == application.id)
        )
    )


def test_service_rejects_invalid_transition_without_history(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)
    application = db_session.get(Application, UUID(detail["id"]))
    assert application is not None
    initial_history_count = len(application.state_history)

    with pytest.raises(ApplicationWorkflowTransitionError):
        service.transition_state(
            application.id,
            ApplicationStateTransitionRequest(state=ApplicationWorkflowState.OFFER),
        )

    db_session.refresh(application)
    assert application.current_state == ApplicationWorkflowState.DISCOVERED.value
    assert len(application.state_history) == initial_history_count


def test_service_same_state_transition_is_idempotent(db_session: Session) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)
    application = db_session.get(Application, UUID(detail["id"]))
    assert application is not None
    initial_history_count = len(application.state_history)

    updated = service.transition_state(
        application.id,
        ApplicationStateTransitionRequest(
            state=ApplicationWorkflowState.DISCOVERED,
            reason="No change.",
        ),
    )

    assert updated["current_state"] == ApplicationWorkflowState.DISCOVERED.value
    assert len(application.state_history) == initial_history_count


def test_service_requires_explicit_reactivation(db_session: Session) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)
    application = db_session.get(Application, UUID(detail["id"]))
    assert application is not None
    service.transition_state(
        application.id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.ARCHIVED),
    )

    with pytest.raises(ApplicationWorkflowTransitionError):
        service.transition_state(
            application.id,
            ApplicationStateTransitionRequest(state=ApplicationWorkflowState.INTERESTED),
        )

    reactivated = service.transition_state(
        application.id,
        ApplicationStateTransitionRequest(
            state=ApplicationWorkflowState.INTERESTED,
            reactivate=True,
        ),
    )

    db_session.refresh(application)
    assert reactivated["current_state"] == ApplicationWorkflowState.INTERESTED.value
    assert application.archived_at is None
    assert application.reactivated_at is not None


def test_service_available_next_states_and_pipeline(db_session: Session) -> None:
    seed_local_data(db_session)
    service = ApplicationWorkflowService(db_session)
    discovered = create_role(db_session, company_name="Discovered Co")
    applied = create_role(db_session, company_name="Applied Co", status="applied")
    archived = create_role(db_session, company_name="Archived Co")
    discovered_detail = service.get_or_create_for_role(discovered.id)
    applied_detail = service.get_or_create_for_role(applied.id)
    archived_detail = service.get_or_create_for_role(archived.id)
    archived_application = db_session.get(Application, UUID(archived_detail["id"]))
    assert archived_application is not None
    service.transition_state(
        archived_application.id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.ARCHIVED),
    )

    assert discovered_detail["available_next_states"] == [
        ApplicationWorkflowState.INTERESTED,
        ApplicationWorkflowState.WITHDRAWN,
        ApplicationWorkflowState.ARCHIVED,
    ]
    assert applied_detail["available_next_states"] == [
        ApplicationWorkflowState.INTERVIEWING,
        ApplicationWorkflowState.REJECTED,
        ApplicationWorkflowState.WITHDRAWN,
        ApplicationWorkflowState.ARCHIVED,
    ]

    active_pipeline = service.get_pipeline()
    assert "archived" not in active_pipeline["states"]
    assert [item["role_id"] for item in active_pipeline["states"]["discovered"]] == [
        discovered.id
    ]
    assert [item["role_id"] for item in active_pipeline["states"]["applied"]] == [
        applied.id
    ]

    inactive_pipeline = service.get_pipeline(include_inactive=True)
    assert [item["role_id"] for item in inactive_pipeline["states"]["archived"]] == [
        archived.id
    ]


def test_service_timeline_includes_creation_state_changes_and_orders_events(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)
    application = db_session.get(Application, UUID(detail["id"]))
    assert application is not None
    service.transition_state(
        application.id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.INTERESTED),
    )
    service.transition_state(
        application.id,
        ApplicationStateTransitionRequest(state=ApplicationWorkflowState.ARCHIVED),
    )
    service.transition_state(
        application.id,
        ApplicationStateTransitionRequest(
            state=ApplicationWorkflowState.DISCOVERED,
            reactivate=True,
        ),
    )

    timeline = service.get_timeline(application.id)

    event_types = [event["event_type"] for event in timeline]
    assert "application.created" in event_types
    assert "application.state_changed" in event_types
    assert "application.archived" in event_types
    assert "application.reactivated" in event_types
    assert [event["occurred_at"] for event in timeline] == sorted(
        [event["occurred_at"] for event in timeline],
        reverse=True,
    )


def test_service_timeline_includes_typed_children_evaluations_and_artifacts(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)
    application = db_session.get(Application, UUID(detail["id"]))
    assert application is not None
    add_workflow_children(db_session, application)
    add_summary_sources(db_session, application)
    reminder = application.reminders[0]
    reminder.completed_at = datetime.now(timezone.utc)
    stage = application.interview_stages[0]
    stage.completed_at = datetime.now(timezone.utc)
    db_session.commit()

    timeline = service.get_timeline(application.id)

    by_type = {event["event_type"]: event for event in timeline}
    assert "note.created" in by_type
    assert "reminder.created" in by_type
    assert "reminder.completed" in by_type
    assert "interview.created" in by_type
    assert "interview.completed" in by_type
    assert "compass.completed" in by_type
    assert "artifact.resume.created" in by_type
    assert "artifact.cover_letter.created" in by_type
    assert "content" not in by_type["artifact.resume.created"]["metadata"]


def test_service_note_crud_uses_soft_delete_and_updates_counts(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)
    application_id = UUID(detail["id"])

    created = service.create_note(
        application_id,
        ApplicationNoteCreate(
            body="Ask about platform ownership.",
            note_type="recruiter",
        ),
    )
    assert created["note_type"] == "recruiter"
    assert created["body"] == "Ask about platform ownership."
    assert service.get_application(application_id)["counts"]["notes"] == 1

    notes = service.list_notes(application_id)
    assert [note["id"] for note in notes] == [created["id"]]

    updated = service.update_note(
        application_id,
        created["id"],
        ApplicationNoteUpdate(
            body="Ask about platform ownership and scope.",
            note_type="follow_up",
        ),
    )
    assert updated["note_type"] == "follow_up"
    assert updated["body"] == "Ask about platform ownership and scope."

    service.delete_note(application_id, created["id"])
    deleted_note = db_session.get(ApplicationNote, created["id"])
    assert deleted_note is not None
    assert deleted_note.deleted_at is not None
    assert service.list_notes(application_id) == []
    assert service.get_application(application_id)["counts"]["notes"] == 0
    with pytest.raises(ApplicationWorkflowNotFoundError):
        service.update_note(
            application_id,
            created["id"],
            ApplicationNoteUpdate(body="Should not update deleted notes."),
        )

    actions = list(
        db_session.scalars(
            select(ActivityLog.action).where(ActivityLog.entity_id == application_id)
        )
    )
    assert "application.note.created" in actions
    assert "application.note.updated" in actions
    assert "application.note.deleted" in actions



def test_service_interview_stage_crud_completion_cancel_and_suggestion(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session, status="applied")
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)
    application_id = UUID(detail["id"])

    created = service.create_interview_stage(
        application_id,
        ApplicationInterviewStageCreate(
            stage_type="technical",
            title="Technical interview",
            scheduled_at="2026-05-20T15:00:00Z",
            interviewer_names=["Ada Lovelace", ""],
            location_or_meeting_link="https://meet.example.com/tech",
            preparation_notes="Review architecture notes.",
            metadata={"source": "manual"},
        ),
    )

    assert created["status"] == "scheduled"
    assert created["interviewer_names"] == ["Ada Lovelace"]
    assert created["state_transition_suggestion"] == "interviewing"
    assert service.get_application(application_id)["current_state"] == "applied"
    assert service.get_application(application_id)["counts"]["interviews"] == 1

    listed = service.list_interview_stages(application_id)
    assert [stage["id"] for stage in listed] == [created["id"]]

    updated = service.update_interview_stage(
        application_id,
        created["id"],
        ApplicationInterviewStageUpdate(
            title="Technical screen",
            status="planned",
            notes="Bring examples.",
        ),
    )
    assert updated["title"] == "Technical screen"
    assert updated["status"] == "planned"

    completed = service.complete_interview_stage(
        application_id,
        created["id"],
        ApplicationInterviewCompleteRequest(outcome_notes="Advanced to panel."),
    )
    assert completed["status"] == "completed"
    assert completed["completed_at"] is not None
    assert completed["outcome_notes"] == "Advanced to panel."

    canceled = service.create_interview_stage(
        application_id,
        ApplicationInterviewStageCreate(stage_type="panel", title="Panel interview"),
    )
    canceled = service.cancel_interview_stage(
        application_id,
        canceled["id"],
        ApplicationInterviewCancelRequest(outcome_notes="Company rescheduled."),
    )
    assert canceled["status"] == "canceled"
    assert canceled["outcome_notes"] == "Company rescheduled."

    service.delete_interview_stage(application_id, canceled["id"])
    deleted = db_session.get(ApplicationInterviewStage, canceled["id"])
    assert deleted is not None
    assert deleted.deleted_at is not None
    assert [stage["id"] for stage in service.list_interview_stages(application_id)] == [
        created["id"]
    ]

    actions = list(
        db_session.scalars(
            select(ActivityLog.action).where(ActivityLog.entity_id == application_id)
        )
    )
    assert "application.interview_stage.created" in actions
    assert "application.interview_stage.updated" in actions
    assert "application.interview_stage.completed" in actions
    assert "application.interview_stage.canceled" in actions
    assert "application.interview_stage.deleted" in actions


def test_service_interview_validation_timeline_and_scoping(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    service = ApplicationWorkflowService(db_session)
    first = service.get_or_create_for_role(create_role(db_session, title="First").id)
    second = service.get_or_create_for_role(create_role(db_session, title="Second").id)
    first_id = UUID(first["id"])
    second_id = UUID(second["id"])

    created = service.create_interview_stage(
        first_id,
        ApplicationInterviewStageCreate(
            stage_type="recruiter_screen",
            title="Recruiter screen",
        ),
    )

    with pytest.raises(ApplicationWorkflowNotFoundError):
        service.update_interview_stage(
            second_id,
            created["id"],
            ApplicationInterviewStageUpdate(title="Nope"),
        )

    with pytest.raises(ValueError):
        ApplicationInterviewStageCreate(
            stage_type="technical",
            title="Naive datetime",
            scheduled_at="2026-05-20T15:00:00",
        )

    timeline = service.get_timeline(first_id)
    event_types = [event["event_type"] for event in timeline]
    assert "interview.created" in event_types


def test_service_external_link_crud_uses_soft_delete(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)
    application_id = UUID(detail["id"])

    created = service.create_external_link(
        application_id,
        ApplicationExternalLinkCreate(
            label="Job posting",
            url="https://example.com/jobs/1",
            type="job_posting",
            metadata={"source": "manual"},
        ),
    )
    assert created["label"] == "Job posting"
    assert created["type"] == "job_posting"
    assert created["metadata"] == {"source": "manual"}
    assert service.list_external_links(application_id)[0]["id"] == created["id"]

    updated = service.update_external_link(
        application_id,
        created["id"],
        ApplicationExternalLinkUpdate(
            label="Application portal",
            type="application_portal",
        ),
    )
    assert updated["label"] == "Application portal"
    assert updated["type"] == "application_portal"

    service.delete_external_link(application_id, created["id"])
    deleted_link = db_session.get(ApplicationExternalLink, created["id"])
    assert deleted_link is not None
    assert deleted_link.deleted_at is not None
    assert service.list_external_links(application_id) == []
    with pytest.raises(ApplicationWorkflowNotFoundError):
        service.update_external_link(
            application_id,
            created["id"],
            ApplicationExternalLinkUpdate(label="Should not update deleted links."),
        )

    actions = list(
        db_session.scalars(
            select(ActivityLog.action).where(ActivityLog.entity_id == application_id)
        )
    )
    assert "application.external_link.created" in actions
    assert "application.external_link.updated" in actions
    assert "application.external_link.deleted" in actions


def test_service_notes_links_are_scoped_to_application(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    service = ApplicationWorkflowService(db_session)
    first = service.get_or_create_for_role(create_role(db_session, title="First").id)
    second = service.get_or_create_for_role(create_role(db_session, title="Second").id)
    first_id = UUID(first["id"])
    second_id = UUID(second["id"])
    note = service.create_note(
        first_id,
        ApplicationNoteCreate(body="Private to first application."),
    )
    link = service.create_external_link(
        first_id,
        ApplicationExternalLinkCreate(
            label="First posting",
            url="https://example.com/first",
        ),
    )

    with pytest.raises(ApplicationWorkflowNotFoundError):
        service.update_note(second_id, note["id"], ApplicationNoteUpdate(body="Nope."))
    with pytest.raises(ApplicationWorkflowNotFoundError):
        service.update_external_link(
            second_id,
            link["id"],
            ApplicationExternalLinkUpdate(label="Nope."),
        )


def test_service_timeline_includes_note_link_activity_without_deleted_body(
    db_session: Session,
) -> None:
    seed_local_data(db_session)
    role = create_role(db_session)
    service = ApplicationWorkflowService(db_session)
    detail = service.get_or_create_for_role(role.id)
    application_id = UUID(detail["id"])
    note = service.create_note(
        application_id,
        ApplicationNoteCreate(
            body="Sensitive recruiter note that should not appear after delete.",
            note_type="recruiter",
        ),
    )
    link = service.create_external_link(
        application_id,
        ApplicationExternalLinkCreate(
            label="Recruiter profile",
            url="https://example.com/recruiter",
            type="recruiter_profile",
        ),
    )
    service.update_note(
        application_id,
        note["id"],
        ApplicationNoteUpdate(body="Updated recruiter note."),
    )
    service.update_external_link(
        application_id,
        link["id"],
        ApplicationExternalLinkUpdate(label="Updated recruiter profile."),
    )
    service.delete_note(application_id, note["id"])
    service.delete_external_link(application_id, link["id"])

    timeline = service.get_timeline(application_id)
    event_types = [event["event_type"] for event in timeline]
    assert "note.created" not in event_types
    assert "external_link.created" not in event_types
    assert "note.updated" in event_types
    assert "note.deleted" in event_types
    assert "external_link.updated" in event_types
    assert "external_link.deleted" in event_types
    assert all(
        event["description"] != "Sensitive recruiter note that should not appear after delete."
        for event in timeline
    )


def test_api_application_timeline_and_missing_application(
    application_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(db_session)
    application_id = application_client.post(
        f"/api/roles/{role.id}/application"
    ).json()["id"]

    timeline_response = application_client.get(
        f"/api/applications/{application_id}/timeline"
    )
    assert timeline_response.status_code == 200
    assert "application.created" in [
        event["event_type"] for event in timeline_response.json()
    ]

    missing_response = application_client.get(f"/api/applications/{uuid4()}/timeline")
    assert missing_response.status_code == 404


def test_api_opportunity_application_alias_preserves_role_compatibility(
    application_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(db_session)

    opportunity_response = application_client.post(
        f"/api/opportunities/{role.id}/application"
    )
    role_response = application_client.post(f"/api/roles/{role.id}/application")

    assert opportunity_response.status_code == 201
    assert role_response.status_code == 201
    assert opportunity_response.json()["id"] == role_response.json()["id"]
    assert opportunity_response.json()["role_id"] == str(role.id)


def test_api_interview_stage_crud(
    application_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(db_session, status="applied")
    application_id = application_client.post(
        f"/api/roles/{role.id}/application"
    ).json()["id"]

    create_response = application_client.post(
        f"/api/applications/{application_id}/interviews",
        json={
            "stage_type": "recruiter_screen",
            "title": "Recruiter screen",
            "scheduled_at": "2026-05-20T15:00:00Z",
            "interviewer_names": ["Recruiter One"],
            "location_or_meeting_link": "https://meet.example.com/one",
        },
    )
    assert create_response.status_code == 201
    interview = create_response.json()
    assert interview["status"] == "scheduled"
    assert interview["state_transition_suggestion"] == "interviewing"

    list_response = application_client.get(
        f"/api/applications/{application_id}/interviews"
    )
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [interview["id"]]

    invalid_response = application_client.post(
        f"/api/applications/{application_id}/interviews",
        json={
            "stage_type": "not_real",
            "title": "Invalid",
        },
    )
    assert invalid_response.status_code == 422

    update_response = application_client.patch(
        f"/api/applications/{application_id}/interviews/{interview['id']}",
        json={"title": "Updated recruiter screen", "status": "planned"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated recruiter screen"

    complete_response = application_client.post(
        f"/api/applications/{application_id}/interviews/{interview['id']}/complete",
        json={"outcome_notes": "Moved forward."},
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completed"

    cancel_response = application_client.post(
        f"/api/applications/{application_id}/interviews/{interview['id']}/cancel",
        json={"outcome_notes": "Canceled after completion for test."},
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "canceled"

    delete_response = application_client.delete(
        f"/api/applications/{application_id}/interviews/{interview['id']}"
    )
    assert delete_response.status_code == 204
    assert application_client.get(
        f"/api/applications/{application_id}/interviews"
    ).json() == []


def test_api_note_and_link_crud(
    application_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(db_session)
    application_id = application_client.post(
        f"/api/roles/{role.id}/application"
    ).json()["id"]

    note_create_response = application_client.post(
        f"/api/applications/{application_id}/notes",
        json={"body": "Ask about team scope.", "note_type": "recruiter"},
    )
    assert note_create_response.status_code == 201
    note = note_create_response.json()
    assert note["note_type"] == "recruiter"

    note_list_response = application_client.get(
        f"/api/applications/{application_id}/notes"
    )
    assert note_list_response.status_code == 200
    assert [item["id"] for item in note_list_response.json()] == [note["id"]]

    note_update_response = application_client.patch(
        f"/api/applications/{application_id}/notes/{note['id']}",
        json={"body": "Ask about team scope and roadmap.", "note_type": "follow_up"},
    )
    assert note_update_response.status_code == 200
    assert note_update_response.json()["note_type"] == "follow_up"

    link_create_response = application_client.post(
        f"/api/applications/{application_id}/links",
        json={
            "label": "Job posting",
            "url": "https://example.com/jobs/1",
            "type": "job_posting",
            "metadata": {"source": "manual"},
        },
    )
    assert link_create_response.status_code == 201
    link = link_create_response.json()
    assert link["type"] == "job_posting"

    invalid_link_response = application_client.post(
        f"/api/applications/{application_id}/links",
        json={"label": "Broken", "url": "not-a-url"},
    )
    assert invalid_link_response.status_code == 422

    link_list_response = application_client.get(
        f"/api/applications/{application_id}/links"
    )
    assert link_list_response.status_code == 200
    assert [item["id"] for item in link_list_response.json()] == [link["id"]]

    link_update_response = application_client.patch(
        f"/api/applications/{application_id}/links/{link['id']}",
        json={"label": "Application portal", "type": "application_portal"},
    )
    assert link_update_response.status_code == 200
    assert link_update_response.json()["label"] == "Application portal"

    note_delete_response = application_client.delete(
        f"/api/applications/{application_id}/notes/{note['id']}"
    )
    link_delete_response = application_client.delete(
        f"/api/applications/{application_id}/links/{link['id']}"
    )
    assert note_delete_response.status_code == 204
    assert link_delete_response.status_code == 204
    assert application_client.get(
        f"/api/applications/{application_id}/notes"
    ).json() == []
    assert application_client.get(
        f"/api/applications/{application_id}/links"
    ).json() == []


def test_api_list_detail_ensure_filter_and_update(
    application_client: TestClient,
    db_session: Session,
) -> None:
    other_workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(title="Leadership Search")
    )
    default_role = create_role(db_session, company_name="Default API Co")
    other_role = create_role(
        db_session,
        company_name="Other API Co",
        workspace_id=other_workspace.id,
    )

    default_response = application_client.post(f"/api/roles/{default_role.id}/application")
    duplicate_response = application_client.post(f"/api/roles/{default_role.id}/application")
    other_response = application_client.post(f"/api/roles/{other_role.id}/application")

    assert default_response.status_code == 201
    assert duplicate_response.status_code == 201
    assert default_response.json()["id"] == duplicate_response.json()["id"]
    assert other_response.status_code == 201

    list_response = application_client.get("/api/applications")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    filtered_response = application_client.get(
        "/api/applications",
        params={"workspace_id": str(DEFAULT_WORKSPACE_ID)},
    )
    assert filtered_response.status_code == 200
    assert [item["role_id"] for item in filtered_response.json()] == [
        str(default_role.id)
    ]

    workspace_response = application_client.get(
        f"/api/workspaces/{other_workspace.id}/applications"
    )
    assert workspace_response.status_code == 200
    assert [item["role_id"] for item in workspace_response.json()] == [
        str(other_role.id)
    ]

    application_id = default_response.json()["id"]
    detail_response = application_client.get(f"/api/applications/{application_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["role"]["company"]["name"] == "Default API Co"
    assert detail_response.json()["application_state"]["currentState"] == "discovered"
    assert detail_response.json()["available_next_states"] == [
        "interested",
        "withdrawn",
        "archived",
    ]

    update_response = application_client.patch(
        f"/api/applications/{application_id}",
        json={
            "workflow_metadata": {"priority": "medium"},
            "next_action_at": "2026-05-20T15:00:00Z",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["workflow_metadata"]["priority"] == "medium"
    assert update_response.json()["next_action_at"] is not None


def test_api_transition_validation_and_pipeline(
    application_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(db_session)
    application_id = application_client.post(
        f"/api/roles/{role.id}/application"
    ).json()["id"]

    invalid_response = application_client.post(
        f"/api/applications/{application_id}/state-transitions",
        json={"state": "offer", "reason": "Invalid jump."},
    )
    assert invalid_response.status_code == 409

    transition_response = application_client.post(
        f"/api/applications/{application_id}/transition",
        json={"state": "interested", "reason": "Worth pursuing."},
    )
    assert transition_response.status_code == 200
    assert transition_response.json()["current_state"] == "interested"

    pipeline_response = application_client.get("/api/applications/pipeline")
    assert pipeline_response.status_code == 200
    pipeline = pipeline_response.json()
    assert pipeline["include_inactive"] is False
    assert [item["id"] for item in pipeline["states"]["interested"]] == [
        application_id
    ]
    assert "archived" not in pipeline["states"]


def test_api_workspace_scope_and_inactive_filtering(
    application_client: TestClient,
    db_session: Session,
) -> None:
    role = create_role(db_session)
    application = application_client.post(f"/api/roles/{role.id}/application").json()
    application_id = application["id"]

    archive_response = application_client.post(
        f"/api/applications/{application_id}/state-transitions",
        json={"state": "archived", "reason": "Closed."},
    )
    assert archive_response.status_code == 200

    active_response = application_client.get("/api/applications")
    assert active_response.status_code == 200
    assert active_response.json() == []

    inactive_response = application_client.get(
        "/api/applications",
        params={"include_inactive": True},
    )
    assert inactive_response.status_code == 200
    assert [item["id"] for item in inactive_response.json()] == [application_id]

    missing_workspace_response = application_client.get(
        "/api/applications",
        params={"workspace_id": str(uuid4())},
    )
    assert missing_workspace_response.status_code == 404


def test_archived_workspace_rejects_new_application_workflow(
    application_client: TestClient,
    db_session: Session,
) -> None:
    workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(title="Archive Test Workspace")
    )
    role = create_role(db_session, workspace_id=workspace.id)
    WorkspaceService(db_session).archive_workspace(workspace.id)

    response = application_client.post(f"/api/roles/{role.id}/application")

    assert response.status_code == 409
    assert db_session.scalar(select(Application).where(Application.role_id == role.id)) is None


def test_service_not_found_and_seed_missing_errors(db_session: Session) -> None:
    seed_local_data(db_session)
    service = ApplicationWorkflowService(db_session)
    with pytest.raises(ApplicationWorkflowNotFoundError):
        service.get_application(uuid4())

    user = db_session.get(User, DEFAULT_LOCAL_USER_ID)
    assert user is not None
    user.deleted_at = datetime.now(timezone.utc)
    db_session.commit()
    with pytest.raises(ApplicationWorkflowSeedMissingError):
        service.list_applications()


def test_service_rejects_inactive_workspace(db_session: Session) -> None:
    seed_local_data(db_session)
    workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(title="Inactive Workspace")
    )
    role = create_role(db_session, workspace_id=workspace.id)
    WorkspaceService(db_session).archive_workspace(workspace.id)

    with pytest.raises(ApplicationWorkflowWorkspaceInactiveError):
        ApplicationWorkflowService(db_session).get_or_create_for_role(role.id)
