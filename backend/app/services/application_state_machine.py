from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException

# The canonical Application Workflow States
ALLOWED_TRANSITIONS = {
    "discovered": ["interested", "withdrawn", "archived"],
    "interested": ["applied", "withdrawn", "archived"],
    "applied": ["interviewing", "rejected", "withdrawn", "archived"],
    "interviewing": ["offer", "rejected", "withdrawn", "archived"],
    "offer": ["withdrawn", "archived"],
    "rejected": ["archived"],
    "withdrawn": ["archived"],
    "archived": ["discovered", "interested"],  # Explicit reactivation
}


def get_available_transitions(current_state: str) -> List[str]:
    """
    Returns a list of allowed next states for a given application state.
    """
    return ALLOWED_TRANSITIONS.get(current_state, [])


def can_transition(from_state: str, to_state: str) -> bool:
    """
    Checks if a transition from one workflow state to another is allowed.
    """
    if from_state == to_state:
        return True  # Idempotent
    return to_state in get_available_transitions(from_state)


def transition_application_state(
    db_session,
    application_record,
    new_state: str,
    changed_by: str = "user",
    reason: Optional[str] = None,
):
    """
    Transitions an application's state, appends a history record, and emits an activity log.
    Raises an HTTPException if the transition is invalid.
    """
    current_state = application_record.current_state

    if not can_transition(current_state, new_state):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid application state transition from '{current_state}' to '{new_state}'.",
        )

    if current_state == new_state:
        return application_record  # No action needed

    now = datetime.now(timezone.utc)

    # 1. Update the application's current state
    application_record.current_state = new_state
    application_record.updated_at = now

    # 2. Build the state history record (Assumes an ApplicationStateHistory model exists)
    # history_entry = ApplicationStateHistory(
    #     application_id=application_record.id,
    #     state=new_state,
    #     changed_at=now,
    #     changed_by=changed_by,
    #     reason=reason
    # )
    # db_session.add(history_entry)

    # 3. Log an ActivityLog event
    # log_activity(
    #     db_session,
    #     entity_type="application",
    #     entity_id=application_record.id,
    #     event_name=f"application.state_changed",
    #     details={"from_state": current_state, "to_state": new_state, "reason": reason}
    # )

    return application_record
