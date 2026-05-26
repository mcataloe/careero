import uuid
import time

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ai_usage import AIUsageEventCreate
from app.schemas.role_parsing import RoleParseRequest, RoleParseResponse
from app.services.ai_usage import (
    AIUsageSeedMissingError,
    AIUsageService,
    content_hash,
)
from app.schemas.roles import RoleCreate, RoleResponse, RoleUpdate
from app.services.role_parsing import (
    RoleParsingProviderError,
    RoleParsingService,
    RoleParsingUnavailableError,
    RoleParsingValidationError,
)
from app.services.roles import (
    RoleDependencyNotFoundError,
    RoleNotFoundError,
    RoleSeedMissingError,
    RoleWorkspaceInactiveError,
    RoleWorkspaceNotFoundError,
    RoleService,
)

router = APIRouter(prefix="/roles", tags=["roles"])


def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    return RoleService(db)


def get_role_parsing_service() -> RoleParsingService:
    return RoleParsingService()


def get_ai_usage_service(db: Session = Depends(get_db)) -> AIUsageService:
    return AIUsageService(db)


def _role_parsing_model(service: RoleParsingService) -> str | None:
    settings = getattr(service, "settings", None)
    return getattr(settings, "openai_default_role_parsing_model", None)


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate,
    service: RoleService = Depends(get_role_service),
):
    try:
        return service.create_role(payload)
    except (RoleDependencyNotFoundError, RoleWorkspaceNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except RoleWorkspaceInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except RoleSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/parse", response_model=RoleParseResponse)
def parse_role(
    payload: RoleParseRequest,
    service: RoleParsingService = Depends(get_role_parsing_service),
    usage_service: AIUsageService = Depends(get_ai_usage_service),
):
    started_at = time.perf_counter()
    try:
        user = usage_service.current_user()
    except AIUsageSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    usage_service.record_event(
        AIUsageEventCreate(
            user_id=user.id,
            feature="parse_opportunity",
            event_type="requested",
            provider="openai",
            model=_role_parsing_model(service),
            content_hash=content_hash(payload.raw_text),
            metadata={"source": payload.source, "job_url_provided": bool(payload.job_url)},
        )
    )
    usage_service.db.commit()
    try:
        result = service.parse(payload)
        usage_service.record_event(
            AIUsageEventCreate(
                user_id=user.id,
                feature="parse_opportunity",
                event_type="completed",
                provider="openai",
                model=_role_parsing_model(service),
                latency_ms=max(0, round((time.perf_counter() - started_at) * 1000)),
                content_hash=content_hash(payload.raw_text),
            )
        )
        usage_service.db.commit()
        return result
    except RoleParsingUnavailableError as exc:
        usage_service.record_event(
            AIUsageEventCreate(
                user_id=user.id,
                feature="parse_opportunity",
                event_type="skipped_disabled",
                provider="openai",
                model=_role_parsing_model(service),
                latency_ms=max(0, round((time.perf_counter() - started_at) * 1000)),
                error_class=type(exc).__name__,
                content_hash=content_hash(payload.raw_text),
            )
        )
        usage_service.db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except RoleParsingValidationError as exc:
        usage_service.record_event(
            AIUsageEventCreate(
                user_id=user.id,
                feature="parse_opportunity",
                event_type="failed",
                provider="openai",
                model=_role_parsing_model(service),
                latency_ms=max(0, round((time.perf_counter() - started_at) * 1000)),
                error_class=type(exc).__name__,
                content_hash=content_hash(payload.raw_text),
            )
        )
        usage_service.db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )
    except RoleParsingProviderError as exc:
        usage_service.record_event(
            AIUsageEventCreate(
                user_id=user.id,
                feature="parse_opportunity",
                event_type="failed",
                provider="openai",
                model=_role_parsing_model(service),
                latency_ms=max(0, round((time.perf_counter() - started_at) * 1000)),
                error_class=type(exc).__name__,
                content_hash=content_hash(payload.raw_text),
            )
        )
        usage_service.db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )


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


@router.post("/{role_id}/opportunity-intelligence", response_model=RoleResponse)
def refresh_opportunity_intelligence(
    role_id: uuid.UUID,
    service: RoleService = Depends(get_role_service),
):
    try:
        return service.refresh_opportunity_intelligence(role_id)
    except RoleNotFoundError as exc:
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
