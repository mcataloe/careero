from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.constants import ApplicationWorkflowState
from app.models import Application, Role, StrideEvaluation, User
from app.seed import DEFAULT_LOCAL_USER_ID


SUBMITTED_STATES = {
    ApplicationWorkflowState.APPLIED.value,
    ApplicationWorkflowState.INTERVIEWING.value,
    ApplicationWorkflowState.OFFER.value,
    ApplicationWorkflowState.REJECTED.value,
    ApplicationWorkflowState.WITHDRAWN.value,
}


class SearchHealthError(Exception):
    pass


class SearchHealthSeedMissingError(SearchHealthError):
    pass


class SearchHealthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        user = self.db.get(User, DEFAULT_LOCAL_USER_ID)
        if user is None or user.deleted_at is not None:
            raise SearchHealthSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            )
        return user

    def get_search_health(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        applications = self._applications(user_id=user.id, workspace_id=workspace_id)
        roles = self._roles(user_id=user.id, workspace_id=workspace_id)
        latest_stride = self._latest_stride_by_role(
            user_id=user.id,
            workspace_id=workspace_id,
        )
        signals = generate_search_health_signals(
            applications=applications,
            roles=roles,
            latest_stride=latest_stride,
            now=datetime.now(timezone.utc),
        )
        insufficient_data = []
        if len(applications) < 3:
            insufficient_data.append(
                "Search health guidance is limited until at least three opportunities are tracked."
            )
        return {
            "workspace_id": workspace_id,
            "signals": signals,
            "insufficient_data": insufficient_data,
        }

    def _applications(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> list[Application]:
        filters = [Application.user_id == user_id, Application.deleted_at.is_(None)]
        if workspace_id is not None:
            filters.append(Application.workspace_id == workspace_id)
        return list(
            self.db.scalars(
                select(Application)
                .where(*filters)
                .options(selectinload(Application.state_history))
            )
        )

    def _roles(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> list[Role]:
        filters = [Role.user_id == user_id, Role.deleted_at.is_(None)]
        if workspace_id is not None:
            filters.append(Role.workspace_id == workspace_id)
        return list(self.db.scalars(select(Role).where(*filters)))

    def _latest_stride_by_role(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> dict[uuid.UUID, StrideEvaluation]:
        filters = [
            StrideEvaluation.user_id == user_id,
            StrideEvaluation.deleted_at.is_(None),
            StrideEvaluation.evaluation_status == "completed",
        ]
        if workspace_id is not None:
            filters.append(StrideEvaluation.workspace_id == workspace_id)
        latest: dict[uuid.UUID, StrideEvaluation] = {}
        for evaluation in self.db.scalars(
            select(StrideEvaluation)
            .where(*filters)
            .order_by(StrideEvaluation.role_id, StrideEvaluation.created_at.desc())
        ):
            latest.setdefault(evaluation.role_id, evaluation)
        return latest


def generate_search_health_signals(
    *,
    applications: list[Application],
    roles: list[Role],
    latest_stride: dict[uuid.UUID, StrideEvaluation],
    now: datetime,
) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    submitted = [application for application in applications if _is_submitted(application)]
    recent_submitted = [
        application
        for application in submitted
        if _submitted_at(application) is not None
        and _submitted_at(application) >= now - timedelta(days=7)
    ]
    if len(recent_submitted) >= 15:
        signals.append(
            _signal(
                "excessive_application_volume",
                "High recent application volume",
                "You have submitted many applications recently.",
                "Consider pausing to review fit, source quality, and follow-up opportunities before adding more volume.",
                "Counts applications submitted in the last seven days.",
                "Weak Signal",
                severity="caution",
                source_inputs={"recent_submissions": len(recent_submitted)},
            )
        )
    low_fit_submitted = [
        application
        for application in submitted
        if _score(latest_stride.get(application.role_id)) is not None
        and _score(latest_stride.get(application.role_id)) < 60
    ]
    if len(submitted) >= 3 and len(low_fit_submitted) / len(submitted) >= 0.5:
        signals.append(
            _signal(
                "heavy_low_fit_focus",
                "Heavy focus on low-fit roles",
                "You have focused heavily on low-fit roles recently.",
                "Review whether these roles are intentional stretches or energy drains before submitting more similar applications.",
                "Compares submitted applications with STRIDE scores below 60.",
                "Weak Signal",
                severity="caution",
                source_inputs={"low_fit_submissions": len(low_fit_submitted), "submitted": len(submitted)},
            )
        )
    if applications and max(application.updated_at for application in applications) < now - timedelta(days=21):
        signals.append(
            _signal(
                "inactivity_collapse",
                "Search activity appears paused",
                "There has not been recent tracked activity.",
                "If the pause was intentional, no action is needed; otherwise, revisit the smallest set of opportunities worth reviewing.",
                "Latest application update is more than 21 days old.",
                "Weak Signal",
                source_inputs={"application_count": len(applications)},
            )
        )
    stale_roles = [
        role
        for role in roles
        if role.date_found is not None
        and role.status != "archived"
        and (now.date() - role.date_found).days >= 30
    ]
    if stale_roles:
        signals.append(
            _signal(
                "stale_opportunities",
                "Stale opportunities may need review",
                "Some saved opportunities have not moved recently.",
                "Review paused or old opportunities before expanding search volume.",
                "Counts active roles found at least 30 days ago.",
                "Weak Signal",
                source_inputs={"stale_opportunities": len(stale_roles)},
            )
        )
    burnout_risk_roles = [
        role
        for role in roles
        if _has_burnout_phrase(role.raw_description or role.normalized_description or "")
    ]
    if len(burnout_risk_roles) >= 2:
        signals.append(
            _signal(
                "burnout_risk_pattern",
                "Repeated sustainability-risk phrasing",
                "Multiple saved roles include possible sustainability-risk language.",
                "Consider prioritizing roles with clearer scope, support, and operating expectations.",
                "Counts saved roles with high-pressure, nights/weekends, always-on, or similar phrasing.",
                "Weak Signal",
                severity="caution",
                source_inputs={"roles": len(burnout_risk_roles)},
            )
        )
    return signals


def _signal(
    signal_type: str,
    label: str,
    message: str,
    guidance: str,
    basis: str,
    confidence: str,
    *,
    severity: str = "info",
    source_inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "signal_type": signal_type,
        "label": label,
        "message": message,
        "gentle_guidance": guidance,
        "basis": basis,
        "confidence": confidence,
        "severity": severity,
        "source_inputs": source_inputs or {},
    }


def _is_submitted(application: Application) -> bool:
    return application.current_state in SUBMITTED_STATES or application.applied_at is not None


def _submitted_at(application: Application) -> datetime | None:
    return application.applied_at or application.updated_at


def _score(evaluation: StrideEvaluation | None) -> float | None:
    if evaluation is None or evaluation.overall_score is None:
        return None
    return float(evaluation.overall_score)


def _has_burnout_phrase(text: str) -> bool:
    value = text.lower()
    return any(
        phrase in value
        for phrase in [
            "high pressure",
            "work hard play hard",
            "nights and weekends",
            "always on",
            "fast-paced environment",
        ]
    )
