import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.applications import (
    ApplicationDetailResponse,
    ApplicationExternalLinkCreate,
    ApplicationExternalLinkResponse,
    ApplicationExternalLinkUpdate,
    ApplicationListItemResponse,
    ApplicationMetadataUpdate,
    ApplicationNoteCreate,
    ApplicationNoteResponse,
    ApplicationNoteUpdate,
    ApplicationPipelineResponse,
    ApplicationReminderCreate,
    ApplicationReminderResponse,
    ApplicationReminderUpdate,
    WorkspaceReminderResponse,
    ApplicationStateTransitionRequest,
    ApplicationTimelineEventResponse,
)
from app.services.applications import (
    ApplicationWorkflowNotFoundError,
    ApplicationWorkflowSeedMissingError,
    ApplicationWorkflowService,
    ApplicationWorkflowTransitionError,
    ApplicationWorkflowValidationError,
    ApplicationWorkflowWorkspaceInactiveError,
    ApplicationWorkflowWorkspaceNotFoundError,
)

router = APIRouter(tags=["applications"])


def get_application_workflow_service(
    db: Session = Depends(get_db),
) -> ApplicationWorkflowService:
    return ApplicationWorkflowService(db)


@router.post(
    "/roles/{role_id}/application",
    response_model=ApplicationDetailResponse,
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


@router.get("/applications", response_model=list[ApplicationListItemResponse])
def list_applications(
    workspace_id: uuid.UUID | None = None,
    include_inactive: bool = False,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.list_applications(
            workspace_id=workspace_id,
            include_inactive=include_inactive,
        )
    except ApplicationWorkflowWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/workspaces/{workspace_id}/applications",
    response_model=list[ApplicationListItemResponse],
)
def list_workspace_applications(
    workspace_id: uuid.UUID,
    include_inactive: bool = False,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.list_applications(
            workspace_id=workspace_id,
            include_inactive=include_inactive,
        )
    except ApplicationWorkflowWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/applications/pipeline", response_model=ApplicationPipelineResponse)
def get_applications_pipeline(
    workspace_id: uuid.UUID | None = None,
    include_inactive: bool = False,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.get_pipeline(
            workspace_id=workspace_id,
            include_inactive=include_inactive,
        )
    except ApplicationWorkflowWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/workspaces/{workspace_id}/applications/pipeline",
    response_model=ApplicationPipelineResponse,
)
def get_workspace_applications_pipeline(
    workspace_id: uuid.UUID,
    include_inactive: bool = False,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.get_pipeline(
            workspace_id=workspace_id,
            include_inactive=include_inactive,
        )
    except ApplicationWorkflowWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/applications/{application_id}", response_model=ApplicationDetailResponse)
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


@router.get(
    "/applications/{application_id}/timeline",
    response_model=list[ApplicationTimelineEventResponse],
)
def get_application_timeline(
    application_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.get_timeline(application_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/applications/{application_id}/notes",
    response_model=list[ApplicationNoteResponse],
)
def list_application_notes(
    application_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.list_notes(application_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/applications/{application_id}/notes",
    response_model=ApplicationNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application_note(
    application_id: uuid.UUID,
    payload: ApplicationNoteCreate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.create_note(application_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch(
    "/applications/{application_id}/notes/{note_id}",
    response_model=ApplicationNoteResponse,
)
def update_application_note(
    application_id: uuid.UUID,
    note_id: uuid.UUID,
    payload: ApplicationNoteUpdate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.update_note(application_id, note_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete(
    "/applications/{application_id}/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
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


@router.get(
    "/applications/{application_id}/reminders",
    response_model=list[ApplicationReminderResponse],
)
def list_application_reminders(
    application_id: uuid.UUID,
    status_filter: str | None = None,
    status: str | None = None,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.list_reminders(
            application_id,
            status_filter=status_filter or status,
        )
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/applications/{application_id}/reminders",
    response_model=ApplicationReminderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application_reminder(
    application_id: uuid.UUID,
    payload: ApplicationReminderCreate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.create_reminder(application_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch(
    "/applications/{application_id}/reminders/{reminder_id}",
    response_model=ApplicationReminderResponse,
)
def update_application_reminder(
    application_id: uuid.UUID,
    reminder_id: uuid.UUID,
    payload: ApplicationReminderUpdate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.update_reminder(application_id, reminder_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/applications/{application_id}/reminders/{reminder_id}/complete",
    response_model=ApplicationReminderResponse,
)
def complete_application_reminder(
    application_id: uuid.UUID,
    reminder_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.complete_reminder(application_id, reminder_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/applications/{application_id}/reminders/{reminder_id}/reopen",
    response_model=ApplicationReminderResponse,
)
def reopen_application_reminder(
    application_id: uuid.UUID,
    reminder_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.reopen_reminder(application_id, reminder_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete(
    "/applications/{application_id}/reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_application_reminder(
    application_id: uuid.UUID,
    reminder_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        service.delete_reminder(application_id, reminder_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/workspaces/{workspace_id}/reminders/upcoming",
    response_model=list[WorkspaceReminderResponse],
)
def list_upcoming_workspace_reminders(
    workspace_id: uuid.UUID,
    limit: int = 25,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.list_workspace_reminders(
            workspace_id,
            window="upcoming",
            limit=limit,
        )
    except ApplicationWorkflowWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/workspaces/{workspace_id}/reminders/overdue",
    response_model=list[WorkspaceReminderResponse],
)
def list_overdue_workspace_reminders(
    workspace_id: uuid.UUID,
    limit: int = 25,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.list_workspace_reminders(
            workspace_id,
            window="overdue",
            limit=limit,
        )
    except ApplicationWorkflowWorkspaceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/applications/{application_id}/links",
    response_model=list[ApplicationExternalLinkResponse],
)
def list_application_links(
    application_id: uuid.UUID,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.list_external_links(application_id)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/applications/{application_id}/links",
    response_model=ApplicationExternalLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application_link(
    application_id: uuid.UUID,
    payload: ApplicationExternalLinkCreate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.create_external_link(application_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch(
    "/applications/{application_id}/links/{link_id}",
    response_model=ApplicationExternalLinkResponse,
)
def update_application_link(
    application_id: uuid.UUID,
    link_id: uuid.UUID,
    payload: ApplicationExternalLinkUpdate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.update_external_link(application_id, link_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete(
    "/applications/{application_id}/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_application_link(
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


@router.patch(
    "/applications/{application_id}", response_model=ApplicationDetailResponse
)
def update_application(
    application_id: uuid.UUID,
    payload: ApplicationMetadataUpdate,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    try:
        return service.update_application(application_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/applications/{application_id}/transition",
    response_model=ApplicationDetailResponse,
)
def transition_application_state_alias(
    application_id: uuid.UUID,
    payload: ApplicationStateTransitionRequest,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _transition_application_state(application_id, payload, service)


@router.post(
    "/applications/{application_id}/state-transitions",
    response_model=ApplicationDetailResponse,
)
def transition_application_state(
    application_id: uuid.UUID,
    payload: ApplicationStateTransitionRequest,
    service: ApplicationWorkflowService = Depends(get_application_workflow_service),
):
    return _transition_application_state(application_id, payload, service)


def _transition_application_state(
    application_id: uuid.UUID,
    payload: ApplicationStateTransitionRequest,
    service: ApplicationWorkflowService,
):
    try:
        return service.transition_state(application_id, payload)
    except ApplicationWorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ApplicationWorkflowTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ApplicationWorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    except ApplicationWorkflowSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
