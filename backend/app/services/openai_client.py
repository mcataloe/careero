from typing import Any

from app.config import Settings


class OpenAIClientUnavailableError(RuntimeError):
    pass


def create_openai_client(settings: Settings) -> Any:
    if not settings.openai_api_key:
        raise OpenAIClientUnavailableError("OpenAI API key is not configured")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise OpenAIClientUnavailableError(
            "OpenAI SDK is not installed; install backend requirements"
        ) from exc

    return OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
    )
