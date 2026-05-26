import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.advisor_packets import (
    AdvisorPacketIncludeOptions,
    AdvisorPacketResponse,
)
from app.services.advisor_packets import (
    AdvisorPacketNotFoundError,
    AdvisorPacketSeedMissingError,
    AdvisorPacketService,
)

router = APIRouter(prefix="/applications", tags=["advisor-packets"])


def get_advisor_packet_service(
    db: Session = Depends(get_db),
) -> AdvisorPacketService:
    return AdvisorPacketService(db)


@router.get("/{application_id}/advisor-packet", response_model=AdvisorPacketResponse)
def get_application_advisor_packet(
    application_id: uuid.UUID,
    service: AdvisorPacketService = Depends(get_advisor_packet_service),
):
    try:
        return service.get_application_packet(application_id)
    except AdvisorPacketNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AdvisorPacketSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/{application_id}/advisor-packet/preview",
    response_model=AdvisorPacketResponse,
)
def preview_application_advisor_packet(
    application_id: uuid.UUID,
    include_options: AdvisorPacketIncludeOptions,
    service: AdvisorPacketService = Depends(get_advisor_packet_service),
):
    try:
        return service.get_application_packet(application_id, include_options)
    except AdvisorPacketNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AdvisorPacketSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/{application_id}/advisor-packet/exports/md")
def export_application_advisor_packet_markdown(
    application_id: uuid.UUID,
    include_options: AdvisorPacketIncludeOptions | None = None,
    service: AdvisorPacketService = Depends(get_advisor_packet_service),
):
    try:
        result = service.export_application_packet_markdown(application_id, include_options)
    except AdvisorPacketNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AdvisorPacketSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return Response(
        content=result.content,
        media_type=result.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{result.file_name}"',
            "X-Careero-Content-Hash": result.content_hash,
            "X-Careero-Local-Only": "true",
            "X-Careero-External-Sharing": "false",
        },
    )
