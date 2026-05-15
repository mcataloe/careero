import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.applications import (
    ApplicationExternalLinkCreate,
    ApplicationExternalLinkUpdate,
    ApplicationInterviewStageCreate,
    ApplicationInterviewStageUpdate,
    ApplicationNoteCreate,
    ApplicationNoteUpdate,
    ApplicationReminderCreate,
    ApplicationReminderUpdate,
    ApplicationStateTransitionRequest,
)
from app.services.applications import (
    ApplicationWorkflowNotFoundError,
    ApplicationWorkflowSeedMissingError,
    ApplicationWorkflowService,
    ApplicationWorkflowValidationError,
    ApplicationWorkflowWorkspaceInactiveError,
)

router = APIRouter(tags=["applications"])


def get_application_workflow_service(
    db: Session = Depends(get_db),
) -> ApplicationWorkflowService:
    return ApplicationWorkflowService(db)


@router.post(
    "/roles/{role_id}/application",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
def get_or_create_role_application(
    role_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.get_or_create_for_role(role_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowWorkspaceInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/applications", response_model=list[dict[str, Any]])
def list_applications(
    include_inactive: bool = False,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.list_applications(include_inactive=include_inactive)
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/applications/{application_id}", response_model=dict[str, Any])
def get_application(
    application_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.get_application(application_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/applications/{application_id}/state-transitions", response_model=dict[str, Any])
def transition_application_state(
    application_id: uuid.UUID,
    payload: ApplicationStateTransitionRequest,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.transition_state(application_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/applications/{application_id}/notes", response_model=dict[str, Any])
def create_application_note(
    application_id: uuid.UUID,
    payload: ApplicationNoteCreate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _application_response(lambda: service.create_note(application_id, payload))


@router.patch("/applications/{application_id}/notes/{note_id}", response_model=dict[str, Any])
def update_application_note(
    application_id: uuid.UUID,
    note_id: uuid.UUID,
    payload: ApplicationNoteUpdate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _application_response(lambda: service.update_note(application_id, note_id, payload))


@router.delete("/applications/{application_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_note(
    application_id: uuid.UUID,
    note_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        service.delete_note(application_id, note_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/applications/{application_id}/reminders", response_model=dict[str, Any])
def create_application_reminder(
    application_id: uuid.UUID,
    payload: ApplicationReminderCreate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _application_response(lambda: service.create_reminder(application_id, payload))


@router.patch("/applications/{application_id}/reminders/{reminder_id}", response_model=dict[str, Any])
def update_application_reminder(
    application_id: uuid.UUID,
    reminder_id: uuid.UUID,
    payload: ApplicationReminderUpdate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _application_response(
        lambda: service.update_reminder(application_id, reminder_id, payload)
    )


@router.post("/applications/{application_id}/reminders/{reminder_id}/complete", response_model=dict[str, Any])
def complete_application_reminder(
    application_id: uuid.UUID,
    reminder_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _application_response(lambda: service.complete_reminder(application_id, reminder_id))


@router.post("/applications/{application_id}/interview-stages", response_model=dict[str, Any])
def create_application_interview_stage(
    application_id: uuid.UUID,
    payload: ApplicationInterviewStageCreate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _application_response(lambda: service.create_interview_stage(application_id, payload))


@router.patch("/applications/{application_id}/interview-stages/{stage_id}", response_model=dict[str, Any])
def update_application_interview_stage(
    application_id: uuid.UUID,
    stage_id: uuid.UUID,
    payload: ApplicationInterviewStageUpdate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _application_response(
        lambda: service.update_interview_stage(application_id, stage_id, payload)
    )


@router.post("/applications/{application_id}/interview-stages/{stage_id}/complete", response_model=dict[str, Any])
def complete_application_interview_stage(
    application_id: uuid.UUID,
    stage_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _application_response(lambda: service.complete_interview_stage(application_id, stage_id))


@router.post("/applications/{application_id}/external-links", response_model=dict[str, Any])
def create_application_external_link(
    application_id: uuid.UUID,
    payload: ApplicationExternalLinkCreate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _application_response(lambda: service.create_external_link(application_id, payload))


@router.patch("/applications/{application_id}/external-links/{link_id}", response_model=dict[str, Any])
def update_application_external_link(
    application_id: uuid.UUID,
    link_id: uuid.UUID,
    payload: ApplicationExternalLinkUpdate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _application_response(
        lambda: service.update_external_link(application_id, link_id, payload)
    )


@router.delete("/applications/{application_id}/external-links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_external_link(
    application_id: uuid.UUID,
    link_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        service.delete_external_link(application_id, link_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _application_response(action):
    try:
        return action()
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
