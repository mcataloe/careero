from types import SimpleNamespace
from uuid import uuid4

from app.services.compass_insights import build_compass_trend_insights


def _point(score, comp, seniority, category="infrastructure"):
    return {
        "role_id": uuid4(),
        "created_at": "2026-05-18T00:00:00Z",
        "overall_score": score,
        "compensation_midpoint": comp,
        "seniority_level": seniority,
        "role_category": category,
    }


def test_compass_insights_surface_trends_as_weak_or_moderate_guidance() -> None:
    points = [
        _point(82, 190000, 4),
        _point(70, 170000, 3),
        _point(58, 135000, 2, "software_engineering"),
        _point(54, 125000, 2, "software_engineering"),
    ]
    workspace = SimpleNamespace(
        preferences={
            "targetCompensation": {"min": 180000},
            "targetSeniority": ["staff"],
        }
    )
    applications = [
        SimpleNamespace(role_id=points[2]["role_id"], current_state="applied"),
        SimpleNamespace(role_id=points[3]["role_id"], current_state="rejected"),
        SimpleNamespace(role_id=points[0]["role_id"], current_state="applied"),
    ]

    insights = build_compass_trend_insights(
        points=points,
        applications=applications,
        workspace=workspace,
    )

    labels = {insight["label"] for insight in insights}
    assert "Average COMPASS fit over time" in labels
    assert "Compensation drift" in labels
    assert "Compensation collapse risk" in labels
    assert "Role-seniority drift" in labels
    assert "Excessive low-fit submissions" in labels
    assert all(insight["confidence"] != "High Confidence" for insight in insights)
    assert all("basis" in insight and insight["basis"] for insight in insights)


def test_compass_insights_avoid_false_precision_with_thin_data() -> None:
    insights = build_compass_trend_insights(
        points=[_point(75, None, 3)],
        applications=[],
        workspace=None,
    )

    assert insights == [
        {
            "label": "COMPASS sample is thin",
            "message": "Search-level COMPASS direction is still a weak signal.",
            "basis": "Fewer than three completed COMPASS scores are available.",
            "confidence": "Insufficient Data",
            "severity": "info",
            "source_inputs": {"score_count": 1},
        }
    ]
