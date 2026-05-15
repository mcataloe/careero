from __future__ import annotations

from typing import Any

from app.models import Workspace


ACTIVE_WORKSPACE_STATUSES = {"active", "paused"}


def is_workspace_active_for_new_work(workspace: Workspace) -> bool:
    return (
        workspace.archived_at is None
        and workspace.status in ACTIVE_WORKSPACE_STATUSES
    )


def workspace_user_context(workspace: Workspace) -> dict[str, Any]:
    preferences = workspace.preferences or {}
    context: dict[str, Any] = {}

    _copy_if_present(
        context,
        preferences,
        "preferred_remote_type",
        "preferredRemoteTypes",
        first=True,
    )
    _copy_if_present(
        context,
        preferences,
        "preferred_locations",
        "preferredLocations",
    )
    _copy_if_present(
        context,
        preferences,
        "target_seniority",
        "targetSeniority",
        first=True,
    )
    _copy_if_present(context, preferences, "target_keywords", "targetKeywords")
    _copy_if_present(context, preferences, "avoid_keywords", "avoidKeywords")

    compensation = preferences.get("targetCompensation")
    if isinstance(compensation, dict) and compensation.get("min") is not None:
        context["target_compensation_min"] = str(compensation["min"])

    if preferences.get("notes"):
        context["workspace_notes"] = preferences["notes"]
    if workspace.ai_context_summary:
        context["workspace_ai_context_summary"] = workspace.ai_context_summary

    metadata = workspace.workspace_metadata or {}
    context_preferences = metadata.get("contextPreferences")
    if isinstance(context_preferences, dict):
        context["workspace_context_preferences"] = context_preferences

    context["workspace"] = workspace_prompt_context(workspace)
    return context


def workspace_prompt_context(workspace: Workspace) -> dict[str, Any]:
    return {
        "id": str(workspace.id),
        "title": workspace.title,
        "description": workspace.description,
        "workspace_type": workspace.workspace_type,
        "status": workspace.status,
        "preferences": workspace.preferences or {},
        "ai_context_summary": workspace.ai_context_summary,
        "tags": workspace.tags or [],
        "metadata": workspace.workspace_metadata or {},
    }


def merge_workspace_context(
    *,
    workspace: Workspace,
    request_context: dict[str, Any],
) -> dict[str, Any]:
    merged = workspace_user_context(workspace)
    merged.update(request_context or {})
    return merged


def _copy_if_present(
    target: dict[str, Any],
    source: dict[str, Any],
    target_key: str,
    source_key: str,
    *,
    first: bool = False,
) -> None:
    value = source.get(source_key)
    if not value:
        return
    if first and isinstance(value, list):
        target[target_key] = value[0] if value else None
    else:
        target[target_key] = value
