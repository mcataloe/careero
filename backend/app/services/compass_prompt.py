import json
from decimal import Decimal
from typing import Any

from app.models import ResumeSourceVersion, Role
from app.services.compass_rules import CompassRuleResult


PROMPT_VERSION = "phase_2c_grounded_prompt_v1"

COMPASS_RULES_TEXT = """
COMPASS evaluates role fit, risk, positioning, and application priority using:
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
Use only the role data, deterministic baseline, user context, and active resume
source supplied in this request. Workspace context is scoped to this workspace
only and must not be copied from other searches. Do not invent resume facts, user experience,
company facts, compensation facts, or external research. If the supplied data is
insufficient, return an insufficient_data status with a brief reason. Identify
gaps instead of inventing experience. Distinguish strong_match, partial_match,
no_evidence, and insufficient_data. Do not generate resumes, cover letters,
outreach messages, or application artifacts.
""".strip()


def build_compass_evaluation_prompt(
    *,
    role: Role,
    baseline: CompassRuleResult,
    user_notes: str | None,
    user_context: dict[str, Any],
    workspace_context: dict[str, Any] | None = None,
    active_resume_source: ResumeSourceVersion | None = None,
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
        "workspace_context": workspace_context,
        "active_resume_source": _active_resume_source_payload(active_resume_source),
        "deterministic_baseline": _baseline_payload(baseline),
        "compass_rules": COMPASS_RULES_TEXT,
        "grounding_instructions": GROUNDING_INSTRUCTIONS,
    }

    return [
        {
            "role": "system",
            "content": (
                "You are Careero's grounded COMPASS evaluator. Return only "
                "schema-valid structured analysis."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(payload, default=str, indent=2, sort_keys=True),
        },
    ]


def _baseline_payload(baseline: CompassRuleResult) -> dict[str, Any]:
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


def _active_resume_source_payload(
    version: ResumeSourceVersion | None,
) -> dict[str, Any] | None:
    if version is None:
        return None
    return {
        "source": {
            "id": str(version.source.id),
            "name": version.source.name,
            "source_type": version.source.source_type,
        },
        "version": {
            "id": str(version.id),
            "version_label": version.version_label,
            "normalized_summary": version.normalized_summary,
            "raw_text": version.raw_text,
            "is_active": version.is_active,
        },
    }


def _string_or_none(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None
