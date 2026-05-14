import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.resume_artifacts import ResumeArtifactGenerateRequest
from app.services.resume_artifacts import (
    ResumeArtifactEvaluationNotFoundError,
    ResumeArtifactProviderError,
    ResumeArtifactRoleNotFoundError,
    ResumeArtifactSeedMissingError,
    ResumeArtifactService,
    ResumeArtifactSourceNotFoundError,
    ResumeArtifactUnavailableError,
    ResumeArtifactValidationError,
)

router = APIRouter(tags=["resume-artifacts"])


def get_resume_artifact_service(db: Session = Depends(get_db)) -> ResumeArtifactService:
    return ResumeArtifactService(db)


@router.post(
    "/roles/{role_id}/resume-artifacts",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
def generate_resume_artifact(
    role_id: uuid.UUID,
    payload: ResumeArtifactGenerateRequest,
    service: ResumeArtifactService = Depends(get_resume_artifact_service),
):
    try:
        return service.generate_for_role(role_id=role_id, payload=payload)
    except (
        ResumeArtifactRoleNotFoundError,
        ResumeArtifactEvaluationNotFoundError,
        ResumeArtifactSourceNotFoundError,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ResumeArtifactSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ResumeArtifactUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except (ResumeArtifactValidationError, ResumeArtifactProviderError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
