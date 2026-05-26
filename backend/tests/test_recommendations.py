from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.services.recommendations import generate_recommendations


def _role(categories):
    return SimpleNamespace(
        id=uuid4(),
        title="Senior Platform Engineer",
        parse_metadata={"opportunityIntelligence": {"categories": categories}},
    )


def _application(role_id, *, days_since_apply=10, state="applied"):
    now = datetime(2026, 5, 18, tzinfo=timezone.utc)
    return SimpleNamespace(
        id=uuid4(),
        role_id=role_id,
        current_state=state,
        applied_at=now - timedelta(days=days_since_apply),
        interview_stages=[],
    )


def _artifact_record(variant, response):
    return SimpleNamespace(
        artifact_type="tailored_resume",
        variant_name=variant,
        targeted_role_category="infrastructure",
        response_outcome=response,
        interview_outcome="interview_received" if response == "positive_response" else "none_recorded",
    )


def test_recommendations_include_reason_basis_and_confidence() -> None:
    role = _role(["Duplicate / Overlap"])
    records = [
        _artifact_record("Platform Resume", "positive_response"),
        _artifact_record("Platform Resume", "positive_response"),
        _artifact_record("Platform Resume", "pending"),
    ]

    recommendations = generate_recommendations(
        roles=[role],
        applications=[_application(role.id)],
        artifact_records=records,
        health_signals=[
            {
                "signal_type": "heavy_low_fit_focus",
                "basis": "Low COMPASS fit among submitted applications.",
                "confidence": "Weak Signal",
                "source_inputs": {"submitted": 4},
            }
        ],
        now=datetime(2026, 5, 18, tzinfo=timezone.utc),
    )

    actions = {recommendation["action"] for recommendation in recommendations}
    assert {"archive", "follow_up", "reuse", "increase_selectivity"} <= actions
    assert all(recommendation["reason"] for recommendation in recommendations)
    assert all(recommendation["basis"] for recommendation in recommendations)
    assert all(recommendation["confidence"] for recommendation in recommendations)


def test_recommendations_are_not_taskmaster_language() -> None:
    role = _role(["Archive Candidate"])
    recommendations = generate_recommendations(
        roles=[role],
        applications=[],
        artifact_records=[],
        health_signals=[],
        now=datetime(2026, 5, 18, tzinfo=timezone.utc),
    )

    text = " ".join(
        f"{item['title']} {item['reason']} {item['basis']}" for item in recommendations
    ).lower()
    forbidden = ["must", "daily goal", "streak", "missed", "failure"]
    assert all(term not in text for term in forbidden)
