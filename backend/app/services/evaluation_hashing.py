from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

from app.models import ResumeSourceVersion, Role


def role_content_hash(role: Role) -> str:
    return _hash_payload(
        {
            "title": role.title,
            "company": {
                "id": str(role.company_id),
                "name": role.company.name if role.company else None,
                "website_url": role.company.website_url if role.company else None,
            },
            "source": {
                "id": str(role.source_id) if role.source_id else None,
                "name": role.source.name if role.source else None,
                "source_type": role.source.source_type if role.source else None,
                "website_url": role.source.website_url if role.source else None,
            },
            "job_url": role.job_url,
            "location": role.location,
            "remote_type": role.remote_type,
            "compensation_min": _string_or_none(role.compensation_min),
            "compensation_max": _string_or_none(role.compensation_max),
            "compensation_currency": role.compensation_currency,
            "raw_description": role.raw_description,
            "normalized_description": role.normalized_description,
            "status": role.status,
            "date_found": role.date_found.isoformat() if role.date_found else None,
            "date_posted": role.date_posted.isoformat() if role.date_posted else None,
        }
    )


def resume_source_hash(version: ResumeSourceVersion | None) -> str | None:
    if version is None:
        return None
    return _hash_payload(
        {
            "source_id": str(version.source_id),
            "source_name": version.source.name if version.source else None,
            "source_type": version.source.source_type if version.source else None,
            "version_id": str(version.id),
            "version_label": version.version_label,
            "normalized_summary": version.normalized_summary,
            "raw_text": version.raw_text,
            "is_active": version.is_active,
        }
    )


def evaluation_input_hash(
    *,
    role_hash: str,
    source_hash: str | None,
    user_notes: str | None,
    user_context: dict[str, Any],
    prompt_version: str,
    ruleset_version: str,
    ai_enabled: bool,
    model_name: str,
    workspace_id: str | None = None,
    workspace_context: dict[str, Any] | None = None,
) -> str:
    return _hash_payload(
        {
            "role_content_hash": role_hash,
            "source_hash": source_hash,
            "workspace_id": workspace_id,
            "workspace_context": workspace_context or {},
            "user_notes": user_notes,
            "user_context": user_context,
            "prompt_version": prompt_version,
            "ruleset_version": ruleset_version,
            "ai_enabled": ai_enabled,
            "model_name": model_name,
        }
    )


def _hash_payload(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _string_or_none(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None
