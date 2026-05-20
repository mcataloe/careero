from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from difflib import SequenceMatcher
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Role


VERSION = "opportunity-intelligence.v1"


class OpportunityIntelligenceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def analyze_role(self, role: Role) -> dict[str, Any]:
        overlapping_roles = self._overlapping_roles(role)
        return analyze_opportunity(role, overlapping_roles=overlapping_roles)

    def refresh_role(self, role: Role) -> dict[str, Any]:
        intelligence = self.analyze_role(role)
        role.parse_metadata = {
            **(role.parse_metadata or {}),
            "opportunityIntelligence": intelligence,
        }
        return intelligence

    def _overlapping_roles(self, role: Role) -> list[Role]:
        statement = (
            select(Role)
            .where(
                Role.user_id == role.user_id,
                Role.workspace_id == role.workspace_id,
                Role.id != role.id,
                Role.deleted_at.is_(None),
            )
            .options(joinedload(Role.company))
        )
        return list(self.db.scalars(statement))


def analyze_opportunity(
    role: Role,
    *,
    overlapping_roles: list[Role] | None = None,
) -> dict[str, Any]:
    description = _clean_text(
        role.normalized_description or role.raw_description or ""
    )
    title = _clean_text(role.title)
    signals: list[dict[str, Any]] = []
    signals.extend(_requirement_stack_signals(description))
    signals.extend(_seniority_signals(title, description))
    signals.extend(_hidden_hybrid_signals(role, description))
    signals.extend(_compensation_signals(role, title))
    signals.extend(_phrase_signals(description))
    signals.extend(_misleading_signals(role, description))
    signals.extend(_duplicate_signals(role, overlapping_roles or []))
    categories = _categories(signals)
    return {
        "version": VERSION,
        "evaluatedAt": datetime.now(timezone.utc).isoformat(),
        "signals": signals,
        "categories": categories,
        "summary": _summary(signals, categories),
    }


def _requirement_stack_signals(description: str) -> list[dict[str, Any]]:
    required_terms = _matches(
        description,
        [
            "kubernetes",
            "terraform",
            "aws",
            "azure",
            "gcp",
            "python",
            "java",
            "react",
            "node",
            "data engineering",
            "machine learning",
            "security",
            "devops",
            "product management",
            "scrum",
            "salesforce",
        ],
    )
    if len(required_terms) >= 9:
        return [
            _signal(
                "unrealistic_requirement_stacking",
                "Requirement stack may be broad",
                "medium",
                f"Detected {len(required_terms)} distinct requirement areas.",
                "Rule matched many unrelated technical/domain requirement terms in the job description.",
                "moderate",
                evidence=required_terms[:8],
            )
        ]
    return []


def _seniority_signals(title: str, description: str) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    years = _years_required(description)
    if any(term in title for term in ["junior", "associate", "entry"]) and _has_any(
        description,
        ["lead", "principal", "architect", "own the roadmap"],
    ):
        signals.append(
            _signal(
                "seniority_mismatch",
                "Seniority language may not match the title",
                "medium",
                "Entry-level title appears alongside senior ownership language.",
                "Title and responsibility language point to different seniority levels.",
                "moderate",
            )
        )
    if any(term in title for term in ["staff", "principal", "director"]) and years is not None and years <= 3:
        signals.append(
            _signal(
                "title_inflation",
                "Title may be inflated relative to stated experience",
                "medium",
                f"Title suggests senior scope while description asks for {years} years.",
                "Rule compares senior title terms with low stated years of experience.",
                "weak",
            )
        )
    return signals


def _hidden_hybrid_signals(role: Role, description: str) -> list[dict[str, Any]]:
    remote_type = (role.remote_type or "").lower()
    if "remote" in remote_type and _has_any(
        description,
        ["hybrid", "on-site", "onsite", "in office", "office three days", "relocate"],
    ):
        return [
            _signal(
                "hidden_hybrid_expectations",
                "Remote language conflicts with location expectations",
                "medium",
                "Remote field appears alongside hybrid, onsite, office, or relocation phrasing.",
                "Rule compares the structured remote type with job-description location language.",
                "moderate",
            )
        ]
    return []


def _compensation_signals(role: Role, title: str) -> list[dict[str, Any]]:
    max_comp = _decimal_to_float(role.compensation_max)
    min_comp = _decimal_to_float(role.compensation_min)
    if max_comp is None and min_comp is None:
        return []
    benchmark = _title_compensation_floor(title)
    if benchmark is None:
        return []
    observed = max_comp or min_comp or 0
    if observed < benchmark:
        return [
            _signal(
                "under_market_compensation",
                "Compensation may be low for the stated scope",
                "medium",
                f"Highest stated compensation is {observed:,.0f}; title heuristic floor is {benchmark:,.0f}.",
                "Internal title-scope heuristic only; this is not external market data.",
                "weak",
            )
        ]
    return []


def _phrase_signals(description: str) -> list[dict[str, Any]]:
    phrase_rules = [
        (
            "suspicious_urgency",
            "Urgency language may deserve caution",
            "medium",
            ["urgent", "immediate start", "start immediately", "asap", "move fast"],
        ),
        (
            "do_everything_role_language",
            "Role may expect one person to cover too many functions",
            "medium",
            ["wear many hats", "do whatever it takes", "end-to-end owner", "full ownership of everything"],
        ),
        (
            "burnout_risk_phrasing",
            "Description includes possible sustainability risk language",
            "medium",
            ["high pressure", "work hard play hard", "nights and weekends", "always on", "fast-paced environment"],
        ),
    ]
    signals: list[dict[str, Any]] = []
    for signal_type, label, severity, phrases in phrase_rules:
        found = _matches(description, phrases)
        if found:
            signals.append(
                _signal(
                    signal_type,
                    label,
                    severity,
                    f"Matched phrasing: {', '.join(found[:3])}.",
                    "Rule matched cautionary phrasing in the job description.",
                    "moderate",
                    evidence=found,
                )
            )
    return signals


def _misleading_signals(role: Role, description: str) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    if _has_any(description, ["competitive salary", "salary commensurate"]) and not (
        role.compensation_min or role.compensation_max
    ):
        signals.append(
            _signal(
                "misleading_job_description_indicators",
                "Compensation language is non-specific",
                "low",
                "Description uses broad compensation language without a stated range.",
                "Rule checks for vague compensation phrasing when no structured range is present.",
                "weak",
            )
        )
    return signals


def _duplicate_signals(role: Role, overlapping_roles: list[Role]) -> list[dict[str, Any]]:
    for other in overlapping_roles:
        if role.job_url and other.job_url and role.job_url == other.job_url:
            return [
                _duplicate_signal(
                    "Same job URL as another saved opportunity.",
                    other,
                    confidence="high",
                )
            ]
        if (
            role.company
            and other.company
            and _norm(role.company.name) == _norm(other.company.name)
            and _title_similarity(role.title, other.title) >= 0.88
        ):
            return [
                _duplicate_signal(
                    "Company and title are very similar to another saved opportunity.",
                    other,
                    confidence="moderate",
                )
            ]
        if _description_similarity(role, other) >= 0.9:
            return [
                _duplicate_signal(
                    "Description is highly similar to another saved opportunity.",
                    other,
                    confidence="moderate",
                )
            ]
    return []


def _duplicate_signal(reason: str, other: Role, *, confidence: str) -> dict[str, Any]:
    return _signal(
        "duplicate_or_overlap",
        "Possible duplicate or overlapping opportunity",
        "medium",
        reason,
        "Rule compares URL, company/title similarity, and description similarity within the workspace.",
        confidence,
        evidence=[{"roleId": str(other.id), "title": other.title}],
    )


def _categories(signals: list[dict[str, Any]]) -> list[str]:
    types = {signal["type"] for signal in signals}
    categories: list[str] = []
    if not signals:
        categories.append("Strong Fit")
    if types & {"seniority_mismatch", "unrealistic_requirement_stacking"}:
        categories.append("Strategic Stretch")
        categories.append("Low Probability")
    if types & {"under_market_compensation", "title_inflation"}:
        categories.append("Compensation Risk")
    if types & {"burnout_risk_phrasing", "do_everything_role_language", "suspicious_urgency"}:
        categories.append("Culture Risk")
    if "duplicate_or_overlap" in types:
        categories.append("Duplicate / Overlap")
    if len([signal for signal in signals if signal["severity"] in {"medium", "high"}]) >= 3:
        categories.append("Archive Candidate")
    if not categories:
        categories.append("Fallback")
    return categories


def _summary(signals: list[dict[str, Any]], categories: list[str]) -> str:
    if not signals:
        return "No deterministic caution signals were detected from the available fields."
    return f"{len(signals)} deterministic signal(s) detected: {', '.join(categories)}."


def _signal(
    signal_type: str,
    label: str,
    severity: str,
    reason: str,
    basis: str,
    confidence: str,
    *,
    evidence: list[Any] | None = None,
) -> dict[str, Any]:
    return {
        "type": signal_type,
        "label": label,
        "severity": severity,
        "reason": reason,
        "basis": basis,
        "confidence": confidence,
        "evidence": evidence or [],
    }


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _matches(text: str, phrases: list[str]) -> list[str]:
    return [phrase for phrase in phrases if phrase in text]


def _has_any(text: str, phrases: list[str]) -> bool:
    return bool(_matches(text, phrases))


def _years_required(description: str) -> int | None:
    matches = re.findall(r"(\d{1,2})\+?\s*(?:years|yrs)", description)
    if not matches:
        return None
    return max(int(match) for match in matches)


def _title_compensation_floor(title: str) -> float | None:
    if any(term in title for term in ["principal", "director"]):
        return 170000
    if "staff" in title:
        return 160000
    if "senior" in title:
        return 140000
    return None


def _decimal_to_float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _title_similarity(first: str, second: str) -> float:
    return SequenceMatcher(None, _norm(first), _norm(second)).ratio()


def _description_similarity(first: Role, second: Role) -> float:
    first_text = _norm((first.normalized_description or first.raw_description or "")[:2000])
    second_text = _norm((second.normalized_description or second.raw_description or "")[:2000])
    if not first_text or not second_text:
        return 0
    return SequenceMatcher(None, first_text, second_text).ratio()
