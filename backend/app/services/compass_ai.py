from __future__ import annotations

import logging
import re
import threading
import time
from decimal import Decimal
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.config import Settings
from app.constants import CompassConfidenceLevel, CompassRecommendation
from app.models import ResumeSourceVersion, Role
from app.schemas.compass_evaluations import CompassEvaluationCreate
from app.services.openai_client import (
    OpenAIClientUnavailableError,
    create_openai_client,
)
from app.services.compass_prompt import build_compass_evaluation_prompt
from app.services.compass_rules import CompassRuleResult

logger = logging.getLogger(__name__)

_session_counter_lock = threading.Lock()
_ai_evaluations_this_session = 0


class AICompassItem(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=1000)
    evidence: str | None = Field(default=None, max_length=2000)
    status: Literal[
        "strong_match",
        "partial_match",
        "no_evidence",
        "insufficient_data",
        "grounded",
    ] = "grounded"


class AICompassSection(BaseModel):
    status: Literal["strong_match", "partial_match", "no_evidence", "insufficient_data", "grounded"]
    score: int | None = Field(default=None, ge=0, le=100)
    notes: str = Field(min_length=1, max_length=2000)
    evidence: list[str] = Field(default_factory=list, max_length=8)


class AICompassEvaluationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=3000)
    strengths: list[AICompassItem] = Field(default_factory=list, max_length=12)
    concerns: list[AICompassItem] = Field(default_factory=list, max_length=12)
    resume_alignment: AICompassSection
    compensation_alignment: AICompassSection
    seniority_alignment: AICompassSection
    remote_alignment: AICompassSection
    technical_alignment: AICompassSection
    company_risk: AICompassSection
    ats_keywords: list[str] = Field(default_factory=list, max_length=40)
    missing_keywords: list[str] = Field(default_factory=list, max_length=40)
    evidence_matches: list[AICompassItem] = Field(default_factory=list, max_length=20)
    evidence_gaps: list[AICompassItem] = Field(default_factory=list, max_length=20)
    positioning_opportunities: list[AICompassItem] = Field(
        default_factory=list,
        max_length=20,
    )
    unsupported_claim_warnings: list[AICompassItem] = Field(
        default_factory=list,
        max_length=20,
    )
    ai_overall_score: int | None = Field(default=None, ge=0, le=100)
    ai_recommendation: CompassRecommendation | None = None
    ai_confidence_level: CompassConfidenceLevel | None = None
    grounding_notes: list[str] = Field(default_factory=list, max_length=12)


class OpenAICompassEvaluator:
    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        self.settings = settings
        self.client = client

    def enrich(
        self,
        *,
        role: Role,
        payload: CompassEvaluationCreate,
        baseline: CompassRuleResult,
        active_resume_source: ResumeSourceVersion | None = None,
        workspace_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.settings.enable_ai_evaluations:
            return self._skipped("AI evaluations are disabled", ai_enabled=False)
        if not self.settings.openai_api_key:
            return self._skipped("OpenAI API key is not configured", ai_enabled=True)
        if not _try_consume_ai_evaluation(self.settings.max_ai_evaluations_per_session):
            return self._skipped(
                "AI evaluation session limit reached",
                ai_enabled=True,
            )

        prompt: list[dict[str, str]] | None = None
        started_at = time.perf_counter()
        try:
            client = self.client or create_openai_client(self.settings)
            prompt = build_compass_evaluation_prompt(
                role=role,
                baseline=baseline,
                user_notes=payload.user_notes,
                user_context=payload.user_context,
                workspace_context=workspace_context,
                active_resume_source=active_resume_source,
            )
            response = client.responses.parse(
                model=self.settings.openai_default_evaluation_model,
                input=prompt,
                text_format=AICompassEvaluationOutput,
                max_output_tokens=self.settings.openai_max_output_tokens,
            )
            usage = getattr(response, "usage", None)
            parsed = getattr(response, "output_parsed", None)
            if parsed is None:
                raise ValueError("OpenAI response did not include parsed output")
            if not isinstance(parsed, AICompassEvaluationOutput):
                parsed = AICompassEvaluationOutput.model_validate(parsed)
        except (OpenAIClientUnavailableError, ValidationError, ValueError) as exc:
            return self._failed(exc, prompt=prompt, started_at=started_at)
        except Exception as exc:
            logger.warning("OpenAI COMPASS evaluation failed: %s", type(exc).__name__)
            return self._failed(exc, prompt=prompt, started_at=started_at)

        output_payload = parsed.model_dump(mode="json")
        return {
            "ai_status": "completed",
            "ai_enabled": True,
            "ai_model": self.settings.openai_default_evaluation_model,
            "ai_latency_ms": _elapsed_ms(started_at),
            "ai_input_token_estimate": _usage_value(
                usage,
                "input_tokens",
                fallback=_estimate_tokens(prompt),
            ),
            "ai_output_token_estimate": _usage_value(
                usage,
                "output_tokens",
                fallback=_estimate_tokens(output_payload),
            ),
            "ai_result": output_payload,
        }

    def _skipped(self, reason: str, *, ai_enabled: bool) -> dict[str, Any]:
        return {
            "ai_status": "skipped",
            "ai_enabled": ai_enabled,
            "ai_model": self.settings.openai_default_evaluation_model if ai_enabled else None,
            "ai_failure_reason": reason,
        }

    def _failed(
        self,
        exc: Exception,
        *,
        prompt: list[dict[str, str]] | None,
        started_at: float,
    ) -> dict[str, Any]:
        return {
            "ai_status": "failed",
            "ai_enabled": True,
            "ai_model": self.settings.openai_default_evaluation_model,
            "ai_latency_ms": _elapsed_ms(started_at),
            "ai_input_token_estimate": _estimate_tokens(prompt),
            "ai_output_token_estimate": None,
            "ai_error_type": type(exc).__name__,
            "ai_failure_reason": _sanitize_failure_reason(str(exc)),
        }


def merge_ai_analysis(
    baseline: CompassRuleResult,
    ai_metadata: dict[str, Any],
    active_resume_source: ResumeSourceVersion | None = None,
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
    raw["active_resume_source"] = _active_resume_source_metadata(active_resume_source)
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


def _active_resume_source_metadata(
    version: ResumeSourceVersion | None,
) -> dict[str, Any] | None:
    if version is None:
        return None
    return {
        "source_id": str(version.source_id),
        "source_name": version.source.name,
        "source_type": version.source.source_type,
        "version_id": str(version.id),
        "version_label": version.version_label,
    }


def _sanitize_failure_reason(reason: str) -> str:
    redacted = reason.replace("\n", " ").strip()
    redacted = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-REDACTED", redacted)
    if len(redacted) > 500:
        redacted = redacted[:497] + "..."
    return redacted or "OpenAI evaluation failed"


def reset_ai_evaluation_session_counter() -> None:
    global _ai_evaluations_this_session
    with _session_counter_lock:
        _ai_evaluations_this_session = 0


def _try_consume_ai_evaluation(limit: int) -> bool:
    global _ai_evaluations_this_session
    with _session_counter_lock:
        if _ai_evaluations_this_session >= limit:
            return False
        _ai_evaluations_this_session += 1
        return True


def _elapsed_ms(started_at: float) -> int:
    return max(0, round((time.perf_counter() - started_at) * 1000))


def _estimate_tokens(payload: Any) -> int | None:
    if payload is None:
        return None
    text = payload if isinstance(payload, str) else json.dumps(payload, default=str)
    return max(1, round(len(text) / 4))


def _usage_value(usage: Any, name: str, *, fallback: int | None) -> int | None:
    if usage is None:
        return fallback
    value = getattr(usage, name, None)
    if value is None and isinstance(usage, dict):
        value = usage.get(name)
    return int(value) if value is not None else fallback
