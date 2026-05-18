from __future__ import annotations

from typing import Any


CONFIDENCE_LABELS = {
    "High Confidence",
    "Moderate Confidence",
    "Weak Signal",
    "Insufficient Data",
}

CONFIDENCE_ALIASES = {
    "high": "High Confidence",
    "moderate": "Moderate Confidence",
    "medium": "Moderate Confidence",
    "weak": "Weak Signal",
    "low": "Weak Signal",
    "insufficient": "Insufficient Data",
}


def normalize_confidence(value: str | None) -> str:
    if value in CONFIDENCE_LABELS:
        return value
    key = (value or "").strip().lower()
    return CONFIDENCE_ALIASES.get(key, "Weak Signal")


def governed_insight(
    *,
    label: str,
    message: str,
    basis: str,
    confidence: str,
    source_inputs: dict[str, Any] | None = None,
    known_uncertainty: str | None = None,
    severity: str = "info",
    **extra: Any,
) -> dict[str, Any]:
    return {
        "label": label,
        "message": message,
        "basis": basis,
        "confidence": normalize_confidence(confidence),
        "source_inputs": source_inputs or {},
        "known_uncertainty": known_uncertainty
        or "Derived from the user's tracked Careero data; incomplete records can change this signal.",
        "severity": severity,
        **extra,
    }


def has_governance_metadata(item: dict[str, Any]) -> bool:
    return bool(item.get("basis")) and bool(item.get("confidence"))
