from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Protocol

from app.constants import (
    StrideConfidenceLevel,
    StrideDimension,
    StrideEvaluationStatus,
    StrideRecommendation,
)

RULESET_VERSION = "phase_2b_deterministic_v1"

RECOMMENDATION_THRESHOLDS = {
    StrideRecommendation.APPLY.value: 75,
    StrideRecommendation.MONITOR.value: 55,
    StrideRecommendation.NEEDS_REVIEW.value: 40,
}

TECH_KEYWORDS = {
    "aws",
    "azure",
    "docker",
    "fastapi",
    "go",
    "graphql",
    "java",
    "javascript",
    "kafka",
    "kubernetes",
    "node",
    "postgres",
    "postgresql",
    "python",
    "react",
    "redis",
    "sql",
    "terraform",
    "typescript",
}

RESPONSIBILITY_TERMS = {
    "build",
    "design",
    "develop",
    "implement",
    "lead",
    "maintain",
    "mentor",
    "own",
    "partner",
    "scale",
    "ship",
}

SENIORITY_TERMS = {
    "intern": "intern",
    "junior": "junior",
    "entry": "junior",
    "mid": "mid",
    "senior": "senior",
    "sr": "senior",
    "staff": "staff",
    "principal": "principal",
    "lead": "lead",
    "manager": "manager",
    "director": "director",
}

GENERIC_PHRASES = {
    "fast-paced environment",
    "rockstar",
    "ninja",
    "wear many hats",
    "other duties as assigned",
    "competitive salary",
    "great opportunity",
    "self starter",
}


class ScorableRole(Protocol):
    title: str
    job_url: str | None
    location: str | None
    remote_type: str | None
    compensation_min: Decimal | None
    compensation_max: Decimal | None
    compensation_currency: str | None
    raw_description: str | None
    normalized_description: str | None
    status: str
    company: Any


@dataclass(frozen=True)
class RuleConcern:
    code: str
    severity: str
    message: str
    dimension: str

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "dimension": self.dimension,
        }


@dataclass(frozen=True)
class StrideRuleResult:
    evaluation_status: str
    overall_score: Decimal
    recommendation: str
    confidence_level: str
    summary: str
    strengths: list[dict[str, Any]]
    concerns: list[dict[str, Any]]
    resume_alignment: dict[str, Any]
    compensation_alignment: dict[str, Any]
    seniority_alignment: dict[str, Any]
    remote_alignment: dict[str, Any]
    technical_alignment: dict[str, Any]
    company_risk: dict[str, Any]
    ats_keywords: list[str]
    missing_keywords: list[str]
    raw_evaluation_json: dict[str, Any]

    def to_persistence_dict(self) -> dict[str, Any]:
        return {
            "evaluation_status": self.evaluation_status,
            "overall_score": self.overall_score,
            "recommendation": self.recommendation,
            "confidence_level": self.confidence_level,
            "summary": self.summary,
            "strengths": self.strengths,
            "concerns": self.concerns,
            "resume_alignment": self.resume_alignment,
            "compensation_alignment": self.compensation_alignment,
            "seniority_alignment": self.seniority_alignment,
            "remote_alignment": self.remote_alignment,
            "technical_alignment": self.technical_alignment,
            "company_risk": self.company_risk,
            "ats_keywords": self.ats_keywords,
            "missing_keywords": self.missing_keywords,
            "raw_evaluation_json": self.raw_evaluation_json,
        }


def evaluate_role(
    role: ScorableRole,
    user_context: dict[str, Any] | None = None,
    user_notes: str | None = None,
) -> StrideRuleResult:
    context = user_context or {}
    text = _role_text(role)
    tokens = set(_tokens(text))
    concerns = detect_concerns(role, context)
    risk_flags = [concern for concern in concerns if concern.severity == "high"]
    target_keywords = _normal_string_list(context.get("target_keywords"))
    avoid_keywords = _normal_string_list(context.get("avoid_keywords"))
    ats_keywords = sorted(keyword for keyword in target_keywords if keyword in text.lower())
    missing_keywords = sorted(keyword for keyword in target_keywords if keyword not in text.lower())

    dimension_scores = {
        StrideDimension.STRATEGIC_FIT.value: _score_strategic_fit(role, context, text),
        StrideDimension.TECHNICAL_ALIGNMENT.value: _score_technical_alignment(
            tokens,
            target_keywords,
            avoid_keywords,
        ),
        StrideDimension.SENIORITY_ALIGNMENT.value: _score_seniority(role, context, text),
        StrideDimension.COMPENSATION_ALIGNMENT.value: _score_compensation(role, context),
        StrideDimension.REMOTE_LOCATION_ALIGNMENT.value: _score_remote_location(
            role,
            context,
        ),
        StrideDimension.COMPANY_SIGNAL.value: _score_company_signal(role),
        StrideDimension.ROLE_CLARITY.value: _score_role_clarity(text, concerns),
        StrideDimension.APPLICATION_EFFORT.value: _score_application_effort(role, text),
        StrideDimension.ATS_RESUME_ALIGNMENT.value: _score_ats_alignment(
            ats_keywords,
            missing_keywords,
            target_keywords,
        ),
        StrideDimension.RISK_FLAGS.value: _score_risk_flags(concerns),
    }
    overall_score = round(sum(dimension_scores.values()) / len(dimension_scores))
    confidence_level = select_confidence(role, context, text, dimension_scores)
    recommendation = select_recommendation(overall_score, confidence_level, risk_flags)
    strengths = _build_strengths(role, dimension_scores, ats_keywords)
    summary = _build_summary(role, overall_score, recommendation, confidence_level)

    return StrideRuleResult(
        evaluation_status=StrideEvaluationStatus.COMPLETED.value,
        overall_score=Decimal(overall_score),
        recommendation=recommendation,
        confidence_level=confidence_level,
        summary=summary,
        strengths=strengths,
        concerns=[concern.as_dict() for concern in concerns],
        resume_alignment=_section(
            score=dimension_scores[StrideDimension.ATS_RESUME_ALIGNMENT.value],
            status="baseline",
            notes="Uses request-scoped target keywords only; no resume data is stored.",
            matched_keywords=ats_keywords,
            missing_keywords=missing_keywords,
        ),
        compensation_alignment=_section(
            score=dimension_scores[StrideDimension.COMPENSATION_ALIGNMENT.value],
            status="baseline",
            notes="Uses role compensation fields and optional target_compensation_min.",
        ),
        seniority_alignment=_section(
            score=dimension_scores[StrideDimension.SENIORITY_ALIGNMENT.value],
            status="baseline",
            notes="Uses seniority language from title and description.",
        ),
        remote_alignment=_section(
            score=dimension_scores[StrideDimension.REMOTE_LOCATION_ALIGNMENT.value],
            status="baseline",
            notes="Uses role remote/location fields and optional preferred_remote_type/preferred_locations.",
        ),
        technical_alignment=_section(
            score=dimension_scores[StrideDimension.TECHNICAL_ALIGNMENT.value],
            status="baseline",
            notes="Uses explicit target and avoid keywords when supplied.",
        ),
        company_risk=_section(
            score=dimension_scores[StrideDimension.COMPANY_SIGNAL.value],
            status="baseline",
            notes="Uses only company fields already stored in Careero.",
        ),
        ats_keywords=ats_keywords,
        missing_keywords=missing_keywords,
        raw_evaluation_json={
            "ruleset_version": RULESET_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dimension_scores": dimension_scores,
            "weights": {dimension: 1 for dimension in dimension_scores},
            "thresholds": RECOMMENDATION_THRESHOLDS,
            "detected_signals": _detected_signals(role, text, ats_keywords),
            "risk_flags": [concern.as_dict() for concern in risk_flags],
            "input_completeness": input_completeness(role, context, text),
            "user_notes": user_notes,
            "limitations": [
                "Deterministic baseline only.",
                "No OpenAI call was made.",
                "No resume facts were inferred.",
                "No external company, compensation, or job market research was performed.",
            ],
        },
    )


def detect_concerns(role: ScorableRole, user_context: dict[str, Any] | None = None) -> list[RuleConcern]:
    context = user_context or {}
    text = _role_text(role)
    concerns: list[RuleConcern] = []

    if role.compensation_min is None and role.compensation_max is None:
        concerns.append(
            RuleConcern(
                code="missing_compensation",
                severity="medium",
                message="The role does not include compensation details.",
                dimension=StrideDimension.COMPENSATION_ALIGNMENT.value,
            )
        )

    if _detect_seniority(text) is None:
        concerns.append(
            RuleConcern(
                code="unclear_seniority",
                severity="medium",
                message="The title and description do not clearly indicate seniority.",
                dimension=StrideDimension.SENIORITY_ALIGNMENT.value,
            )
        )

    preferred_remote = _normal_string(context.get("preferred_remote_type"))
    role_remote = _normal_string(role.remote_type)
    if preferred_remote == "remote" and role_remote in {"hybrid", "onsite", "on-site", "office"}:
        concerns.append(
            RuleConcern(
                code="remote_mismatch",
                severity="high" if role_remote in {"onsite", "on-site", "office"} else "medium",
                message="The role remote type conflicts with the requested remote preference.",
                dimension=StrideDimension.REMOTE_LOCATION_ALIGNMENT.value,
            )
        )

    responsibility_hits = sum(1 for term in RESPONSIBILITY_TERMS if term in text.lower())
    if _word_count(text) < 60 or responsibility_hits < 2:
        concerns.append(
            RuleConcern(
                code="vague_responsibilities",
                severity="medium",
                message="The description has limited concrete responsibility language.",
                dimension=StrideDimension.ROLE_CLARITY.value,
            )
        )

    tech_hits = sorted(keyword for keyword in TECH_KEYWORDS if keyword in _tokens(text))
    if len(tech_hits) >= 11:
        concerns.append(
            RuleConcern(
                code="technology_sprawl",
                severity="medium",
                message="The description lists many technologies, which may indicate broad or unfocused scope.",
                dimension=StrideDimension.TECHNICAL_ALIGNMENT.value,
            )
        )

    generic_phrase_hits = [phrase for phrase in GENERIC_PHRASES if phrase in text.lower()]
    if _word_count(text) < 35 or len(generic_phrase_hits) >= 2:
        concerns.append(
            RuleConcern(
                code="generic_description",
                severity="high" if len(generic_phrase_hits) >= 2 else "medium",
                message="The description appears unusually generic or sparse.",
                dimension=StrideDimension.RISK_FLAGS.value,
            )
        )

    return concerns


def select_recommendation(
    overall_score: int,
    confidence_level: str,
    severe_risk_flags: list[RuleConcern] | None = None,
) -> str:
    severe_risk_flags = severe_risk_flags or []
    if severe_risk_flags or overall_score < 40:
        return StrideRecommendation.SKIP.value
    if confidence_level == StrideConfidenceLevel.LOW.value:
        return StrideRecommendation.NEEDS_REVIEW.value
    if overall_score >= RECOMMENDATION_THRESHOLDS[StrideRecommendation.APPLY.value]:
        return StrideRecommendation.APPLY.value
    if overall_score >= RECOMMENDATION_THRESHOLDS[StrideRecommendation.MONITOR.value]:
        return StrideRecommendation.MONITOR.value
    return StrideRecommendation.NEEDS_REVIEW.value


def select_confidence(
    role: ScorableRole,
    user_context: dict[str, Any],
    text: str,
    dimension_scores: dict[str, int],
) -> str:
    completeness = input_completeness(role, user_context, text)
    unknown_dimensions = sum(1 for score in dimension_scores.values() if score == 50)
    if _word_count(text) < 25 or unknown_dimensions >= 5:
        return StrideConfidenceLevel.LOW.value
    if (
        completeness["has_title"]
        and completeness["has_company"]
        and completeness["has_description"]
        and completeness["has_location_or_remote"]
        and completeness["has_compensation"]
        and completeness["has_user_context"]
        and _word_count(text) >= 40
    ):
        return StrideConfidenceLevel.HIGH.value
    return StrideConfidenceLevel.MEDIUM.value


def input_completeness(
    role: ScorableRole,
    user_context: dict[str, Any],
    text: str,
) -> dict[str, bool | int]:
    return {
        "has_title": bool(role.title),
        "has_company": bool(getattr(role.company, "name", None)),
        "has_description": bool(text.strip()),
        "description_word_count": _word_count(text),
        "has_location_or_remote": bool(role.location or role.remote_type),
        "has_compensation": role.compensation_min is not None or role.compensation_max is not None,
        "has_user_context": bool(user_context),
    }


def _score_strategic_fit(role: ScorableRole, context: dict[str, Any], text: str) -> int:
    score = 65
    if role.job_url:
        score += 5
    if role.normalized_description or _word_count(text) >= 80:
        score += 10
    avoid_keywords = _normal_string_list(context.get("avoid_keywords"))
    if any(keyword in text.lower() for keyword in avoid_keywords):
        score -= 25
    return _clamp(score)


def _score_technical_alignment(
    tokens: set[str],
    target_keywords: list[str],
    avoid_keywords: list[str],
) -> int:
    if not target_keywords and not avoid_keywords:
        return 50
    matched = [keyword for keyword in target_keywords if keyword in tokens]
    avoided = [keyword for keyword in avoid_keywords if keyword in tokens]
    score = 55
    if target_keywords:
        score += round(40 * (len(matched) / len(target_keywords)))
    if avoided:
        score -= min(40, 15 * len(avoided))
    return _clamp(score)


def _score_seniority(role: ScorableRole, context: dict[str, Any], text: str) -> int:
    detected = _detect_seniority(text)
    target = _normal_string(context.get("target_seniority"))
    if detected is None:
        return 45
    if not target:
        return 70
    return 90 if detected == target else 45


def _score_compensation(role: ScorableRole, context: dict[str, Any]) -> int:
    if role.compensation_min is None and role.compensation_max is None:
        return 35
    target_min = _number(context.get("target_compensation_min"))
    if target_min is None:
        return 70
    role_max = role.compensation_max or role.compensation_min
    role_min = role.compensation_min or role.compensation_max
    if role_max is None or role_min is None:
        return 50
    if role_max < target_min:
        return 35
    if role_min >= target_min:
        return 90
    return 75


def _score_remote_location(role: ScorableRole, context: dict[str, Any]) -> int:
    preferred_remote = _normal_string(context.get("preferred_remote_type"))
    role_remote = _normal_string(role.remote_type)
    preferred_locations = _normal_string_list(context.get("preferred_locations"))
    location = _normal_string(role.location)
    score = 60 if role_remote or location else 45
    if preferred_remote:
        if role_remote == preferred_remote:
            score += 30
        elif preferred_remote == "remote" and role_remote in {"hybrid", "onsite", "on-site", "office"}:
            score -= 30
        else:
            score -= 10
    if preferred_locations and location:
        score += 15 if any(preferred in location for preferred in preferred_locations) else -10
    return _clamp(score)


def _score_company_signal(role: ScorableRole) -> int:
    score = 55
    company = role.company
    if getattr(company, "name", None):
        score += 15
    if getattr(company, "website_url", None):
        score += 15
    return _clamp(score)


def _score_role_clarity(text: str, concerns: list[RuleConcern]) -> int:
    score = 45
    words = _word_count(text)
    if words >= 80:
        score += 25
    elif words >= 40:
        score += 10
    responsibility_hits = sum(1 for term in RESPONSIBILITY_TERMS if term in text.lower())
    score += min(20, responsibility_hits * 5)
    if any(concern.code in {"vague_responsibilities", "generic_description"} for concern in concerns):
        score -= 20
    return _clamp(score)


def _score_application_effort(role: ScorableRole, text: str) -> int:
    score = 70
    if role.job_url:
        score += 10
    if _word_count(text) > 450:
        score -= 10
    if "cover letter" in text.lower():
        score -= 10
    return _clamp(score)


def _score_ats_alignment(
    ats_keywords: list[str],
    missing_keywords: list[str],
    target_keywords: list[str],
) -> int:
    if not target_keywords:
        return 50
    return _clamp(round(40 + 60 * (len(ats_keywords) / len(target_keywords))) - len(missing_keywords) * 2)


def _score_risk_flags(concerns: list[RuleConcern]) -> int:
    score = 90
    for concern in concerns:
        score -= 25 if concern.severity == "high" else 12
    return _clamp(score)


def _build_strengths(
    role: ScorableRole,
    dimension_scores: dict[str, int],
    ats_keywords: list[str],
) -> list[dict[str, Any]]:
    strengths = []
    for dimension, score in dimension_scores.items():
        if score >= 80:
            strengths.append(
                {
                    "code": f"{dimension}_strong",
                    "dimension": dimension,
                    "message": f"{dimension.replace('_', ' ').title()} is a strong baseline signal.",
                    "score": score,
                }
            )
    if ats_keywords:
        strengths.append(
            {
                "code": "target_keywords_matched",
                "dimension": StrideDimension.ATS_RESUME_ALIGNMENT.value,
                "message": "The role description includes requested target keywords.",
                "keywords": ats_keywords,
            }
        )
    if role.compensation_min is not None or role.compensation_max is not None:
        strengths.append(
            {
                "code": "compensation_present",
                "dimension": StrideDimension.COMPENSATION_ALIGNMENT.value,
                "message": "The role includes compensation information.",
            }
        )
    return strengths


def _build_summary(
    role: ScorableRole,
    overall_score: int,
    recommendation: str,
    confidence_level: str,
) -> str:
    return (
        f"Deterministic STRIDE baseline for {role.title} at {role.company.name}: "
        f"{overall_score}/100, recommendation {recommendation}, "
        f"{confidence_level} confidence."
    )


def _section(score: int, status: str, notes: str, **extra: Any) -> dict[str, Any]:
    return {
        "status": status,
        "score": score,
        "notes": notes,
        **extra,
    }


def _detected_signals(
    role: ScorableRole,
    text: str,
    ats_keywords: list[str],
) -> dict[str, Any]:
    return {
        "seniority": _detect_seniority(text),
        "remote_type": role.remote_type,
        "has_compensation": role.compensation_min is not None or role.compensation_max is not None,
        "description_word_count": _word_count(text),
        "matched_target_keywords": ats_keywords,
    }


def _detect_seniority(text: str) -> str | None:
    lowered = text.lower()
    for term, label in SENIORITY_TERMS.items():
        if re.search(rf"\b{re.escape(term)}\b", lowered):
            return label
    return None


def _role_text(role: ScorableRole) -> str:
    parts = [
        role.title,
        role.location or "",
        role.remote_type or "",
        role.normalized_description or role.raw_description or "",
    ]
    return " ".join(part for part in parts if part).strip()


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#.]+", text.lower())


def _word_count(text: str) -> int:
    return len(_tokens(text))


def _normal_string(value: Any) -> str:
    return str(value).strip().lower().replace("_", "-") if value is not None else ""


def _normal_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [_normal_string(value)]
    if isinstance(value, list):
        return [_normal_string(item) for item in value if _normal_string(item)]
    return []


def _number(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _clamp(score: int) -> int:
    return max(0, min(100, score))
