from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.services.historical_learning import build_historical_summaries


def _role(title, company="Example Co", text=""):
    return SimpleNamespace(
        id=uuid4(),
        title=title,
        company=SimpleNamespace(name=company),
        raw_description=text,
        normalized_description=None,
    )


def _application(role, state="applied", *, days_ago=30, interviews=False):
    now = datetime(2026, 5, 18, tzinfo=timezone.utc)
    return SimpleNamespace(
        id=uuid4(),
        role_id=role.id,
        role=role,
        current_state=state,
        applied_at=now - timedelta(days=days_ago),
        interview_stages=[SimpleNamespace()] if interviews else [],
    )


def _artifact_record(response):
    return SimpleNamespace(
        artifact_type="tailored_resume",
        variant_name="Platform Resume",
        targeted_role_category="infrastructure",
        response_outcome=response,
        interview_outcome="interview_received" if response == "positive_response" else "none_recorded",
    )


def test_historical_learning_answers_prior_search_questions() -> None:
    platform = _role("Senior Platform Engineer", "Platform Co")
    manager = _role("Engineering Manager", "Quiet Co", "High pressure role.")
    applications = [
        _application(platform, state="interviewing", interviews=True),
        _application(manager, state="applied", days_ago=40),
    ]
    summaries = build_historical_summaries(
        workspaces=[SimpleNamespace(status="completed")],
        roles=[platform, manager],
        applications=applications,
        artifact_records=[
            _artifact_record("positive_response"),
            _artifact_record("pending"),
        ],
        now=datetime(2026, 5, 18, tzinfo=timezone.utc),
    )

    labels = {summary["label"] for summary in summaries}
    assert "Best responding role category" in labels
    assert "Best observed artifact variant" in labels
    assert "Most repeated no-response company" in labels
    assert "Roles that led to interviews" in labels
    assert "High-friction low-ROI pattern" in labels
    assert all(summary["basis"] for summary in summaries)
    assert all(summary["confidence"] for summary in summaries)


def test_historical_learning_handles_empty_history() -> None:
    summaries = build_historical_summaries(
        workspaces=[],
        roles=[],
        applications=[],
        artifact_records=[],
        now=datetime(2026, 5, 18, tzinfo=timezone.utc),
    )

    assert len(summaries) == 1
    assert summaries[0]["label"] == "Historical tracks reviewed"
    assert summaries[0]["value"] == 0
    assert summaries[0]["confidence"] == "Insufficient Data"
    assert summaries[0]["confidence_level"] == "insufficient_data"
    assert summaries[0]["category"] == "historical_learning"
    assert summaries[0]["source_inputs"] == {"workspace_count": 0}
