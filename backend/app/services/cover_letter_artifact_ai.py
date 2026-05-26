from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.config import Settings, get_settings
from app.models import ResumeSourceVersion, Role, CompassEvaluation
from app.services.cover_letter_artifact_prompt import (
    build_cover_letter_artifact_prompt,
)
from app.services.openai_client import (
    OpenAIClientUnavailableError,
    create_openai_client,
)

logger = logging.getLogger(__name__)


class CoverLetterArtifactGenerationError(Exception):
    pass


class CoverLetterArtifactGenerationUnavailableError(
    CoverLetterArtifactGenerationError
):
    pass


class CoverLetterArtifactProviderError(CoverLetterArtifactGenerationError):
    pass


class CoverLetterArtifactOutputValidationError(
    CoverLetterArtifactGenerationError
):
    pass


class AICoverLetterArtifactOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=20000)
    warnings: list[str] = Field(default_factory=list, max_length=20)
    limitations: list[str] = Field(default_factory=list, max_length=20)
    unsupported_claims: list[str] = Field(default_factory=list, max_length=20)


class OpenAICoverLetterArtifactGenerator:
    def __init__(self, settings: Settings | None = None, client: Any | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = client

    def generate(
        self,
        *,
        role: Role,
        tone: str,
        evaluation: CompassEvaluation | None = None,
        source_version: ResumeSourceVersion | None = None,
        workspace_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.settings.enable_ai_cover_letter_generation:
            raise CoverLetterArtifactGenerationUnavailableError(
                "AI cover letter generation is disabled"
            )
        if not self.settings.openai_api_key:
            raise CoverLetterArtifactGenerationUnavailableError(
                "OpenAI API key is not configured"
            )

        prompt: list[dict[str, str]] | None = None
        started_at = time.perf_counter()
        try:
            client = self.client or create_openai_client(self.settings)
            prompt = build_cover_letter_artifact_prompt(
                role=role,
                tone=tone,
                evaluation=evaluation,
                source_version=source_version,
                workspace_context=workspace_context,
            )
            response = client.responses.parse(
                model=self.settings.openai_default_cover_letter_generation_model,
                input=prompt,
                text_format=AICoverLetterArtifactOutput,
                max_output_tokens=self.settings.openai_max_output_tokens,
            )
            usage = getattr(response, "usage", None)
            parsed = getattr(response, "output_parsed", None)
            if parsed is None:
                raise CoverLetterArtifactOutputValidationError(
                    "Cover letter generator response did not include parsed output"
                )
            if not isinstance(parsed, AICoverLetterArtifactOutput):
                parsed = AICoverLetterArtifactOutput.model_validate(parsed)
        except OpenAIClientUnavailableError as exc:
            raise CoverLetterArtifactGenerationUnavailableError(str(exc)) from exc
        except (ValidationError, CoverLetterArtifactOutputValidationError) as exc:
            logger.warning(
                "Cover letter artifact output validation failed: %s",
                type(exc).__name__,
            )
            raise CoverLetterArtifactOutputValidationError(
                "Cover letter generator returned invalid data"
            ) from exc
        except Exception as exc:
            logger.warning("Cover letter artifact provider failed: %s", type(exc).__name__)
            raise CoverLetterArtifactProviderError(
                _sanitize_failure_reason(
                    "Cover letter generator provider request failed"
                )
            ) from exc

        output_payload = parsed.model_dump(mode="json")
        return {
            "status": "completed",
            "model": self.settings.openai_default_cover_letter_generation_model,
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
    return redacted or "Cover letter artifact generation failed"


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
