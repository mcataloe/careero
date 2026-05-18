from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.services.opportunity_intelligence import analyze_opportunity


def _role(**overrides):
    values = {
        "id": uuid4(),
        "user_id": uuid4(),
        "workspace_id": uuid4(),
        "title": "Senior Platform Engineer",
        "company": SimpleNamespace(name="Example Co"),
        "job_url": "https://example.com/jobs/1",
        "remote_type": "remote",
        "compensation_min": Decimal("120000"),
        "compensation_max": Decimal("130000"),
        "raw_description": "",
        "normalized_description": "",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_opportunity_intelligence_detects_explainable_risk_signals() -> None:
    role = _role(
        title="Staff Platform Engineer",
        normalized_description=(
            "Urgent immediate start for a fast-paced environment. "
            "Must know Kubernetes Terraform AWS Azure GCP Python Java React Node "
            "security devops product management. This is remote, but hybrid in office "
            "three days per week. You will wear many hats."
        ),
        compensation_max=Decimal("125000"),
    )

    intelligence = analyze_opportunity(role)

    signal_types = {signal["type"] for signal in intelligence["signals"]}
    assert "unrealistic_requirement_stacking" in signal_types
    assert "hidden_hybrid_expectations" in signal_types
    assert "under_market_compensation" in signal_types
    assert "suspicious_urgency" in signal_types
    assert "do_everything_role_language" in signal_types
    assert "Compensation Risk" in intelligence["categories"]
    assert "Culture Risk" in intelligence["categories"]
    assert all(signal["basis"] for signal in intelligence["signals"])
    assert all(signal["confidence"] for signal in intelligence["signals"])


def test_opportunity_intelligence_detects_duplicate_overlap() -> None:
    first = _role(title="Senior Platform Engineer")
    duplicate = _role(
        id=uuid4(),
        company=SimpleNamespace(name="Example Co"),
        title="Senior Platform Engineer",
        job_url="https://example.com/jobs/1",
    )

    intelligence = analyze_opportunity(first, overlapping_roles=[duplicate])

    signal = next(
        signal
        for signal in intelligence["signals"]
        if signal["type"] == "duplicate_or_overlap"
    )
    assert signal["type"] == "duplicate_or_overlap"
    assert signal["confidence"] == "high"
    assert "Duplicate / Overlap" in intelligence["categories"]


def test_opportunity_intelligence_does_not_invent_signals_without_basis() -> None:
    role = _role(
        title="Platform Engineer",
        remote_type="hybrid",
        compensation_min=None,
        compensation_max=None,
        normalized_description="Build internal infrastructure with a focused team.",
    )

    intelligence = analyze_opportunity(role)

    assert intelligence["signals"] == []
    assert intelligence["categories"] == ["Strong Fit"]
    assert "No deterministic caution signals" in intelligence["summary"]
