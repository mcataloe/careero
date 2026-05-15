from collections.abc import Generator
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.cover_letter_artifacts import get_cover_letter_artifact_service
from app.config import Settings, get_settings
from app.database import get_db
from app.main import create_app
from app.models import ActivityLog, GeneratedArtifact
from app.schemas.cover_letter_artifacts import CoverLetterArtifactGenerateRequest
from app.schemas.resume_sources import ResumeSourceCreate
from app.schemas.roles import CompanyLookup, RoleCreate, SourceLookup
from app.schemas.stride_evaluations import StrideEvaluationCreate
from app.schemas.workspaces import WorkspaceCreate
from app.seed import DEFAULT_WORKSPACE_ID, seed_local_data
from app.services.cover_letter_artifact_ai import (
    CoverLetterArtifactGenerationUnavailableError,
)
from app.services.cover_letter_artifacts import (
    CoverLetterArtifactService,
    CoverLetterArtifactSourceNotFoundError,
    CoverLetterArtifactTruthfulnessError,
    CoverLetterArtifactValidationError,
    CoverLetterArtifactWorkspaceMismatchError,
)
from app.services.resume_sources import ResumeSourceService
from app.services.roles import RoleService
from app.services.stride_evaluations import StrideEvaluationService
from app.services.workspaces import WorkspaceService


WORKSPACE_ID = DEFAULT_WORKSPACE_ID


class FakeCoverLetterGenerator:
    def __init__(
        self,
        *,
        content: str | None = None,
        unsupported_claims: list[str] | None = None,
        unavailable: bool = False,
    ) -> None:
        self.content = content or (
            "I'm writing to be considered for the Senior Platform Engineer role "
            "at Example Co.\n\n"
            "My background includes Python services and PostgreSQL-backed "
            "platform work, and I would welcome the opportunity to discuss the "
            "role's platform priorities."
        )
        self.unsupported_claims = unsupported_claims or []
        self.unavailable = unavailable

    def generate(self, **kwargs) -> dict[str, Any]:
        if self.unavailable:
            raise CoverLetterArtifactGenerationUnavailableError(
                "AI cover letter generation is disabled"
            )
        return {
            "status": "completed",
            "model": "gpt-5-mini",
            "latency_ms": 1,
            "input_token_estimate": 100,
            "output_token_estimate": 50,
            "output": {
                "title": "Example Co cover letter",
                "content": self.content,
                "warnings": [],
                "limitations": [],
                "unsupported_claims": self.unsupported_claims,
            },
        }


@pytest.fixture
def seeded_session(db_session: Session) -> Session:
    seed_local_data(db_session)
    return db_session


@pytest.fixture
def cover_letter_api_client(
    seeded_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("CAREERO_ENABLE_AI_COVER_LETTER_GENERATION", "false")
    monkeypatch.setenv("CAREERO_OPENAI_API_KEY", "")
    get_settings.cache_clear()
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield seeded_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def cover_letter_api_client_with_fake_generator(
    seeded_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("CAREERO_ENABLE_AI_COVER_LETTER_GENERATION", "false")
    monkeypatch.setenv("CAREERO_OPENAI_API_KEY", "")
    get_settings.cache_clear()
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield seeded_session

    def override_service() -> CoverLetterArtifactService:
        return CoverLetterArtifactService(
            seeded_session,
            settings=Settings(_env_file=None),
            generator=FakeCoverLetterGenerator(),
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cover_letter_artifact_service] = override_service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def create_role(db_session: Session):
    return RoleService(db_session).create_role(
        RoleCreate(
            title="Senior Platform Engineer",
            company=CompanyLookup(
                name="Example Co",
                website_url="https://example.com",
            ),
            source=SourceLookup(source_type="manual"),
            job_url="https://example.com/jobs/platform",
            location="Chicago, IL",
            remote_type="hybrid",
            raw_description="Build Python and PostgreSQL platforms for internal teams.",
            normalized_description="Senior platform role using Python and PostgreSQL.",
            status="found",
        )
    )


def create_source(db_session: Session, *, is_active: bool = True) -> dict[str, Any]:
    return ResumeSourceService(db_session).create_source(
        ResumeSourceCreate(
            name="Master Resume",
            source_type="master_resume",
            version_label="v1",
            raw_text="Built Python services and PostgreSQL-backed platforms.",
            normalized_summary="Backend platform engineer.",
            is_active=is_active,
        )
    )


def create_evaluation(db_session: Session, role_id: UUID):
    result = StrideEvaluationService(
        db_session,
        settings=Settings(_env_file=None),
    ).create_for_role(
        role_id=role_id,
        payload=StrideEvaluationCreate(
            user_context={"target_keywords": ["python", "postgresql", "kubernetes"]},
            force=True,
        ),
    )
    return result.evaluation


def generate_artifact(
    db_session: Session,
    *,
    role_id: UUID,
    generator: FakeCoverLetterGenerator | None = None,
    evaluation_id: UUID | None = None,
    source_version_id: UUID | None = None,
    tone: str = "direct",
    workspace_id: UUID = WORKSPACE_ID,
) -> dict[str, Any]:
    service = CoverLetterArtifactService(
        db_session,
        settings=Settings(_env_file=None),
        generator=generator or FakeCoverLetterGenerator(),
    )
    return service.generate_for_role(
        role_id=role_id,
        payload=CoverLetterArtifactGenerateRequest(
            workspace_id=workspace_id,
            evaluation_id=evaluation_id,
            source_version_id=source_version_id,
            tone=tone,
        ),
    )


def test_service_creates_and_persists_valid_cover_letter_artifact(
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)
    source = create_source(seeded_session)
    evaluation = create_evaluation(seeded_session, role.id)

    artifact = generate_artifact(
        seeded_session,
        role_id=role.id,
        evaluation_id=evaluation.id,
    )

    assert artifact["contractVersion"] == "careero.contracts.v1"
    assert artifact["workspaceId"] == str(WORKSPACE_ID)
    assert artifact["opportunityId"] == str(role.id)
    assert artifact["tone"] == "direct"
    assert "I'm excited to apply" not in artifact["content"]
    assert artifact["generationMetadata"]["generatedBy"] == "ai"
    assert artifact["generationMetadata"]["modelMetadata"]["model"] == "gpt-5-mini"
    assert str(source["active_version"]["id"]) in artifact["generationMetadata"][
        "groundingSourceIds"
    ]
    assert artifact["metadata"]["targetEvaluationId"] == str(evaluation.id)
    assert artifact["metadata"]["sourceResume"]["version_id"] == str(
        source["active_version"]["id"]
    )
    assert artifact["editHistory"] == []
    assert artifact["exportMetadata"] == []
    assert artifact["revision"]["revisionNumber"] == 1

    persisted = seeded_session.get(GeneratedArtifact, UUID(artifact["id"]))
    assert persisted is not None
    assert persisted.role_id == role.id
    assert persisted.artifact_type == "cover_letter"
    assert persisted.artifact_metadata["contract"]["id"] == artifact["id"]
    assert persisted.artifact_metadata["target_evaluation_id"] == str(evaluation.id)


def test_api_generates_cover_letter_artifact_with_expected_links(
    cover_letter_api_client_with_fake_generator: TestClient,
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)
    create_source(seeded_session)
    evaluation = create_evaluation(seeded_session, role.id)

    response = cover_letter_api_client_with_fake_generator.post(
        f"/api/roles/{role.id}/cover-letter-artifacts",
        json={
            "workspace_id": str(WORKSPACE_ID),
            "evaluation_id": str(evaluation.id),
        },
    )

    assert response.status_code == 201
    artifact = response.json()
    assert artifact["workspaceId"] == str(WORKSPACE_ID)
    assert artifact["opportunityId"] == str(role.id)
    assert artifact["metadata"]["targetEvaluationId"] == str(evaluation.id)
    assert artifact["tone"] == "direct"
    assert artifact["revision"]["revisionNumber"] == 1


def test_missing_stride_evaluation_succeeds_with_warning(
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)
    create_source(seeded_session)

    artifact = generate_artifact(seeded_session, role_id=role.id)

    assert artifact["metadata"]["targetEvaluationId"] is None
    assert "Generated without a STRIDE evaluation." in artifact[
        "generationMetadata"
    ]["warnings"]


def test_missing_source_succeeds_with_empty_grounding_and_warning(
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)
    create_evaluation(seeded_session, role.id)

    artifact = generate_artifact(
        seeded_session,
        role_id=role.id,
        generator=FakeCoverLetterGenerator(
            content=(
                "I'm writing to be considered for the Senior Platform Engineer "
                "role at Example Co."
            )
        ),
    )

    assert artifact["metadata"]["sourceResume"] is None
    assert artifact["generationMetadata"]["groundingSourceIds"] == []
    assert "Generated without a resume/profile source." in artifact[
        "generationMetadata"
    ]["warnings"]


def test_explicit_missing_source_returns_error_without_persisting(
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)

    with pytest.raises(CoverLetterArtifactSourceNotFoundError):
        generate_artifact(
            seeded_session,
            role_id=role.id,
            source_version_id=uuid4(),
        )

    assert seeded_session.query(GeneratedArtifact).count() == 0


def test_validation_failure_rolls_back_and_logs_failure(
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)
    create_source(seeded_session)

    with pytest.raises(CoverLetterArtifactValidationError):
        generate_artifact(
            seeded_session,
            role_id=role.id,
            generator=FakeCoverLetterGenerator(unsupported_claims=["Invented AWS work"]),
        )

    assert seeded_session.query(GeneratedArtifact).count() == 0
    actions = list(
        seeded_session.scalars(
            select(ActivityLog.action).where(
                ActivityLog.entity_type == "cover_letter_artifact",
            )
        )
    )
    assert "cover_letter_artifact.failed" in actions


def test_banned_enthusiastic_opening_is_rejected(
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)
    create_source(seeded_session)

    with pytest.raises(CoverLetterArtifactValidationError):
        generate_artifact(
            seeded_session,
            role_id=role.id,
            generator=FakeCoverLetterGenerator(
                content="I'm excited to apply for the Senior Platform Engineer role."
            ),
        )


def test_missing_keyword_not_supported_by_source_is_rejected(
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)
    create_source(seeded_session)
    create_evaluation(seeded_session, role.id)

    with pytest.raises(CoverLetterArtifactTruthfulnessError):
        generate_artifact(
            seeded_session,
            role_id=role.id,
            generator=FakeCoverLetterGenerator(
                content=(
                    "I'm writing to be considered for the role. My background "
                    "includes Kubernetes, Python, and PostgreSQL platform work."
                )
            ),
        )

    assert seeded_session.query(GeneratedArtifact).count() == 0


def test_revision_lineage_increments_for_same_workspace_and_role(
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)
    create_source(seeded_session)

    first = generate_artifact(seeded_session, role_id=role.id)
    second = generate_artifact(seeded_session, role_id=role.id)

    assert first["revision"]["revisionNumber"] == 1
    assert second["revision"]["revisionNumber"] == 2
    assert second["revision"]["parentArtifactId"] == first["id"]


def test_api_returns_503_when_ai_cover_letter_generation_is_disabled(
    cover_letter_api_client: TestClient,
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)

    response = cover_letter_api_client.post(
        f"/api/roles/{role.id}/cover-letter-artifacts",
        json={"workspace_id": str(WORKSPACE_ID)},
    )

    assert response.status_code == 503
    assert seeded_session.query(GeneratedArtifact).count() == 0


def test_invalid_role_or_explicit_evaluation_returns_404(
    cover_letter_api_client: TestClient,
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)

    missing_role_response = cover_letter_api_client.post(
        f"/api/roles/{uuid4()}/cover-letter-artifacts",
        json={"workspace_id": str(WORKSPACE_ID)},
    )
    missing_evaluation_response = cover_letter_api_client.post(
        f"/api/roles/{role.id}/cover-letter-artifacts",
        json={
            "workspace_id": str(WORKSPACE_ID),
            "evaluation_id": str(uuid4()),
        },
    )

    assert missing_role_response.status_code == 404
    assert missing_evaluation_response.status_code == 404


def test_role_workspace_mismatch_is_rejected(
    seeded_session: Session,
) -> None:
    role = create_role(seeded_session)
    create_source(seeded_session)
    other_workspace = WorkspaceService(seeded_session).create_workspace(
        WorkspaceCreate(title="Other active search")
    )

    with pytest.raises(CoverLetterArtifactWorkspaceMismatchError):
        generate_artifact(
            seeded_session,
            role_id=role.id,
            workspace_id=other_workspace.id,
        )
