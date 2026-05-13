from __future__ import annotations

import logging
import re
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.config import Settings
from app.constants import StrideConfidenceLevel, StrideRecommendation
from app.models import Role
from app.schemas.stride_evaluations import StrideEvaluationCreate
from app.services.openai_client import (
    OpenAIClientUnavailableError,
    create_openai_client,
)
from app.services.stride_prompt import build_stride_evaluation_prompt
from app.services.stride_rules import StrideRuleResult

logger = logging.getLogger(__name__)


class AIStrideItem(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=1000)
    evidence: str | None = Field(default=None, max_length=2000)
    status: Literal["grounded", "insufficient_data"] = "grounded"


class AIStrideSection(BaseModel):
    status: Literal["grounded", "insufficient_data"]
    score: int | None = Field(default=None, ge=0, le=100)
    notes: str = Field(min_length=1, max_length=2000)
    evidence: list[str] = Field(default_factory=list, max_length=8)


class AIStrideEvaluationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=3000)
    strengths: list[AIStrideItem] = Field(default_factory=list, max_length=12)
    concerns: list[AIStrideItem] = Field(default_factory=list, max_length=12)
    resume_alignment: AIStrideSection
    compensation_alignment: AIStrideSection
    seniority_alignment: AIStrideSection
    remote_alignment: AIStrideSection
    technical_alignment: AIStrideSection
    company_risk: AIStrideSection
    ats_keywords: list[str] = Field(default_factory=list, max_length=40)
    missing_keywords: list[str] = Field(default_factory=list, max_length=40)
    ai_overall_score: int | None = Field(default=None, ge=0, le=100)
    ai_recommendation: StrideRecommendation | None = None
    ai_confidence_level: StrideConfidenceLevel | None = None
    grounding_notes: list[str] = Field(default_factory=list, max_length=12)


class OpenAIStrideEvaluator:
    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        self.settings = settings
        self.client = client

    def enrich(
        self,
        *,
        role: Role,
        payload: StrideEvaluationCreate,
        baseline: StrideRuleResult,
    ) -> dict[str, Any]:
        if not self.settings.enable_ai_evaluations:
            return self._skipped("AI evaluations are disabled")
        if not self.settings.openai_api_key:
            return self._skipped("OpenAI API key is not configured")

        try:
            client = self.client or create_openai_client(self.settings)
            prompt = build_stride_evaluation_prompt(
                role=role,
                baseline=baseline,
                user_notes=payload.user_notes,
                user_context=payload.user_context,
            )
            response = client.responses.parse(
                model=self.settings.openai_default_evaluation_model,
                input=prompt,
                text_format=AIStrideEvaluationOutput,
                max_output_tokens=self.settings.openai_max_output_tokens,
            )
            parsed = getattr(response, "output_parsed", None)
            if parsed is None:
                raise ValueError("OpenAI response did not include parsed output")
            if not isinstance(parsed, AIStrideEvaluationOutput):
                parsed = AIStrideEvaluationOutput.model_validate(parsed)
        except (OpenAIClientUnavailableError, ValidationError, ValueError) as exc:
            return self._failed(exc)
        except Exception as exc:
            logger.warning("OpenAI STRIDE evaluation failed: %s", type(exc).__name__)
            return self._failed(exc)

        return {
            "ai_status": "completed",
            "ai_model": self.settings.openai_default_evaluation_model,
            "ai_result": parsed.model_dump(mode="json"),
        }

    def _skipped(self, reason: str) -> dict[str, str]:
        return {
            "ai_status": "skipped",
            "ai_failure_reason": reason,
        }

    def _failed(self, exc: Exception) -> dict[str, str]:
        return {
            "ai_status": "failed",
            "ai_error_type": type(exc).__name__,
            "ai_failure_reason": _sanitize_failure_reason(str(exc)),
        }


def merge_ai_analysis(
    baseline: StrideRuleResult,
    ai_metadata: dict[str, Any],
) -> dict[str, Any]:
    result = baseline.to_persistence_dict()
    raw = dict(result["raw_evaluation_json"])
    raw["deterministic_baseline"] = {
        "overall_score": str(baseline.overall_score),
        "recommendation": baseline.recommendation,
        "confidence_level": baseline.confidence_level,
        "summary": baseline.summary,
        "strengths": baseline.strengths,
        "concerns": baseline.concerns,
        "dimension_scores": baseline.raw_evaluation_json.get("dimension_scores", {}),
    }
    raw.update(ai_metadata)

    if ai_metadata.get("ai_status") == "completed":
        ai_result = ai_metadata["ai_result"]
        result.update(
            {
                "summary": ai_result["summary"],
                "strengths": ai_result["strengths"],
                "concerns": ai_result["concerns"],
                "resume_alignment": ai_result["resume_alignment"],
                "compensation_alignment": ai_result["compensation_alignment"],
                "seniority_alignment": ai_result["seniority_alignment"],
                "remote_alignment": ai_result["remote_alignment"],
                "technical_alignment": ai_result["technical_alignment"],
                "company_risk": ai_result["company_risk"],
                "ats_keywords": ai_result["ats_keywords"],
                "missing_keywords": ai_result["missing_keywords"],
            }
        )
        raw["ai_score_context"] = {
            "ai_overall_score": ai_result.get("ai_overall_score"),
            "ai_recommendation": ai_result.get("ai_recommendation"),
            "ai_confidence_level": ai_result.get("ai_confidence_level"),
            "canonical_score_source": "deterministic_baseline",
        }

    result["overall_score"] = Decimal(result["overall_score"])
    result["recommendation"] = baseline.recommendation
    result["confidence_level"] = baseline.confidence_level
    result["raw_evaluation_json"] = raw
    return result


def _sanitize_failure_reason(reason: str) -> str:
    redacted = reason.replace("\n", " ").strip()
    redacted = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-REDACTED", redacted)
    if len(redacted) > 500:
        redacted = redacted[:497] + "..."
    return redacted or "OpenAI evaluation failed"
