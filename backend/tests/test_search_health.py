from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.services.search_health import generate_search_health_signals


def _application(role_id, state="applied", *, days_ago=1):
    now = datetime(2026, 5, 18, tzinfo=timezone.utc)
    return SimpleNamespace(
        role_id=role_id,
        current_state=state,
        applied_at=now - timedelta(days=days_ago),
        updated_at=now - timedelta(days=days_ago),
    )


def _role(*, days_old=5, text=""):
    return SimpleNamespace(
        id=uuid4(),
        date_found=date(2026, 5, 18) - timedelta(days=days_old),
        status="found",
        raw_description=text,
        normalized_description=None,
    )


def _evaluation(score):
    return SimpleNamespace(overall_score=Decimal(str(score)))


def test_search_health_generates_gentle_low_fit_and_volume_signals() -> None:
    now = datetime(2026, 5, 18, tzinfo=timezone.utc)
    roles = [_role() for _ in range(16)]
    applications = [
        _application(role.id, days_ago=1)
        for role in roles
    ]
    latest_stride = {
        role.id: _evaluation(50 if index < 10 else 75)
        for index, role in enumerate(roles)
    }

    signals = generate_search_health_signals(
        applications=applications,
        roles=roles,
        latest_stride=latest_stride,
        now=now,
    )

    labels = {signal["signal_type"] for signal in signals}
    assert "excessive_application_volume" in labels
    assert "heavy_low_fit_focus" in labels
    all_text = " ".join(
        f"{signal['message']} {signal['gentle_guidance']}" for signal in signals
    ).lower()
    forbidden = ["streak", "missed your", "daily goal", "must apply", "should apply more"]
    assert all(term not in all_text for term in forbidden)


def test_search_health_detects_stale_and_burnout_risk_without_diagnosis() -> None:
    now = datetime(2026, 5, 18, tzinfo=timezone.utc)
    roles = [
        _role(days_old=45, text="High pressure fast-paced environment."),
        _role(days_old=40, text="Nights and weekends may be needed."),
    ]

    signals = generate_search_health_signals(
        applications=[],
        roles=roles,
        latest_stride={},
        now=now,
    )

    labels = {signal["signal_type"] for signal in signals}
    assert "stale_opportunities" in labels
    assert "burnout_risk_pattern" in labels
    text = " ".join(signal["message"] for signal in signals).lower()
    assert "diagnosis" not in text
    assert "therapy" not in text
