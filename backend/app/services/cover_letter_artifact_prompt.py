import json
from decimal import Decimal
from typing import Any

from app.models import ResumeSourceVersion, Role, StrideEvaluation


PROMPT_VERSION = "cover_letter_artifact_generation_v1"

NEUTRAL_TONE_INSTRUCTIONS = """
Use a neutral, forward-looking professional tone for cold applications. Do not
open with overly enthusiastic phrasing such as "I'm excited to apply" or "I am
thrilled". Prefer direct phrasing such as "I'm writing to be considered for..."
or an equivalent professional opening.
""".strip()

TRUTHFULNESS_INSTRUCTIONS = """
Use only the supplied role/opportunity, optional STRIDE evaluation, and optional
resume/profile source. Do not invent employers, roles, dates, technologies,
metrics, accomplishments, credentials, or experience. If no resume/profile
source is supplied, avoid candidate-specific claims beyond generic application
intent and opportunity-facing interest. Report unsupported claims instead of
including them in the cover letter.
""".strip()


def build_cover_letter_artifact_prompt(
    *,
    role: Role,
    tone: str,
    evaluation: StrideEvaluation | None = None,
    source_version: ResumeSourceVersion | None = None,
) -> list[dict[str, str]]:
    payload = {
        "target_role": _role_payload(role),
        "stride_evaluation": _evaluation_payload(evaluation),
        "resume_source": _source_payload(source_version),
        "tone": tone,
        "tone_instructions": NEUTRAL_TONE_INSTRUCTIONS
        if tone == "direct"
        else "Use the requested tone while remaining professional and truthful.",
        "truthfulness_instructions": TRUTHFULNESS_INSTRUCTIONS,
        "output_contract": {
            "title": "Short title for this cover letter artifact.",
            "content": "Markdown/plain text cover letter content grounded in inputs.",
            "warnings": [
                "Truthfulness, missing source, or missing evaluation warning. Empty list if none."
            ],
            "limitations": [
                "Insufficient source material limitation. Empty list if none."
            ],
            "unsupported_claims": [
                "Any attempted claim not grounded in the inputs. Empty list required."
            ],
        },
    }

    return [
        {
            "role": "system",
            "content": (
                "You are Careero's grounded cover letter artifact generator. "
                "Return only schema-valid structured output. Unsupported claims "
                "must be reported instead of included in the letter."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(payload, default=str, indent=2, sort_keys=True),
        },
    ]


def _role_payload(role: Role) -> dict[str, Any]:
    return {
        "id": str(role.id),
        "title": role.title,
        "company": {
            "name": role.company.name if role.company else None,
            "website_url": role.company.website_url if role.company else None,
        },
        "job_url": role.job_url,
        "location": role.location,
        "remote_type": role.remote_type,
        "compensation": {
            "min": _string_or_none(role.compensation_min),
            "max": _string_or_none(role.compensation_max),
            "currency": role.compensation_currency,
        },
        "raw_description": role.raw_description,
        "normalized_description": role.normalized_description,
    }


def _evaluation_payload(evaluation: StrideEvaluation | None) -> dict[str, Any] | None:
    if evaluation is None:
        return None
    return {
        "id": str(evaluation.id),
        "summary": evaluation.summary,
        "overall_score": _string_or_none(evaluation.overall_score),
        "recommendation": evaluation.recommendation,
        "confidence_level": evaluation.confidence_level,
        "strengths": evaluation.strengths,
        "concerns": evaluation.concerns,
        "resume_alignment": evaluation.resume_alignment,
        "technical_alignment": evaluation.technical_alignment,
        "ats_keywords": evaluation.ats_keywords,
        "missing_keywords": evaluation.missing_keywords,
    }


def _source_payload(
    source_version: ResumeSourceVersion | None,
) -> dict[str, Any] | None:
    if source_version is None:
        return None
    return {
        "source": {
            "id": str(source_version.source_id),
            "name": source_version.source.name if source_version.source else None,
            "source_type": (
                source_version.source.source_type if source_version.source else None
            ),
        },
        "version": {
            "id": str(source_version.id),
            "version_label": source_version.version_label,
            "normalized_summary": source_version.normalized_summary,
            "raw_text": source_version.raw_text,
        },
    }


def _string_or_none(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None
