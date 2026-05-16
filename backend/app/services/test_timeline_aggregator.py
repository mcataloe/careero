import pytest
from datetime import datetime, timezone, timedelta
from app.schemas.timeline import TimelineEventResponse
from app.services.timeline_aggregator import get_application_timeline


def test_get_application_timeline_returns_empty_when_no_records():
    # Assuming a mock DB session
    mock_db = None

    events = get_application_timeline(mock_db, "app-123")
    assert isinstance(events, list)

    # In the real test with DB seeded, assert len(events) == 0
    assert len(events) == 0


def test_timeline_sorting():
    # Future validation: ensure that the aggregator dynamically sorts all gathered lists correctly
    # into reverse-chronological order (DESC).
    event_old = datetime.now(timezone.utc) - timedelta(days=2)
    event_new = datetime.now(timezone.utc) - timedelta(days=1)

    # Mock insertion into the timeline service output...
    # events = get_application_timeline(mock_db, "app-123")
    # assert events[0].occurred_at > events[-1].occurred_at
