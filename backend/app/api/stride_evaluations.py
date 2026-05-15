import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.constants import StrideEvaluationStatus
from app.database import get_db
from app.schemas.stride_evaluations import (
    StrideEvaluationCreate,
    StrideEvaluationResponse,
)
from app.services.stride_evaluations import (
    StrideEvaluationNotFoundError,
    StrideEvaluationRoleNotFoundError,
    StrideEvaluationSeedMissingError,
    StrideEvaluationService,
    StrideEvaluationWorkspaceInactiveError,
)

router = APIRouter(tags=["stride-evaluations"])


def get_stride_evaluation_service(
    db: Session = Depends(get_db),
) -> StrideEvaluationService:
    return StrideEvaluationService(db)


@router.post(
    "/roles/{role_id}/evaluations",
    response_model=StrideEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_stride_evaluation(
    role_id: uuid.UUID,
    response: Response,
    payload: StrideEvaluationCreate | None = None,
    service: StrideEvaluationService = Depends(get_stride_evaluation_service),
):
    try:
        result = service.create_for_role(
            role_id=role_id,
            payload=payload or StrideEvaluationCreate(),
        )
        if result.reused_cache:
            response.status_code = status.HTTP_200_OK
        return result.evaluation
    except StrideEvaluationRoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except StrideEvaluationWorkspaceInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except StrideEvaluationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/roles/{role_id}/evaluations/latest",
    response_model=StrideEvaluationResponse,
)
def get_latest_stride_evaluation(
    role_id: uuid.UUID,
    service: StrideEvaluationService = Depends(get_stride_evaluation_service),
):
    try:
        return service.get_latest_for_role(role_id=role_id)
    except (StrideEvaluationRoleNotFoundError, StrideEvaluationNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except StrideEvaluationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/stride-evaluations", response_model=list[StrideEvaluationResponse])
def list_stride_evaluations(
    role_id: uuid.UUID | None = None,
    evaluation_status: StrideEvaluationStatus | None = None,
    service: StrideEvaluationService = Depends(get_stride_evaluation_service),
):
    try:
        return service.list_evaluations(
            role_id=role_id,
            evaluation_status=evaluation_status,
        )
    except StrideEvaluationRoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except StrideEvaluationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/stride-evaluations/{evaluation_id}",
    response_model=StrideEvaluationResponse,
)
def get_stride_evaluation(
    evaluation_id: uuid.UUID,
    service: StrideEvaluationService = Depends(get_stride_evaluation_service),
):
    try:
        return service.get_by_id(evaluation_id)
    except StrideEvaluationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except StrideEvaluationSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
