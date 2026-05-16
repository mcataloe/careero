from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

# from app.database import get_db
# from app.models import Application
from app.schemas.application import (
    ApplicationStateTransitionRequest,
    ApplicationResponse,
    ApplicationPipelineResponse,
)
from app.services.application_state_machine import (
    transition_application_state,
    get_available_transitions,
)

router = APIRouter(prefix="/api", tags=["Applications"])


@router.post(
    "/applications/{application_id}/transition", response_model=ApplicationResponse
)
def transition_application(
    application_id: str,
    request: ApplicationStateTransitionRequest,
    # db: Session = Depends(get_db)
):
    # Mock db fetch
    # application = db.query(Application).filter(Application.id == application_id).first()
    # if not application:
    #     raise HTTPException(status_code=404, detail="Application not found.")

    # application = transition_application_state(
    #     db_session=db,
    #     application_record=application,
    #     new_state=request.new_state,
    #     changed_by=request.changed_by.value,
    #     reason=request.reason
    # )
    # db.commit()
    # db.refresh(application)

    # For now, return a mock response that maps to expected schema
    pass


@router.get(
    "/workspaces/{workspace_id}/applications/pipeline",
    response_model=ApplicationPipelineResponse,
)
def get_application_pipeline(
    workspace_id: str,
    # db: Session = Depends(get_db)
):
    # applications = db.query(Application).filter(
    #     Application.workspace_id == workspace_id,
    #     Application.current_state != "archived"
    # ).all()

    pipeline = {
        "discovered": [],
        "interested": [],
        "applied": [],
        "interviewing": [],
        "offer": [],
        "rejected": [],
        "withdrawn": [],
    }

    # for app in applications:
    #     pipeline[app.current_state].append(app)

    return ApplicationPipelineResponse(workspace_id=workspace_id, pipeline=pipeline)
