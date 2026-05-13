import json
from decimal import Decimal
from typing import Any

from app.models import Role
from app.services.stride_rules import StrideRuleResult


STRIDE_RULES_TEXT = """
STRIDE evaluates role fit, risk, positioning, and application priority using:
- strategic fit
- technical alignment
- seniority alignment
- compensation alignment
- remote/location alignment
- company signal
- role clarity
- application effort
- ATS/resume alignment
- risk flags

Recommendation thresholds:
- apply: deterministic score 75+, medium/high confidence, no severe risks
- monitor: deterministic score 55-74 with acceptable risk
- needs_review: deterministic score 40-54, low confidence, or conflicting signals
- skip: deterministic score below 40 or severe risk flags
""".strip()

GROUNDING_INSTRUCTIONS = """
Use only the role data, deterministic baseline, and user context supplied in this
request. Do not invent resume facts, user experience, company facts,
compensation facts, or external research. If the supplied data is insufficient,
return an insufficient_data status with a brief reason. Do not generate resumes,
cover letters, outreach messages, or application artifacts.
""".strip()


def build_stride_evaluation_prompt(
    *,
    role: Role,
    baseline: StrideRuleResult,
    user_notes: str | None,
    user_context: dict[str, Any],
) -> list[dict[str, str]]:
    payload = {
        "role": {
            "title": role.title,
            "company": {
                "name": role.company.name,
                "website_url": role.company.website_url,
            },
            "location": role.location,
            "remote_type": role.remote_type,
            "compensation": {
                "min": _string_or_none(role.compensation_min),
                "max": _string_or_none(role.compensation_max),
                "currency": role.compensation_currency,
            },
            "job_url": role.job_url,
            "raw_description": role.raw_description,
            "normalized_description": role.normalized_description,
            "metadata": {
                "status": role.status,
                "date_found": role.date_found.isoformat() if role.date_found else None,
                "date_posted": (
                    role.date_posted.isoformat() if role.date_posted else None
                ),
            },
        },
        "user_notes": user_notes,
        "user_context": user_context,
        "deterministic_baseline": _baseline_payload(baseline),
        "stride_rules": STRIDE_RULES_TEXT,
        "grounding_instructions": GROUNDING_INSTRUCTIONS,
    }

    return [
        {
            "role": "system",
            "content": (
                "You are Careero's grounded STRIDE evaluator. Return only "
                "schema-valid structured analysis."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(payload, default=str, indent=2, sort_keys=True),
        },
    ]


def _baseline_payload(baseline: StrideRuleResult) -> dict[str, Any]:
    return {
        "overall_score": str(baseline.overall_score),
        "recommendation": baseline.recommendation,
        "confidence_level": baseline.confidence_level,
        "summary": baseline.summary,
        "strengths": baseline.strengths,
        "concerns": baseline.concerns,
        "dimension_scores": baseline.raw_evaluation_json.get("dimension_scores", {}),
        "risk_flags": baseline.raw_evaluation_json.get("risk_flags", []),
        "limitations": baseline.raw_evaluation_json.get("limitations", []),
    }


def _string_or_none(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None
