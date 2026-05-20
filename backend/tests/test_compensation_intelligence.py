from types import SimpleNamespace
from uuid import uuid4

from app.services.compensation_intelligence import build_compensation_insights


def _observation(title, midpoint, employment_type="full_time"):
    return {
        "role_id": uuid4(),
        "title": title,
        "compensation_min": midpoint - 10000 if midpoint is not None else None,
        "compensation_max": midpoint + 10000 if midpoint is not None else None,
        "midpoint": midpoint,
        "currency": "USD",
        "employment_type": employment_type,
        "remote_type": "remote",
        "source_basis": "stated_range" if midpoint is not None else "not_stated",
    }


def test_compensation_intelligence_uses_stated_ranges_and_flags_risks() -> None:
    observations = [
        _observation("Staff Platform Engineer", 185000),
        _observation("Senior Platform Engineer", 135000),
        _observation("Senior Infrastructure Engineer", 125000, "contract"),
    ]
    workspace = SimpleNamespace(
        workspace_type="full_time_individual_contributor",
        preferences={"targetCompensation": {"min": 170000}},
    )

    insights = build_compensation_insights(
        observations=observations,
        target_compensation_min=170000,
        workspace=workspace,
    )

    labels = {insight["label"] for insight in insights}
    assert "Under-target compensation" in labels
    assert "Compensation decline trend" in labels
    assert "Scope/compensation mismatch" in labels
    assert "Contract versus full-time assumptions" in labels
    assert all("external market data" not in insight["message"].lower() for insight in insights)
    assert any("not external market data" in insight["basis"] for insight in insights)


def test_compensation_intelligence_does_not_fabricate_without_ranges() -> None:
    insights = build_compensation_insights(
        observations=[_observation("Platform Engineer", None)],
        target_compensation_min=None,
        workspace=None,
    )

    assert insights == []
