from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import create_app
from app.models import GeneratedArtifact
from app.seed import DEFAULT_LOCAL_USER_ID, DEFAULT_WORKSPACE_ID, seed_local_data
from app.services.artifact_exports import (
    ArtifactExportDependencyError,
    ArtifactExportService,
)


@pytest.fixture
def artifact_export_client(db_session: Session) -> Generator[TestClient, None, None]:
    seed_local_data(db_session)
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def create_generated_artifact(db_session: Session) -> GeneratedArtifact:
    artifact = GeneratedArtifact(
        id=uuid4(),
        user_id=DEFAULT_LOCAL_USER_ID,
        workspace_id=DEFAULT_WORKSPACE_ID,
        role_id=None,
        artifact_type="cover_letter",
        title="Example Co Cover Letter",
        content=(
            "# Example Co Cover Letter\n\n"
            "I'm writing to be considered for the Senior Platform Engineer role.\n\n"
            "- Python services\n"
            "- PostgreSQL platforms\n"
        ),
        artifact_metadata={
            "contract": {
                "id": "contract-id",
                "exportMetadata": [],
            }
        },
    )
    db_session.add(artifact)
    db_session.commit()
    return artifact


def test_markdown_export_returns_file_and_records_metadata(
    artifact_export_client: TestClient,
    db_session: Session,
) -> None:
    artifact = create_generated_artifact(db_session)

    response = artifact_export_client.post(f"/api/artifacts/{artifact.id}/exports/md")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert response.headers["x-careero-content-hash"].startswith("sha256:")
    assert b"Senior Platform Engineer" in response.content

    db_session.refresh(artifact)
    contract = artifact.artifact_metadata["contract"]
    assert contract["exportMetadata"][0]["format"] == "md"
    assert contract["exportMetadata"][0]["fileName"] == "example-co-cover-letter.md"
    assert artifact.artifact_metadata["export_history"][0]["externalMutation"] is False


def test_docx_and_pdf_exports_use_same_stored_artifact_content(
    artifact_export_client: TestClient,
    db_session: Session,
) -> None:
    artifact = create_generated_artifact(db_session)

    docx_response = artifact_export_client.post(
        f"/api/artifacts/{artifact.id}/exports/docx"
    )
    pdf_response = artifact_export_client.post(
        f"/api/artifacts/{artifact.id}/exports/pdf"
    )

    assert docx_response.status_code == 200
    assert docx_response.content.startswith(b"PK")
    assert pdf_response.status_code == 200
    assert pdf_response.content.startswith(b"%PDF-1.4")

    db_session.refresh(artifact)
    formats = [
        item["format"]
        for item in artifact.artifact_metadata["contract"]["exportMetadata"]
    ]
    assert formats == ["docx", "pdf"]


def test_missing_artifact_export_returns_404(
    artifact_export_client: TestClient,
) -> None:
    response = artifact_export_client.post(f"/api/artifacts/{uuid4()}/exports/md")

    assert response.status_code == 404


def test_docx_dependency_failure_does_not_corrupt_export_metadata(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed_local_data(db_session)
    artifact = create_generated_artifact(db_session)

    def fail_docx_import(*, title: str, content: str) -> bytes:
        raise ArtifactExportDependencyError("DOCX export requires python-docx")

    monkeypatch.setattr(
        "app.services.artifact_exports._render_docx",
        fail_docx_import,
    )

    with pytest.raises(ArtifactExportDependencyError):
        ArtifactExportService(db_session).export_artifact(
            artifact_id=artifact.id,
            export_format="docx",
        )

    db_session.refresh(artifact)
    assert artifact.artifact_metadata["contract"]["exportMetadata"] == []
    assert "export_history" not in artifact.artifact_metadata
