from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.constants import ApplicationWorkflowState
from app.models import Application, ArtifactPerformanceRecord, Role, User
from app.seed import DEFAULT_LOCAL_USER_ID
from app.services.artifact_performance import summarize_artifact_records
from app.services.search_health import generate_search_health_signals


class RecommendationError(Exception):
    pass


class RecommendationSeedMissingError(RecommendationError):
    pass


class RecommendationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        user = self.db.get(User, DEFAULT_LOCAL_USER_ID)
        if user is None or user.deleted_at is not None:
            raise RecommendationSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            )
        return user

    def list_recommendations(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        roles = self._roles(user_id=user.id, workspace_id=workspace_id)
        applications = self._applications(user_id=user.id, workspace_id=workspace_id)
        artifacts = self._artifact_records(user_id=user.id, workspace_id=workspace_id)
        latest_stride = {}
        health_signals = generate_search_health_signals(
            applications=applications,
            roles=roles,
            latest_stride=latest_stride,
            now=datetime.now(timezone.utc),
        )
        recommendations = generate_recommendations(
            roles=roles,
            applications=applications,
            artifact_records=artifacts,
            health_signals=health_signals,
            now=datetime.now(timezone.utc),
        )
        return {
            "workspace_id": workspace_id,
            "recommendations": recommendations,
            "read_only": True,
        }

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
                .options(joinedload(Application.role), selectinload(Application.interview_stages))
            )
        )

    def _artifact_records(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> list[ArtifactPerformanceRecord]:
        filters = [ArtifactPerformanceRecord.user_id == user_id]
        if workspace_id is not None:
            filters.append(ArtifactPerformanceRecord.workspace_id == workspace_id)
        return list(self.db.scalars(select(ArtifactPerformanceRecord).where(*filters)))


def generate_recommendations(
    *,
    roles: list[Role],
    applications: list[Application],
    artifact_records: list[ArtifactPerformanceRecord],
    health_signals: list[dict[str, Any]],
    now: datetime,
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    recommendations.extend(_opportunity_recommendations(roles, applications, now))
    recommendations.extend(_artifact_recommendations(artifact_records))
    recommendations.extend(_workflow_recommendations(health_signals))
    return recommendations[:12]


def _opportunity_recommendations(
    roles: list[Role],
    applications: list[Application],
    now: datetime,
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    application_by_role = {application.role_id: application for application in applications}
    for role in roles:
        intelligence = (role.parse_metadata or {}).get("opportunityIntelligence")
        categories = intelligence.get("categories", []) if isinstance(intelligence, dict) else []
        if "Duplicate / Overlap" in categories:
            recommendations.append(
                _recommendation(
                    "opportunity",
                    "role",
                    role.id,
                    "archive",
                    "Review duplicate opportunity",
                    f"{role.title} is marked as a possible duplicate or overlap.",
                    "Opportunity intelligence detected duplicate/overlap signals.",
                    "Moderate Confidence",
                    source_inputs={"categories": categories},
                )
            )
        elif "Archive Candidate" in categories:
            recommendations.append(
                _recommendation(
                    "opportunity",
                    "role",
                    role.id,
                    "deprioritize",
                    "Deprioritize risky opportunity",
                    f"{role.title} has several caution signals.",
                    "Opportunity intelligence assigned Archive Candidate based on deterministic signals.",
                    "Weak Signal",
                    source_inputs={"categories": categories},
                )
            )
        application = application_by_role.get(role.id)
        if application and _needs_follow_up(application, now):
            recommendations.append(
                _recommendation(
                    "opportunity",
                    "application",
                    application.id,
                    "follow_up",
                    "Review follow-up timing",
                    f"{role.title} has been applied without a recorded response for more than a week.",
                    "Application applied date is older than seven days and no interview/offer signal is present.",
                    "Weak Signal",
                    source_inputs={"applied_at": application.applied_at.isoformat() if application.applied_at else None},
                )
            )
    return recommendations


def _artifact_recommendations(
    records: list[ArtifactPerformanceRecord],
) -> list[dict[str, Any]]:
    summary = summarize_artifact_records(records)
    eligible = [
        metric
        for metric in summary["by_variant"]
        if metric["total"] >= 3 and (metric["response_rate"] or 0) > 0
    ]
    if not eligible:
        return []
    best = max(eligible, key=lambda metric: metric["response_rate"] or 0)
    return [
        _recommendation(
            "artifact",
            "artifact_variant",
            None,
            "reuse",
            "Reuse a higher-traction artifact variant",
            f"{best['label']} has the strongest observed response rate among variants with enough usage.",
            "Observed artifact performance by variant; this is correlation, not causation.",
            "Weak Signal" if best["total"] < 6 else "Moderate Confidence",
            source_inputs={"variant": best["label"], "uses": best["total"], "response_rate": best["response_rate"]},
        )
    ]


def _workflow_recommendations(
    health_signals: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    signal_types = {signal["signal_type"]: signal for signal in health_signals}
    if "heavy_low_fit_focus" in signal_types:
        signal = signal_types["heavy_low_fit_focus"]
        recommendations.append(
            _recommendation(
                "workflow",
                "search",
                None,
                "increase_selectivity",
                "Increase selectivity before adding volume",
                "Search health detected a heavy focus on low-fit submissions.",
                signal["basis"],
                signal["confidence"],
                source_inputs=signal["source_inputs"],
            )
        )
    if "stale_opportunities" in signal_types:
        signal = signal_types["stale_opportunities"]
        recommendations.append(
            _recommendation(
                "workflow",
                "search",
                None,
                "review_stale_opportunities",
                "Review stale opportunities",
                "Some saved roles may need an archive, revisit, or pause decision.",
                signal["basis"],
                signal["confidence"],
                source_inputs=signal["source_inputs"],
            )
        )
    return recommendations


def _needs_follow_up(application: Application, now: datetime) -> bool:
    if application.applied_at is None:
        return False
    if application.current_state in {
        ApplicationWorkflowState.INTERVIEWING.value,
        ApplicationWorkflowState.OFFER.value,
        ApplicationWorkflowState.REJECTED.value,
        ApplicationWorkflowState.WITHDRAWN.value,
        ApplicationWorkflowState.ARCHIVED.value,
    }:
        return False
    return application.applied_at < now - timedelta(days=7)


def _recommendation(
    recommendation_type: str,
    subject_type: str,
    subject_id: uuid.UUID | None,
    action: str,
    title: str,
    reason: str,
    basis: str,
    confidence: str,
    *,
    source_inputs: dict[str, Any],
) -> dict[str, Any]:
    stable_id = f"{recommendation_type}:{subject_type}:{subject_id or action}:{action}"
    return {
        "id": stable_id,
        "recommendation_type": recommendation_type,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "action": action,
        "title": title,
        "reason": reason,
        "basis": basis,
        "confidence": confidence,
        "source_inputs": source_inputs,
    }
