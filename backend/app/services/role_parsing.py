from __future__ import annotations

import logging
from typing import Any

from pydantic import ValidationError

from app.config import Settings, get_settings
from app.schemas.role_parsing import (
    ParsedRole,
    RoleParseAIOutput,
    RoleParseMetadata,
    RoleParseRequest,
    RoleParseResponse,
)
from app.services.openai_client import (
    OpenAIClientUnavailableError,
    create_openai_client,
)
from app.services.role_parsing_prompt import (
    ROLE_PARSER_VERSION,
    build_role_parsing_prompt,
)

logger = logging.getLogger(__name__)


class RoleParsingError(Exception):
    pass


class RoleParsingUnavailableError(RoleParsingError):
    pass


class RoleParsingProviderError(RoleParsingError):
    pass


class RoleParsingValidationError(RoleParsingError):
    pass


class RoleParsingService:
    def __init__(self, settings: Settings | None = None, client: Any | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = client

    def parse(self, payload: RoleParseRequest) -> RoleParseResponse:
        if not self.settings.enable_ai_role_parsing:
            raise RoleParsingUnavailableError("AI role parsing is disabled")
        if not self.settings.openai_api_key:
            raise RoleParsingUnavailableError("OpenAI API key is not configured")

        try:
            client = self.client or create_openai_client(self.settings)
            response = client.responses.parse(
                model=self.settings.openai_default_role_parsing_model,
                input=build_role_parsing_prompt(payload),
                text_format=RoleParseAIOutput,
                max_output_tokens=self.settings.openai_max_output_tokens,
                **self._model_options(),
            )
            parsed = getattr(response, "output_parsed", None)
            if parsed is None:
                details = self._missing_parsed_output_details(response)
                logger.warning("Role parsing response was not parseable: %s", details)
                raise RoleParsingValidationError(
                    f"Role parser did not return parseable output: {details}"
                )
            if not isinstance(parsed, RoleParseAIOutput):
                parsed = RoleParseAIOutput.model_validate(parsed)
        except OpenAIClientUnavailableError as exc:
            raise RoleParsingUnavailableError(str(exc)) from exc
        except ValidationError as exc:
            logger.warning(
                "Role parsing response validation failed: %s",
                type(exc).__name__,
            )
            raise RoleParsingValidationError("Role parser returned invalid data") from exc
        except RoleParsingValidationError:
            raise
        except Exception as exc:
            logger.warning("Role parsing provider failed: %s", type(exc).__name__)
            raise RoleParsingProviderError("Role parser provider request failed") from exc

        parsed = self._apply_request_defaults(parsed, payload)
        return RoleParseResponse(
            parsed=self._to_public_parsed_role(parsed),
            metadata=RoleParseMetadata(
                parserVersion=ROLE_PARSER_VERSION,
                model=self.settings.openai_default_role_parsing_model,
            ),
        )

    def _apply_request_defaults(
        self,
        parsed: RoleParseAIOutput,
        request: RoleParseRequest,
    ) -> RoleParseAIOutput:
        data = parsed.model_dump()
        if data.get("job_url") is None and request.job_url is not None:
            data["job_url"] = request.job_url
        if data.get("source") is None and request.source is not None:
            data["source"] = request.source
        return RoleParseAIOutput.model_validate(data)

    def _to_public_parsed_role(self, parsed: RoleParseAIOutput) -> ParsedRole:
        data = parsed.model_dump(by_alias=True)
        data["confidence"] = parsed.confidence.model_dump(
            by_alias=True,
            exclude_none=True,
        )
        return ParsedRole.model_validate(data)

    def _model_options(self) -> dict[str, Any]:
        model = self.settings.openai_default_role_parsing_model.lower()
        if model.startswith("gpt-5"):
            return {"reasoning": {"effort": "minimal"}}
        return {}

    def _missing_parsed_output_details(self, response: Any) -> str:
        status = getattr(response, "status", None)
        incomplete_reason = self._incomplete_reason(response)
        output_types = self._output_types(response)
        refusal = self._refusal_summary(response)
        reasoning_tokens = self._reasoning_tokens(response)

        parts: list[str] = []
        if status:
            if status == "incomplete" and incomplete_reason:
                parts.append(f"incomplete {incomplete_reason}")
            else:
                parts.append(f"status {status}")
        if refusal:
            parts.append(f"refusal {refusal}")
        if output_types:
            parts.append(f"output types {','.join(output_types)}")
        if reasoning_tokens is not None:
            parts.append(f"reasoning tokens {reasoning_tokens}")
        return "; ".join(parts) if parts else "missing output_parsed"

    def _incomplete_reason(self, response: Any) -> str | None:
        incomplete_details = getattr(response, "incomplete_details", None)
        if incomplete_details is None:
            return None
        if isinstance(incomplete_details, dict):
            reason = incomplete_details.get("reason")
        else:
            reason = getattr(incomplete_details, "reason", None)
        return str(reason) if reason else None

    def _output_types(self, response: Any) -> list[str]:
        output = getattr(response, "output", None)
        if not output:
            return []
        output_types: list[str] = []
        for item in output:
            item_type = self._field_value(item, "type")
            if item_type:
                output_types.append(str(item_type))
            content = self._field_value(item, "content")
            if not content:
                continue
            for content_item in content:
                content_type = self._field_value(content_item, "type")
                if content_type:
                    output_types.append(str(content_type))
        return output_types

    def _refusal_summary(self, response: Any) -> str | None:
        output = getattr(response, "output", None)
        if not output:
            return None
        for item in output:
            content = self._field_value(item, "content")
            if not content:
                continue
            for content_item in content:
                refusal = self._field_value(content_item, "refusal")
                if refusal:
                    return "present"
                if self._field_value(content_item, "type") == "refusal":
                    return "present"
        return None

    def _reasoning_tokens(self, response: Any) -> int | None:
        usage = getattr(response, "usage", None)
        output_token_details = self._field_value(usage, "output_tokens_details")
        if output_token_details is None:
            return None
        value = self._field_value(output_token_details, "reasoning_tokens")
        if isinstance(value, int):
            return value
        return None

    def _field_value(self, value: Any, field: str) -> Any:
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get(field)
        return getattr(value, field, None)
