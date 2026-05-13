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
            )
            parsed = getattr(response, "output_parsed", None)
            if parsed is None:
                raise RoleParsingValidationError(
                    "Role parser response did not include parsed output"
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
