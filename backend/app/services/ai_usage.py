from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AIUsageEvent, User
from app.schemas.ai_usage import AIUsageEventCreate
from app.services.current_user import (
    CurrentUserContext,
    CurrentUserResolutionError,
    get_current_user_context,
    resolve_current_user,
)


class AIUsageSeedMissingError(Exception):
    pass


class AIUsageService:
    def __init__(
        self,
        db: Session,
        current_user_context: CurrentUserContext | None = None,
    ) -> None:
        self.db = db
        self.current_user_context = current_user_context or get_current_user_context()

    def current_user(self) -> User:
        try:
            return resolve_current_user(self.db, self.current_user_context)
        except CurrentUserResolutionError as exc:
            raise AIUsageSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def record_event(self, payload: AIUsageEventCreate) -> AIUsageEvent:
        event = AIUsageEvent(
            user_id=payload.user_id,
            workspace_id=payload.workspace_id,
            opportunity_id=payload.opportunity_id,
            application_id=payload.application_id,
            artifact_id=payload.artifact_id,
            feature=payload.feature,
            event_type=payload.event_type,
            provider=payload.provider,
            model=payload.model,
            status=payload.status or payload.event_type,
            prompt_version=payload.prompt_version,
            ruleset_version=payload.ruleset_version,
            input_token_estimate=payload.input_token_estimate,
            output_token_estimate=payload.output_token_estimate,
            latency_ms=payload.latency_ms,
            error_class=sanitize_error_class(payload.error_class),
            content_hash=payload.content_hash,
            event_metadata=safe_metadata(payload.metadata),
        )
        self.db.add(event)
        return event

    def list_recent(self, *, limit: int = 50) -> list[AIUsageEvent]:
        user = self.current_user()
        normalized_limit = max(1, min(limit, 200))
        statement = (
            select(AIUsageEvent)
            .where(AIUsageEvent.user_id == user.id)
            .order_by(AIUsageEvent.created_at.desc(), AIUsageEvent.id.desc())
            .limit(normalized_limit)
        )
        return list(self.db.scalars(statement))


def usage_response(event: AIUsageEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "user_id": event.user_id,
        "workspace_id": event.workspace_id,
        "opportunity_id": event.opportunity_id,
        "role_id": event.role_id,
        "application_id": event.application_id,
        "artifact_id": event.artifact_id,
        "feature": event.feature,
        "event_type": event.event_type,
        "provider": event.provider,
        "model": event.model,
        "status": event.status,
        "prompt_version": event.prompt_version,
        "ruleset_version": event.ruleset_version,
        "input_token_estimate": event.input_token_estimate,
        "output_token_estimate": event.output_token_estimate,
        "latency_ms": event.latency_ms,
        "error_class": event.error_class,
        "content_hash": event.content_hash,
        "metadata": event.event_metadata or {},
        "created_at": event.created_at,
    }


def usage_summary(events: list[AIUsageEvent]) -> dict[str, Any]:
    by_feature: dict[str, int] = {}
    by_event_type: dict[str, int] = {}
    for event in events:
        by_feature[event.feature] = by_feature.get(event.feature, 0) + 1
        by_event_type[event.event_type] = by_event_type.get(event.event_type, 0) + 1
    return {
        "total_events": len(events),
        "by_feature": by_feature,
        "by_event_type": by_event_type,
    }


def usage_note() -> str:
    return (
        "Local AI usage metering records safe metadata only. It is not billing, "
        "credits, paid quota enforcement, or a production cost-control system."
    )


def content_hash(payload: Any) -> str:
    encoded = (
        payload.encode("utf-8")
        if isinstance(payload, str)
        else json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    )
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def event_type_for_ai_status(status: str | None, reason: str | None = None) -> str:
    normalized = (status or "").lower()
    normalized_reason = (reason or "").lower()
    if normalized == "completed":
        return "completed"
    if normalized == "failed":
        return "failed"
    if "session limit" in normalized_reason or "quota" in normalized_reason:
        return "skipped_quota"
    if normalized == "skipped":
        return "skipped_disabled"
    return "failed"


def sanitize_error_class(value: str | None) -> str | None:
    if value is None:
        return None
    value = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-REDACTED", value)
    cleaned = re.split(r"[:\\s]", value.strip(), maxsplit=1)[0]
    cleaned = re.sub(r"[^A-Za-z0-9_.-]", "", cleaned)
    return cleaned[:200] or "UnknownError"


def safe_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    allowed: dict[str, Any] = {}
    for key, value in metadata.items():
        safe_key = str(key)[:100]
        if _looks_secret(safe_key):
            continue
        if isinstance(value, str):
            allowed[safe_key] = _safe_string(value)
        elif isinstance(value, (int, float, bool)) or value is None:
            allowed[safe_key] = value
        elif isinstance(value, list):
            allowed[safe_key] = [
                _safe_string(item) if isinstance(item, str) else item
                for item in value
                if isinstance(item, (str, int, float, bool))
            ][:20]
        elif isinstance(value, dict):
            nested = {
                str(nested_key)[:100]: _safe_string(nested_value)
                if isinstance(nested_value, str)
                else nested_value
                for nested_key, nested_value in value.items()
                if isinstance(nested_value, (str, int, float, bool))
                and not _looks_secret(str(nested_key))
            }
            if nested:
                allowed[safe_key] = nested
    return allowed


def _safe_string(value: str) -> str:
    redacted = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-REDACTED", value)
    redacted = re.sub(r"postgresql(?:\\+psycopg)?://\\S+", "postgresql://REDACTED", redacted)
    return redacted[:500]


def _looks_secret(key: str) -> bool:
    normalized = key.lower()
    blocked_terms = (
        "secret",
        "api_key",
        "token",
        "password",
        "raw_prompt",
        "raw_resume",
        "raw_job",
        "raw_description",
        "private_note",
        "compensation_strategy",
    )
    return any(term in normalized for term in blocked_terms)
