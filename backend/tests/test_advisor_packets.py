from collections.abc import Generator
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import create_app
from app.models import (
    Application,
    ApplicationExternalLink,
    ApplicationNote,
    GeneratedArtifact,
    StrideEvaluation,
)
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.seed import seed_local_data
from app.services.applications import ApplicationWorkflowService
from app.services.roles import RoleService


@pytest.fixture
def advisor_packet_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def create_application_with_private_inputs(db_session: Session) -> Application:
    role = RoleService(db_session).create_role(
        RoleCreate(
            title="Staff Platform Engineer",
            company=CompanyLookup(name="Packet Co"),
            source=SourceLookup(source_type="manual"),
            job_url="https://example.com/private-job",
            location="Remote",
            remote_type="remote",
            compensation_min=Decimal("180000.00"),
            compensation_max=Decimal("220000.00"),
            compensation_currency="USD",
            raw_description="Private raw job description with hidden keywords.",
            normalized_description="Build internal platform systems.",
        )
    )
    application_detail = ApplicationWorkflowService(db_session).get_or_create_for_role(
        role.id
    )
    application = db_session.get(Application, UUID(str(application_detail["id"])))
    assert application is not None
    db_session.add_all(
        [
            ApplicationNote(
                application_id=application.id,
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                author="Local User",
                note_type="compensation",
                body="Private negotiation note: ask for 220k minimum.",
            ),
            ApplicationExternalLink(
                application_id=application.id,
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                label="Recruiter profile",
                url="https://example.com/recruiter/private",
                link_type="recruiter_profile",
            ),
            StrideEvaluation(
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                role_id=application.role_id,
                evaluation_status="completed",
                overall_score=Decimal("88.50"),
                recommendation="apply",
                confidence_level="high",
                summary="Private STRIDE summary with ATS risk notes.",
            ),
            GeneratedArtifact(
                id=uuid4(),
                user_id=application.user_id,
                workspace_id=application.workspace_id,
                role_id=application.role_id,
                artifact_type="cover_letter",
                title="Packet Co Cover Letter",
                content="Private generated artifact content.",
                artifact_metadata={
                    "contract": {
                        "lifecycleStatus": "draft",
                        "revision": {"revisionNumber": 1},
                    }
                },
            ),
        ]
    )
    db_session.commit()
    return application


def test_advisor_packet_preview_is_local_only_and_redacted_by_default(
    advisor_packet_client: TestClient,
    db_session: Session,
) -> None:
    application = create_application_with_private_inputs(db_session)

    response = advisor_packet_client.get(
        f"/api/applications/{application.id}/advisor-packet"
    )

    assert response.status_code == 200
    packet = response.json()
    assert packet["mode"] == "local_preview"
    assert packet["local_only"] is True
    assert packet["external_sharing_enabled"] is False
    assert packet["opportunity"]["title"] == "Staff Platform Engineer"
    assert packet["opportunity"]["company_name"] == "Packet Co"
    assert packet["application"]["counts"]["notes"] == 1
    assert packet["artifacts"][0]["content_included"] is False
    assert packet["artifacts"][0]["lifecycle_status"] == "draft"

    body = response.text
    assert "Private negotiation note" not in body
    assert "Private raw job description" not in body
    assert "Private STRIDE summary" not in body
    assert "Private generated artifact content" not in body
    assert "https://example.com/recruiter/private" not in body
    assert "Compensation targets and strategy" in body
    assert "STRIDE score and explanation" in body


def test_advisor_packet_markdown_export_is_local_only(
    advisor_packet_client: TestClient,
    db_session: Session,
) -> None:
    application = create_application_with_private_inputs(db_session)

    response = advisor_packet_client.post(
        f"/api/applications/{application.id}/advisor-packet/exports/md"
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert response.headers["x-careero-local-only"] == "true"
    assert response.headers["x-careero-external-sharing"] == "false"
    assert response.headers["x-careero-content-hash"].startswith("sha256:")
    assert b"Advisor Packet Preview: Staff Platform Engineer" in response.content
    assert b"Private negotiation note" not in response.content
    assert b"Private generated artifact content" not in response.content


def test_missing_application_advisor_packet_returns_404(
    advisor_packet_client: TestClient,
) -> None:
    response = advisor_packet_client.get(f"/api/applications/{uuid4()}/advisor-packet")

    assert response.status_code == 404
