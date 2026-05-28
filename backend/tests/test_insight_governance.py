from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.services.artifact_performance import summarize_artifact_records
from app.services.insight_governance import (
    CONFIDENCE_LABELS,
    governed_insight,
    has_governance_metadata,
    normalize_confidence,
    normalize_confidence_level,
)
from app.services.recommendations import generate_recommendations
from app.services.search_health import generate_search_health_signals


def test_governed_insight_normalizes_confidence_and_uncertainty() -> None:
    insight = governed_insight(
        label="Example",
        message="Example message.",
        basis="Example basis.",
        confidence="moderate",
        source_inputs={"count": 3},
    )

    assert insight["confidence"] == "Moderate Confidence"
    assert insight["confidence_level"] == "moderate"
    assert insight["known_uncertainty"]
    assert insight["id"].startswith("insight_")
    assert insight["freshness"]["generated_at"]
    assert insight["generation_method"] == "deterministic"
    assert insight["visibility"] == "internal"
    assert has_governance_metadata(insight)
    assert normalize_confidence("unknown") == "Weak Signal"
    assert normalize_confidence_level("insufficient_data") == "insufficient_data"


def test_governed_insight_supports_sources_scope_and_actionability() -> None:
    insight = governed_insight(
        category="follow_up_action",
        label="Review follow-up timing",
        message="Application may need review.",
        basis="Applied date is older than the follow-up threshold.",
        confidence="weak",
        scope={"workspace_id": "workspace-1", "application_id": "application-1"},
        source_references=[
            {
                "source_type": "application_event",
                "source_id": None,
                "label": "Applied date",
                "field": "applied_at",
                "metadata": {},
            }
        ],
        recommended_action={
            "action_type": "review_follow_up",
            "label": "Review follow-up",
            "route_path": "/applications/application-1/overview",
            "review_required": True,
            "metadata": {},
        },
    )

    assert insight["category"] == "follow_up_action"
    assert insight["scope"]["workspace_id"] == "workspace-1"
    assert insight["source_references"][0]["source_type"] == "application_event"
    assert insight["recommended_action"]["review_required"] is True


def test_major_layer5_outputs_expose_confidence_and_basis() -> None:
    artifact_records = [
        SimpleNamespace(
            artifact_type="tailored_resume",
            variant_name="Platform Resume",
            targeted_role_category="infrastructure",
            response_outcome="positive_response",
            interview_outcome="interview_received",
        )
        for _ in range(3)
    ]
    artifact_insights = summarize_artifact_records(artifact_records)["insights"]

    now = datetime(2026, 5, 18, tzinfo=timezone.utc)
    role_id = uuid4()
    health_signals = generate_search_health_signals(
        applications=[
            SimpleNamespace(
                role_id=role_id,
                current_state="applied",
                applied_at=now,
                updated_at=now,
            )
            for _ in range(15)
        ],
        roles=[],
        latest_compass={role_id: SimpleNamespace(overall_score=Decimal("55"))},
        now=now,
    )
    recommendations = generate_recommendations(
        roles=[
            SimpleNamespace(
                id=role_id,
                title="Senior Platform Engineer",
                parse_metadata={"opportunityIntelligence": {"categories": ["Archive Candidate"]}},
            )
        ],
        applications=[],
        artifact_records=artifact_records,
        health_signals=health_signals,
        now=now,
    )

    for item in [*artifact_insights, *health_signals, *recommendations]:
        assert item["basis"]
        assert item["confidence"]
        assert item["confidence"] in CONFIDENCE_LABELS
        assert item["confidence_level"] in {
            "insufficient_data",
            "weak",
            "moderate",
            "high",
            "unknown",
        }
