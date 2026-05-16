from typing import List
from datetime import datetime
from app.schemas.timeline import TimelineEventResponse


def get_application_timeline(
    db_session, application_id: str
) -> List[TimelineEventResponse]:
    """
    Aggregates typed domain events and ActivityLog entries into a unified timeline.
    Returns a reverse-chronological list of TimelineEventResponse.
    """
    events = []

    # 1. Fetch Application creation event (mocked)
    # app_record = db_session.query(Application).filter_by(id=application_id).first()
    # if app_record:
    #     events.append(TimelineEventResponse(
    #         id=f"app-created-{app_record.id}",
    #         application_id=app_record.id,
    #         event_type="application.created",
    #         title="Application tracked",
    #         occurred_at=app_record.created_at,
    #         actor="user",
    #         source_type="application",
    #         source_id=app_record.id
    #     ))

    # 2. Fetch Typed State History (mocked)
    # state_history = db_session.query(ApplicationStateHistory).filter_by(application_id=application_id).all()
    # for state in state_history:
    #     events.append(TimelineEventResponse(
    #         id=state.id,
    #         application_id=application_id,
    #         event_type="application.state_changed",
    #         title=f"Moved to {state.state.capitalize()}",
    #         description=state.reason,
    #         occurred_at=state.changed_at,
    #         actor=state.changed_by,
    #         source_type="application_state_history",
    #         source_id=state.id,
    #         metadata={"new_state": state.state}
    #     ))

    # 3. Fetch ActivityLog entries related to this application (mocked)
    # logs = db_session.query(ActivityLog).filter_by(entity_type="application", entity_id=application_id).all()
    # map logs to TimelineEventResponse, avoiding overlaps with the typed history

    # 4. Fetch linked entities (Stride Evaluations, Artifacts) using opportunity_id and map to events

    # Sort events descending by occurred_at (newest first)
    events.sort(key=lambda x: x.occurred_at, reverse=True)
    return events
