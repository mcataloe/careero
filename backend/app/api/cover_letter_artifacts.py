import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.cover_letter_artifacts import CoverLetterArtifactGenerateRequest
from app.services.cover_letter_artifacts import (
    CoverLetterArtifactEvaluationNotFoundError,
    CoverLetterArtifactProviderError,
    CoverLetterArtifactRoleNotFoundError,
    CoverLetterArtifactSeedMissingError,
    CoverLetterArtifactService,
    CoverLetterArtifactSourceNotFoundError,
    CoverLetterArtifactUnavailableError,
    CoverLetterArtifactValidationError,
    CoverLetterArtifactWorkspaceInactiveError,
    CoverLetterArtifactWorkspaceMismatchError,
    CoverLetterArtifactWorkspaceNotFoundError,
)

router = APIRouter(tags=["cover-letter-artifacts"])


def get_cover_letter_artifact_service(
    db: Session = Depends(get_db),
) -> CoverLetterArtifactService:
    return CoverLetterArtifactService(db)


@router.post(
    "/roles/{role_id}/cover-letter-artifacts",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
def generate_cover_letter_artifact(
    role_id: uuid.UUID,
    payload: CoverLetterArtifactGenerateRequest,
    service: CoverLetterArtifactService = Depends(get_cover_letter_artifact_service),
):
    try:
        return service.generate_for_role(role_id=role_id, payload=payload)
    except (
        CoverLetterArtifactRoleNotFoundError,
        CoverLetterArtifactEvaluationNotFoundError,
        CoverLetterArtifactSourceNotFoundError,
        CoverLetterArtifactWorkspaceMismatchError,
        CoverLetterArtifactWorkspaceNotFoundError,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except CoverLetterArtifactSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except CoverLetterArtifactUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except CoverLetterArtifactWorkspaceInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except (CoverLetterArtifactValidationError, CoverLetterArtifactProviderError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
