from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Role, User, Workspace
from app.services.current_user import CurrentUserResolutionError, resolve_current_user


class CompensationIntelligenceError(Exception):
    pass


class CompensationIntelligenceSeedMissingError(CompensationIntelligenceError):
    pass


class CompensationIntelligenceWorkspaceNotFoundError(CompensationIntelligenceError):
    pass


class CompensationIntelligenceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise CompensationIntelligenceSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def get_compensation_intelligence(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        workspace = self._workspace(user.id, workspace_id)
        roles = self._roles(user_id=user.id, workspace_id=workspace_id)
        observations = [compensation_observation(role) for role in roles]
        target = _target_compensation(workspace)
        insights = build_compensation_insights(
            observations=observations,
            target_compensation_min=target,
            workspace=workspace,
        )
        insufficient_data = []
        if len([item for item in observations if item["midpoint"] is not None]) < 3:
            insufficient_data.append(
                "Compensation intelligence needs at least three stated ranges for trend comparison."
            )
        return {
            "workspace_id": workspace_id,
            "target_compensation_min": target,
            "observations": observations,
            "insights": insights,
            "insufficient_data": insufficient_data,
        }

    def _workspace(
        self,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> Workspace | None:
        if workspace_id is None:
            return None
        workspace = self.db.scalar(
            select(Workspace).where(
                Workspace.id == workspace_id,
                Workspace.user_id == user_id,
            )
        )
        if workspace is None:
            raise CompensationIntelligenceWorkspaceNotFoundError("Workspace not found")
        return workspace

    def _roles(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> list[Role]:
        filters = [Role.user_id == user_id, Role.deleted_at.is_(None)]
        if workspace_id is not None:
            filters.append(Role.workspace_id == workspace_id)
        return list(self.db.scalars(select(Role).where(*filters).order_by(Role.date_found.asc(), Role.created_at.asc())))


def compensation_observation(role: Role) -> dict[str, Any]:
    low = float(role.compensation_min) if role.compensation_min is not None else None
    high = float(role.compensation_max) if role.compensation_max is not None else None
    midpoint = None
    if low is not None or high is not None:
        midpoint = ((low if low is not None else high) + (high if high is not None else low)) / 2
    metadata = role.parse_metadata or {}
    employment_type = metadata.get("employmentType")
    return {
        "role_id": role.id,
        "title": role.title,
        "compensation_min": low,
        "compensation_max": high,
        "midpoint": midpoint,
        "currency": role.compensation_currency,
        "employment_type": employment_type if isinstance(employment_type, str) else None,
        "remote_type": role.remote_type,
        "source_basis": "stated_range" if midpoint is not None else "not_stated",
    }


def build_compensation_insights(
    *,
    observations: list[dict[str, Any]],
    target_compensation_min: float | None,
    workspace: Workspace | None,
) -> list[dict[str, Any]]:
    insights: list[dict[str, Any]] = []
    stated = [item for item in observations if item["midpoint"] is not None]
    if target_compensation_min is not None:
        under_target = [
            item for item in stated if item["midpoint"] < target_compensation_min
        ]
        if under_target:
            insights.append(
                _insight(
                    "Under-target compensation",
                    "Some saved opportunities state compensation below the workspace target.",
                    "Compares known stated compensation midpoints to the user's workspace target.",
                    "Weak Signal" if len(stated) < 5 else "Moderate Confidence",
                    severity="caution",
                    source_inputs={
                        "under_target": len(under_target),
                        "stated_ranges": len(stated),
                        "target": target_compensation_min,
                    },
                )
            )
    if len(stated) >= 3 and stated[-1]["midpoint"] < stated[0]["midpoint"] - 15000:
        insights.append(
            _insight(
                "Compensation decline trend",
                "Stated compensation appears lower in newer saved opportunities.",
                "Compares first and latest stated compensation midpoints in saved-role order.",
                "Weak Signal",
                severity="caution",
                source_inputs={
                    "first_midpoint": stated[0]["midpoint"],
                    "latest_midpoint": stated[-1]["midpoint"],
                },
            )
        )
    inflated = [
        item
        for item in stated
        if _title_floor(item["title"]) is not None
        and item["midpoint"] < _title_floor(item["title"])
    ]
    if inflated:
        insights.append(
            _insight(
                "Scope/compensation mismatch",
                "Some senior-scope titles are paired with comparatively low stated compensation.",
                "Uses internal title-scope heuristics against stated compensation; this is not external market data.",
                "Weak Signal",
                severity="caution",
                source_inputs={"mismatches": len(inflated)},
            )
        )
    contract_mismatch = [
        item
        for item in stated
        if item["employment_type"] in {"contract", "consulting", "fractional"}
        and workspace is not None
        and workspace.workspace_type.startswith("full_time")
    ]
    if contract_mismatch:
        insights.append(
            _insight(
                "Contract versus full-time assumptions",
                "Some compensation ranges come from contract/consulting roles inside a full-time search track.",
                "Compares parsed employment type metadata against workspace type.",
                "Weak Signal",
                source_inputs={"contract_like_roles": len(contract_mismatch)},
            )
        )
    if workspace is not None and workspace.workspace_type == "contract_consulting":
        full_time = [
            item for item in observations if item["employment_type"] == "full_time"
        ]
        if full_time:
            insights.append(
                _insight(
                    "Advisory/consulting assumptions",
                    "Some roles in this consulting track appear to be full-time opportunities.",
                    "Compares parsed employment type metadata against workspace type.",
                    "Weak Signal",
                    source_inputs={"full_time_roles": len(full_time)},
                )
            )
    return insights


def _insight(
    label: str,
    message: str,
    basis: str,
    confidence: str,
    *,
    severity: str = "info",
    source_inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "label": label,
        "message": message,
        "basis": basis,
        "confidence": confidence,
        "severity": severity,
        "source_inputs": source_inputs or {},
    }


def _target_compensation(workspace: Workspace | None) -> float | None:
    if workspace is None:
        return None
    target = (workspace.preferences or {}).get("targetCompensation")
    if isinstance(target, dict) and target.get("min") is not None:
        return float(target["min"])
    return None


def _title_floor(title: str) -> float | None:
    value = title.lower()
    if any(term in value for term in ["principal", "director"]):
        return 170000
    if "staff" in value:
        return 160000
    if "senior" in value:
        return 140000
    return None
