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
    assert insight["known_uncertainty"]
    assert has_governance_metadata(insight)
    assert normalize_confidence("unknown") == "Weak Signal"


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
