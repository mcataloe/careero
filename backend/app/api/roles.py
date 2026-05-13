import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.roles import RoleCreate, RoleResponse, RoleUpdate
from app.services.roles import (
    RoleDependencyNotFoundError,
    RoleNotFoundError,
    RoleSeedMissingError,
    RoleService,
)

router = APIRouter(prefix="/roles", tags=["roles"])


def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    return RoleService(db)


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate,
    service: RoleService = Depends(get_role_service),
):
    try:
        return service.create_role(payload)
    except RoleDependencyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except RoleSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("", response_model=list[RoleResponse])
def list_roles(service: RoleService = Depends(get_role_service)):
    try:
        return service.list_roles()
    except RoleSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: uuid.UUID,
    service: RoleService = Depends(get_role_service),
):
    try:
        return service.get_role(role_id)
    except RoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except RoleSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: uuid.UUID,
    payload: RoleUpdate,
    service: RoleService = Depends(get_role_service),
):
    try:
        return service.update_role(role_id, payload)
    except (RoleNotFoundError, RoleDependencyNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except RoleSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_role(
    role_id: uuid.UUID,
    service: RoleService = Depends(get_role_service),
):
    try:
        service.archive_role(role_id)
    except RoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except RoleSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
