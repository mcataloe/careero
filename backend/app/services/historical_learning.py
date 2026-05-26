from __future__ import annotations

import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.constants import ApplicationWorkflowState
from app.models import Application, ArtifactPerformanceRecord, Role, User, Workspace
from app.services.artifact_performance import summarize_artifact_records
from app.services.current_user import CurrentUserResolutionError, resolve_current_user


class HistoricalLearningError(Exception):
    pass


class HistoricalLearningSeedMissingError(HistoricalLearningError):
    pass


class HistoricalLearningService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise HistoricalLearningSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def get_historical_learning(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        workspaces = self._workspaces(user.id, workspace_id)
        roles = self._roles(user_id=user.id, workspace_id=workspace_id)
        applications = self._applications(user_id=user.id, workspace_id=workspace_id)
        artifact_records = self._artifact_records(user_id=user.id, workspace_id=workspace_id)
        summaries = build_historical_summaries(
            workspaces=workspaces,
            roles=roles,
            applications=applications,
            artifact_records=artifact_records,
            now=datetime.now(timezone.utc),
        )
        insufficient_data = []
        if not workspaces:
            insufficient_data.append("Historical learning is strongest after a search track is archived or completed.")
        if len(applications) < 3:
            insufficient_data.append("Historical summaries need more tracked application outcomes.")
        return {
            "workspace_id": workspace_id,
            "summaries": summaries,
            "insufficient_data": insufficient_data,
        }

    def _workspaces(
        self,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> list[Workspace]:
        filters = [Workspace.user_id == user_id]
        if workspace_id is not None:
            filters.append(Workspace.id == workspace_id)
        else:
            filters.append(Workspace.status.in_(["archived", "completed"]))
        return list(self.db.scalars(select(Workspace).where(*filters)))

    def _roles(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> list[Role]:
        filters = [Role.user_id == user_id]
        if workspace_id is not None:
            filters.append(Role.workspace_id == workspace_id)
        return list(self.db.scalars(select(Role).where(*filters).options(joinedload(Role.company))))

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
                .options(joinedload(Application.role).joinedload(Role.company), selectinload(Application.interview_stages))
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


def build_historical_summaries(
    *,
    workspaces: list[Workspace],
    roles: list[Role],
    applications: list[Application],
    artifact_records: list[ArtifactPerformanceRecord],
    now: datetime,
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    summaries.extend(_role_category_response_summary(applications))
    summaries.extend(_artifact_summary(artifact_records))
    summaries.extend(_company_ghosting_summary(applications, now))
    summaries.extend(_interview_pipeline_summary(applications))
    summaries.extend(_low_roi_emotional_cost_summary(roles, applications))
    summaries.append(
        _summary(
            "Historical tracks reviewed",
            len(workspaces),
            "Counts archived/completed tracks when no specific workspace filter is provided.",
            "Moderate Confidence" if workspaces else "Insufficient Data",
            source_inputs={"workspace_count": len(workspaces)},
        )
    )
    return summaries


def _role_category_response_summary(applications: list[Application]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Application]] = defaultdict(list)
    for application in applications:
        grouped[_role_category(application.role)].append(application)
    if not grouped:
        return []
    metrics = []
    for category, items in grouped.items():
        responses = sum(1 for item in items if _has_response(item))
        metrics.append((category, responses, len(items), responses / len(items)))
    best = max(metrics, key=lambda item: item[3])
    worst = min(metrics, key=lambda item: item[3])
    return [
        _summary(
            "Best responding role category",
            best[0],
            "Compares interview/offer signals by title-derived role category.",
            "Weak Signal",
            source_inputs={"responses": best[1], "total": best[2]},
        ),
        _summary(
            "Weakest responding role category",
            worst[0],
            "Compares interview/offer signals by title-derived role category.",
            "Weak Signal",
            source_inputs={"responses": worst[1], "total": worst[2]},
        ),
    ]


def _artifact_summary(records: list[ArtifactPerformanceRecord]) -> list[dict[str, Any]]:
    if not records:
        return []
    performance = summarize_artifact_records(records)
    variants = [metric for metric in performance["by_variant"] if metric["total"] > 0]
    if not variants:
        return []
    best = max(variants, key=lambda metric: metric["response_rate"] or 0)
    return [
        _summary(
            "Best observed artifact variant",
            best["label"],
            "Uses observed artifact response rate; this is correlation, not causation.",
            "Weak Signal",
            source_inputs={"uses": best["total"], "response_rate": best["response_rate"]},
        )
    ]


def _company_ghosting_summary(
    applications: list[Application],
    now: datetime,
) -> list[dict[str, Any]]:
    counts = Counter()
    for application in applications:
        if (
            application.applied_at is not None
            and application.applied_at < now - timedelta(days=21)
            and not _has_response(application)
            and application.current_state != ApplicationWorkflowState.REJECTED.value
        ):
            counts[application.role.company.name] += 1
    if not counts:
        return []
    company, count = counts.most_common(1)[0]
    return [
        _summary(
            "Most repeated no-response company",
            company,
            "Counts older submitted applications without interview, offer, rejection, or withdrawal signals.",
            "Weak Signal",
            source_inputs={"no_response_applications": count},
        )
    ]


def _interview_pipeline_summary(applications: list[Application]) -> list[dict[str, Any]]:
    interviewed = [application for application in applications if _has_response(application)]
    if not interviewed:
        return []
    titles = [application.role.title for application in interviewed[:5]]
    return [
        _summary(
            "Roles that led to interviews",
            len(interviewed),
            "Counts applications with interview stage, interviewing state, or offer state.",
            "Moderate Confidence",
            source_inputs={"sample_titles": titles},
        )
    ]


def _low_roi_emotional_cost_summary(
    roles: list[Role],
    applications: list[Application],
) -> list[dict[str, Any]]:
    response_by_role = {application.role_id: _has_response(application) for application in applications}
    costly = [
        role
        for role in roles
        if _has_burnout_phrase(role.raw_description or role.normalized_description or "")
        and response_by_role.get(role.id) is False
    ]
    if not costly:
        return []
    return [
        _summary(
            "High-friction low-ROI pattern",
            len(costly),
            "Counts roles with sustainability-risk phrasing and no recorded response.",
            "Weak Signal",
            source_inputs={"roles": [role.title for role in costly[:5]]},
        )
    ]


def _summary(
    label: str,
    value: str | int | float | None,
    basis: str,
    confidence: str,
    *,
    source_inputs: dict[str, Any],
) -> dict[str, Any]:
    return {
        "label": label,
        "value": value,
        "basis": basis,
        "confidence": confidence,
        "source_inputs": source_inputs,
    }


def _has_response(application: Application) -> bool:
    return application.current_state in {
        ApplicationWorkflowState.INTERVIEWING.value,
        ApplicationWorkflowState.OFFER.value,
    } or bool(application.interview_stages)


def _role_category(role: Role) -> str:
    title = role.title.lower()
    if any(term in title for term in ["manager", "director", "head of"]):
        return "leadership"
    if any(term in title for term in ["platform", "infrastructure", "devops"]):
        return "infrastructure"
    if "data" in title:
        return "data"
    return "software_engineering"


def _has_burnout_phrase(text: str) -> bool:
    value = text.lower()
    return any(
        phrase in value
        for phrase in ["high pressure", "nights and weekends", "always on", "work hard play hard"]
    )
