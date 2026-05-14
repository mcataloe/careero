from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.config import Settings, get_settings
from app.models import ResumeSourceVersion, Role, StrideEvaluation
from app.services.openai_client import (
    OpenAIClientUnavailableError,
    create_openai_client,
)
from app.services.resume_artifact_prompt import build_resume_artifact_prompt

logger = logging.getLogger(__name__)


class ResumeArtifactGenerationError(Exception):
    pass


class ResumeArtifactGenerationUnavailableError(ResumeArtifactGenerationError):
    pass


class ResumeArtifactProviderError(ResumeArtifactGenerationError):
    pass


class ResumeArtifactOutputValidationError(ResumeArtifactGenerationError):
    pass


class AIResumeArtifactOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=30000)
    tailoring_notes: str | None = Field(default=None, max_length=5000)
    warnings: list[str] = Field(default_factory=list, max_length=20)
    limitations: list[str] = Field(default_factory=list, max_length=20)
    unsupported_claims: list[str] = Field(default_factory=list, max_length=20)


class OpenAIResumeArtifactGenerator:
    def __init__(self, settings: Settings | None = None, client: Any | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = client

    def generate(
        self,
        *,
        role: Role,
        evaluation: StrideEvaluation,
        source_version: ResumeSourceVersion,
    ) -> dict[str, Any]:
        if not self.settings.enable_ai_resume_generation:
            raise ResumeArtifactGenerationUnavailableError(
                "AI resume generation is disabled"
            )
        if not self.settings.openai_api_key:
            raise ResumeArtifactGenerationUnavailableError(
                "OpenAI API key is not configured"
            )

        prompt: list[dict[str, str]] | None = None
        started_at = time.perf_counter()
        try:
            client = self.client or create_openai_client(self.settings)
            prompt = build_resume_artifact_prompt(
                role=role,
                evaluation=evaluation,
                source_version=source_version,
            )
            response = client.responses.parse(
                model=self.settings.openai_default_resume_generation_model,
                input=prompt,
                text_format=AIResumeArtifactOutput,
                max_output_tokens=self.settings.openai_max_output_tokens,
            )
            usage = getattr(response, "usage", None)
            parsed = getattr(response, "output_parsed", None)
            if parsed is None:
                raise ResumeArtifactOutputValidationError(
                    "Resume generator response did not include parsed output"
                )
            if not isinstance(parsed, AIResumeArtifactOutput):
                parsed = AIResumeArtifactOutput.model_validate(parsed)
        except OpenAIClientUnavailableError as exc:
            raise ResumeArtifactGenerationUnavailableError(str(exc)) from exc
        except (ValidationError, ResumeArtifactOutputValidationError) as exc:
            logger.warning(
                "Resume artifact output validation failed: %s",
                type(exc).__name__,
            )
            raise ResumeArtifactOutputValidationError(
                "Resume generator returned invalid data"
            ) from exc
        except Exception as exc:
            logger.warning("Resume artifact provider failed: %s", type(exc).__name__)
            raise ResumeArtifactProviderError(
                _sanitize_failure_reason("Resume generator provider request failed")
            ) from exc

        output_payload = parsed.model_dump(mode="json")
        return {
            "status": "completed",
            "model": self.settings.openai_default_resume_generation_model,
            "latency_ms": _elapsed_ms(started_at),
            "input_token_estimate": _usage_value(
                usage,
                "input_tokens",
                fallback=_estimate_tokens(prompt),
            ),
            "output_token_estimate": _usage_value(
                usage,
                "output_tokens",
                fallback=_estimate_tokens(output_payload),
            ),
            "output": output_payload,
        }


def _sanitize_failure_reason(reason: str) -> str:
    redacted = reason.replace("\n", " ").strip()
    redacted = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-REDACTED", redacted)
    if len(redacted) > 500:
        redacted = redacted[:497] + "..."
    return redacted or "Resume artifact generation failed"


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
