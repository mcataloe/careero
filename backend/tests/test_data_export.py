from __future__ import annotations

import json
from collections.abc import Generator
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import get_db
from app.main import create_app
from app.models import User
from app.schemas.applications import ApplicationNoteCreate
from app.schemas.compass_evaluations import CompassEvaluationCreate
from app.schemas.resume_artifacts import ResumeArtifactGenerateRequest
from app.schemas.resume_sources import ResumeSourceCreate
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.schemas.workspaces import WorkspaceCreate
from app.seed import seed_default_job_sources, seed_local_data
from app.services.applications import ApplicationWorkflowService
from app.services.compass_evaluations import CompassEvaluationService
from app.services.current_user import CurrentUserContext
from app.services.data_export import LocalDataExportService
from app.services.resume_artifacts import ResumeArtifactService
from app.services.resume_sources import ResumeSourceService
from app.services.roles import RoleService
from app.services.workspaces import WorkspaceService


class FakeResumeGenerator:
    def generate(self, **kwargs):
        return {
            "status": "completed",
            "model": "gpt-5-mini",
            "latency_ms": 1,
            "input_token_estimate": 100,
            "output_token_estimate": 50,
            "output": {
                "title": "Example tailored resume",
                "content": "Built Python services and PostgreSQL platforms.",
                "tailoring_notes": "Use source-supported platform work.",
                "warnings": [],
                "limitations": [],
                "unsupported_claims": [],
            },
        }


def _seed_representative_data(db_session: Session):
    user, _ = seed_local_data(db_session)
    role = RoleService(db_session).create_role(
        RoleCreate(
            title="Senior Platform Engineer",
            company=CompanyLookup(name="Example Co"),
            source=SourceLookup(source_type="manual"),
            raw_description="Build Python and PostgreSQL platforms.",
            normalized_description="Senior platform role.",
            status="found",
        )
    )
    source = ResumeSourceService(db_session).create_source(
        ResumeSourceCreate(
            name="Master Resume",
            source_type="master_resume",
            version_label="v1",
            raw_text="Built Python services and PostgreSQL platforms.",
            normalized_summary="Backend platform engineer.",
            is_active=True,
        )
    )
    evaluation = CompassEvaluationService(
        db_session,
        settings=Settings(_env_file=None),
    ).create_for_role(role_id=role.id, payload=CompassEvaluationCreate(force=True))
    artifact = ResumeArtifactService(
        db_session,
        settings=Settings(_env_file=None),
        generator=FakeResumeGenerator(),
    ).generate_for_role(
        role_id=role.id,
        payload=ResumeArtifactGenerateRequest(
            workspace_id=role.workspace_id,
            evaluation_id=evaluation.evaluation.id,
            source_version_id=source["active_version"]["id"],
        ),
    )
    application = ApplicationWorkflowService(db_session).get_or_create_for_role(role.id)
    ApplicationWorkflowService(db_session).create_note(
        application["id"],
        ApplicationNoteCreate(body="Private follow-up note."),
    )
    return user, role, artifact


def test_export_endpoint_returns_stable_local_json(db_session: Session) -> None:
    _seed_representative_data(db_session)
    app = create_app(Settings(_env_file=None, environment="local"))

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        response = client.get("/api/data-export/local")

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {
        "metadata",
        "workspaces",
        "companies",
        "job_sources",
        "opportunities",
        "resume_sources",
        "resume_source_versions",
        "compass_evaluations",
        "generated_artifacts",
        "artifact_performance_records",
        "applications",
        "application_state_history",
        "notes",
        "reminders",
        "external_links",
        "interview_stages",
        "activity_logs",
        "automation_suggestions",
        "automation_approval_logs",
    }
    assert body["metadata"]["schema_version"] == "careero.local_data_export.v1"
    assert body["metadata"]["current_user"]["email"] == "local-user@careero.local"
    assert body["opportunities"][0]["raw_description"] == (
        "Build Python and PostgreSQL platforms."
    )
    assert body["resume_source_versions"][0]["raw_text"] == (
        "Built Python services and PostgreSQL platforms."
    )
    assert body["generated_artifacts"][0]["content"]
    assert body["notes"][0]["body"] == "Private follow-up note."


def test_export_is_scoped_to_current_user(db_session: Session) -> None:
    user, role, _artifact = _seed_representative_data(db_session)
    other_user = User(
        id=uuid4(),
        email="other-user@careero.local",
        display_name="Other User",
    )
    db_session.add(other_user)
    db_session.commit()
    seed_default_job_sources(db_session, other_user)
    other_context = CurrentUserContext(
        user_id=other_user.id,
        email=other_user.email,
        display_name=other_user.display_name,
        mode="test",
    )
    other_workspace = WorkspaceService(
        db_session,
        current_user_context=other_context,
    ).create_workspace(WorkspaceCreate(title="Other workspace"))
    RoleService(db_session, current_user_context=other_context).create_role(
        RoleCreate(
            workspace_id=other_workspace.id,
            title="Other private opportunity",
            company=CompanyLookup(name="Other Co"),
            source=SourceLookup(source_type="manual"),
        )
    )

    export = LocalDataExportService(db_session).build_export()
    serialized = export.model_dump_json()

    assert str(user.id) in serialized
    assert str(role.id) in serialized
    assert "Other private opportunity" not in serialized
    assert str(other_user.id) not in serialized


def test_export_does_not_include_runtime_secrets(db_session: Session) -> None:
    _seed_representative_data(db_session)
    export = LocalDataExportService(
        db_session,
        settings=Settings(
            _env_file=None,
            database_url="postgresql://secret_user:secret_pass@localhost/careero",
            openai_api_key="sk-secret-export-test",
        ),
    ).build_export()

    serialized = json.dumps(export.model_dump(mode="json"))
    assert "secret_user" not in serialized
    assert "secret_pass" not in serialized
    assert "sk-secret-export-test" not in serialized
    assert "postgresql://" not in serialized


def test_export_handles_empty_sections(db_session: Session) -> None:
    seed_local_data(db_session)

    export = LocalDataExportService(db_session).build_export()

    assert export.metadata.schema_version == "careero.local_data_export.v1"
    assert export.opportunities == []
    assert export.generated_artifacts == []
    assert export.applications == []
