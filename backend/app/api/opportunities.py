import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.roles import (
    get_ai_usage_service,
    get_role_parsing_service,
    get_role_service,
    parse_role_with_usage,
)
from app.schemas.role_parsing import RoleParseRequest, RoleParseResponse
from app.schemas.roles import OpportunityCreate, OpportunityResponse, OpportunityUpdate
from app.services.ai_usage import AIUsageService
from app.services.role_parsing import RoleParsingService
from app.services.opportunities import (
    OpportunityDependencyNotFoundError,
    OpportunityNotFoundError,
    OpportunitySeedMissingError,
    OpportunityService,
    OpportunityWorkspaceInactiveError,
    OpportunityWorkspaceNotFoundError,
)

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    payload: OpportunityCreate,
    service: OpportunityService = Depends(get_role_service),
):
    try:
        return service.create_role(payload)
    except (OpportunityDependencyNotFoundError, OpportunityWorkspaceNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except OpportunityWorkspaceInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except OpportunitySeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/parse", response_model=RoleParseResponse)
def parse_opportunity(
    payload: RoleParseRequest,
    service: RoleParsingService = Depends(get_role_parsing_service),
    usage_service: AIUsageService = Depends(get_ai_usage_service),
):
    return parse_role_with_usage(payload, service, usage_service)


@router.get("", response_model=list[OpportunityResponse])
def list_opportunities(service: OpportunityService = Depends(get_role_service)):
    try:
        return service.list_roles()
    except OpportunitySeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: uuid.UUID,
    service: OpportunityService = Depends(get_role_service),
):
    try:
        return service.get_role(opportunity_id)
    except OpportunityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except OpportunitySeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(
    opportunity_id: uuid.UUID,
    payload: OpportunityUpdate,
    service: OpportunityService = Depends(get_role_service),
):
    try:
        return service.update_role(opportunity_id, payload)
    except (OpportunityNotFoundError, OpportunityDependencyNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except OpportunitySeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/{opportunity_id}/opportunity-intelligence",
    response_model=OpportunityResponse,
)
def refresh_opportunity_intelligence(
    opportunity_id: uuid.UUID,
    service: OpportunityService = Depends(get_role_service),
):
    try:
        return service.refresh_opportunity_intelligence(opportunity_id)
    except OpportunityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except OpportunitySeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_opportunity(
    opportunity_id: uuid.UUID,
    service: OpportunityService = Depends(get_role_service),
):
    try:
        service.archive_role(opportunity_id)
    except OpportunityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except OpportunitySeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
