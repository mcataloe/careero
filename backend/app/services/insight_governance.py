from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
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
    "insufficient_data": "Insufficient Data",
    "unknown": "Weak Signal",
}

CONFIDENCE_LEVELS = {
    "High Confidence": "high",
    "Moderate Confidence": "moderate",
    "Weak Signal": "weak",
    "Insufficient Data": "insufficient_data",
}

DEFAULT_UNCERTAINTY = (
    "Derived from the user's tracked Careero data; incomplete records can change this signal."
)


def normalize_confidence(value: str | None) -> str:
    if value in CONFIDENCE_LABELS:
        return value
    key = (value or "").strip().lower()
    return CONFIDENCE_ALIASES.get(key, "Weak Signal")


def normalize_confidence_level(value: str | None) -> str:
    return CONFIDENCE_LEVELS.get(normalize_confidence(value), "weak")


def governed_insight(
    *,
    label: str,
    message: str,
    basis: str,
    confidence: str,
    category: str = "other",
    insight_id: str | None = None,
    confidence_explanation: str | None = None,
    source_inputs: dict[str, Any] | None = None,
    known_uncertainty: str | list[str] | None = None,
    warnings: list[str] | None = None,
    severity: str = "info",
    priority: int | None = None,
    generation_method: str = "deterministic",
    visibility: str = "internal",
    scope: dict[str, Any] | None = None,
    source_references: list[dict[str, Any]] | None = None,
    freshness: dict[str, Any] | None = None,
    recommended_action: dict[str, Any] | None = None,
    created_at: datetime | str | None = None,
    updated_at: datetime | str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    generated_at = _iso_now()
    source_inputs = source_inputs or {}
    normalized_confidence = normalize_confidence(confidence)
    normalized_scope = _scope(scope)
    normalized_freshness = {
        "generated_at": generated_at,
        "source_updated_at": None,
        "is_stale": False,
        "refresh_reason": None,
        **(freshness or {}),
    }
    return {
        "id": insight_id
        or stable_insight_id(
            category=category,
            label=label,
            basis=basis,
            scope=normalized_scope,
            source_inputs=source_inputs,
        ),
        "category": category,
        "label": label,
        "message": message,
        "basis": basis,
        "confidence": normalized_confidence,
        "confidence_level": normalize_confidence_level(confidence),
        "confidence_explanation": confidence_explanation,
        "known_uncertainty": _uncertainty_list(known_uncertainty),
        "warnings": warnings or [],
        "severity": severity,
        "priority": priority,
        "generation_method": generation_method,
        "visibility": visibility,
        "scope": normalized_scope,
        "source_references": source_references or [],
        "source_inputs": source_inputs,
        "freshness": normalized_freshness,
        "recommended_action": recommended_action,
        "created_at": created_at,
        "updated_at": updated_at,
        **extra,
    }


def has_governance_metadata(item: dict[str, Any]) -> bool:
    return bool(item.get("basis")) and bool(item.get("confidence"))


def generated_timestamp() -> str:
    return _iso_now()


def stable_insight_id(
    *,
    category: str,
    label: str,
    basis: str,
    scope: dict[str, Any] | None = None,
    source_inputs: dict[str, Any] | None = None,
) -> str:
    payload = {
        "category": category,
        "label": label,
        "basis": basis,
        "scope": scope or {},
        "source_inputs": source_inputs or {},
    }
    raw = json.dumps(payload, sort_keys=True, default=str)
    return f"insight_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:20]}"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _scope(scope: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "user_scoped": True,
        "workspace_id": None,
        "opportunity_id": None,
        "compass_evaluation_id": None,
        "artifact_id": None,
        "application_id": None,
        **(scope or {}),
    }


def _uncertainty_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return [DEFAULT_UNCERTAINTY]
    if isinstance(value, str):
        return [value]
    return value
