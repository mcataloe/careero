import json
from decimal import Decimal
from typing import Any

from app.models import ResumeSourceVersion, Role, StrideEvaluation


PROMPT_VERSION = "resume_artifact_generation_v1"

TRUTHFULNESS_INSTRUCTIONS = """
Use only the supplied resume/profile source, target role, and STRIDE evaluation.
Do not invent employers, roles, dates, technologies, metrics, accomplishments,
credentials, or experience. Do not convert missing target keywords into candidate
claims unless the resume/profile source explicitly supports them. If source
material is insufficient, omit or weaken unsupported claims and record the
limitation in warnings or limitations. Return markdown resume content only; do
not render or export files.
""".strip()


def build_resume_artifact_prompt(
    *,
    role: Role,
    evaluation: StrideEvaluation,
    source_version: ResumeSourceVersion,
    workspace_context: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    payload = {
        "workspace_context": workspace_context,
        "target_role": _role_payload(role),
        "stride_evaluation": _evaluation_payload(evaluation),
        "resume_source": _source_payload(source_version),
        "truthfulness_instructions": TRUTHFULNESS_INSTRUCTIONS,
        "output_contract": {
            "title": "Short title for this tailored resume artifact.",
            "content": "Markdown resume content grounded in the source material.",
            "tailoring_notes": "Brief opportunity-specific tailoring summary or null.",
            "warnings": [
                "Truthfulness or source limitation warning. Empty list if none."
            ],
            "limitations": [
                "Insufficient source material limitation. Empty list if none."
            ],
            "unsupported_claims": [
                "Any attempted claim not grounded in the source. Empty list required."
            ],
        },
    }

    return [
        {
            "role": "system",
            "content": (
                "You are Careero's grounded resume artifact generator. Return "
                "only schema-valid structured output. Unsupported claims must be "
                "reported instead of included in resume content."
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


def _evaluation_payload(evaluation: StrideEvaluation) -> dict[str, Any]:
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
        "raw_evaluation_json": _safe_raw_evaluation(evaluation.raw_evaluation_json),
    }


def _source_payload(source_version: ResumeSourceVersion) -> dict[str, Any]:
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


def _safe_raw_evaluation(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "ai_result": raw.get("ai_result"),
        "deterministic_baseline": raw.get("deterministic_baseline"),
        "limitations": raw.get("limitations"),
        "risk_flags": raw.get("risk_flags"),
    }


def _string_or_none(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None
