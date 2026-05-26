import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.constants import CompassEvaluationStatus
from app.database import get_db
from app.schemas.compass_evaluations import (
    CompassEvaluationCreate,
    CompassEvaluationResponse,
)
from app.services.compass_evaluations import (
    CompassEvaluationNotFoundError,
    CompassEvaluationRoleNotFoundError,
    CompassEvaluationSeedMissingError,
    CompassEvaluationService,
    CompassEvaluationWorkspaceInactiveError,
)

router = APIRouter(tags=["compass-evaluations"])


def get_compass_evaluation_service(
    db: Session = Depends(get_db),
) -> CompassEvaluationService:
    return CompassEvaluationService(db)


@router.post(
    "/roles/{role_id}/evaluations",
    response_model=CompassEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_compass_evaluation(
    role_id: uuid.UUID,
    response: Response,
    payload: CompassEvaluationCreate | None = None,
    service: CompassEvaluationService = Depends(get_compass_evaluation_service),
):
    try:
        result = service.create_for_role(
            role_id=role_id,
            payload=payload or CompassEvaluationCreate(),
        )
        if result.reused_cache:
            response.status_code = status.HTTP_200_OK
        return result.evaluation
    except CompassEvaluationRoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except CompassEvaluationWorkspaceInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except CompassEvaluationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/roles/{role_id}/evaluations/latest",
    response_model=CompassEvaluationResponse,
)
def get_latest_compass_evaluation(
    role_id: uuid.UUID,
    service: CompassEvaluationService = Depends(get_compass_evaluation_service),
):
    try:
        return service.get_latest_for_role(role_id=role_id)
    except (CompassEvaluationRoleNotFoundError, CompassEvaluationNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except CompassEvaluationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/compass-evaluations", response_model=list[CompassEvaluationResponse])
def list_compass_evaluations(
    role_id: uuid.UUID | None = None,
    evaluation_status: CompassEvaluationStatus | None = None,
    service: CompassEvaluationService = Depends(get_compass_evaluation_service),
):
    try:
        return service.list_evaluations(
            role_id=role_id,
            evaluation_status=evaluation_status,
        )
    except CompassEvaluationRoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except CompassEvaluationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/compass-evaluations/{evaluation_id}",
    response_model=CompassEvaluationResponse,
)
def get_compass_evaluation(
    evaluation_id: uuid.UUID,
    service: CompassEvaluationService = Depends(get_compass_evaluation_service),
):
    try:
        return service.get_by_id(evaluation_id)
    except CompassEvaluationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except CompassEvaluationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
