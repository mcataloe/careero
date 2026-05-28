from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.constants import ApplicationWorkflowState
from app.models import (
    Application,
    ApplicationNote,
    ApplicationReminder,
    ApplicationStateHistory,
    Role,
    CompassEvaluation,
    User,
    Workspace,
)
from app.services.current_user import CurrentUserResolutionError, resolve_current_user
from app.services.insight_governance import generated_timestamp, governed_insight


RESPONSE_STATES = {
    ApplicationWorkflowState.INTERVIEWING.value,
    ApplicationWorkflowState.OFFER.value,
}
SUBMITTED_OR_LATER_STATES = {
    ApplicationWorkflowState.APPLIED.value,
    ApplicationWorkflowState.INTERVIEWING.value,
    ApplicationWorkflowState.OFFER.value,
    ApplicationWorkflowState.REJECTED.value,
    ApplicationWorkflowState.WITHDRAWN.value,
}
STAGE_PAIRS = (
    (ApplicationWorkflowState.DISCOVERED.value, ApplicationWorkflowState.INTERESTED.value),
    (ApplicationWorkflowState.INTERESTED.value, ApplicationWorkflowState.APPLIED.value),
    (ApplicationWorkflowState.APPLIED.value, ApplicationWorkflowState.INTERVIEWING.value),
    (ApplicationWorkflowState.INTERVIEWING.value, ApplicationWorkflowState.OFFER.value),
)


class SearchAnalyticsError(Exception):
    pass


class SearchAnalyticsSeedMissingError(SearchAnalyticsError):
    pass


class SearchAnalyticsWorkspaceNotFoundError(SearchAnalyticsError):
    pass


class SearchAnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise SearchAnalyticsSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def get_search_analytics(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        workspace = None
        if workspace_id is not None:
            workspace = self.db.scalar(
                select(Workspace).where(
                    Workspace.id == workspace_id,
                    Workspace.user_id == user.id,
                )
            )
            if workspace is None:
                raise SearchAnalyticsWorkspaceNotFoundError("Workspace not found")

        roles = self._roles(user_id=user.id, workspace_id=workspace_id)
        applications = self._applications(user_id=user.id, workspace_id=workspace_id)
        latest_compass = self._latest_compass_by_role(
            user_id=user.id,
            workspace_id=workspace_id,
        )

        submitted = [
            application
            for application in applications
            if _has_reached(application, ApplicationWorkflowState.APPLIED.value)
        ]
        responded = [application for application in applications if _has_response(application)]
        archived = [
            application
            for application in applications
            if application.archived_at is not None
            or application.current_state == ApplicationWorkflowState.ARCHIVED.value
        ]
        recruiter_contacts = self._count_recruiter_contacts(
            user_id=user.id,
            workspace_id=workspace_id,
        )
        completed_followups = self._count_completed_followups(
            user_id=user.id,
            workspace_id=workspace_id,
        )

        summary = {
            "opportunities_saved": _metric(
                len(roles),
                "Opportunities saved",
                "Active saved opportunities in the selected search scope.",
            ),
            "opportunities_archived": _metric(
                len(archived),
                "Opportunities archived",
                "Application workflows currently archived or archived at least once.",
            ),
            "applications_submitted": _metric(
                len(submitted),
                "Applications submitted",
                "Applications that reached the applied stage.",
            ),
            "interviews_received": _metric(
                len(responded),
                "Interviews or positive responses",
                "Applications with an interview stage or current workflow state of interviewing/offer.",
            ),
            "recruiter_contacts": _metric(
                recruiter_contacts,
                "Recruiter contacts",
                "Application notes tagged as recruiter interactions.",
            ),
            "followups_completed": _metric(
                completed_followups,
                "Follow-ups completed",
                "Completed application reminders.",
            ),
            "response_latency_days": _metric(
                _average_response_latency(submitted),
                "Average response latency",
                "Average days from applied date to first interview signal where both dates exist.",
            ),
        }

        conversion_rates = _stage_conversions(applications)
        average_stage_durations = _stage_durations(applications)
        segment_response_rates = [
            *_compass_response_rates(applications, latest_compass),
            *_compensation_response_rates(applications, latest_compass),
        ]
        insufficient_data = _insufficient_data(
            applications=applications,
            submitted=submitted,
            latest_compass=latest_compass,
            durations=average_stage_durations,
        )

        return {
            "generated_at": generated_timestamp(),
            "workspace_id": workspace.id if workspace is not None else None,
            "scope": workspace.title if workspace is not None else "all_workspaces",
            "summary": summary,
            "conversion_rates": conversion_rates,
            "average_stage_durations": average_stage_durations,
            "segment_response_rates": segment_response_rates,
            "signals": _focus_signals(
                applications=applications,
                submitted=submitted,
                responded=responded,
                latest_compass=latest_compass,
            ),
            "insufficient_data": insufficient_data,
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
        statement = (
            select(Application)
            .where(*filters)
            .options(
                selectinload(Application.state_history),
                selectinload(Application.interview_stages),
            )
        )
        return list(self.db.scalars(statement))

    def _latest_compass_by_role(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> dict[uuid.UUID, CompassEvaluation]:
        filters = [
            CompassEvaluation.user_id == user_id,
            CompassEvaluation.deleted_at.is_(None),
            CompassEvaluation.evaluation_status == "completed",
        ]
        if workspace_id is not None:
            filters.append(CompassEvaluation.workspace_id == workspace_id)
        evaluations = self.db.scalars(
            select(CompassEvaluation)
            .where(*filters)
            .order_by(CompassEvaluation.role_id, CompassEvaluation.created_at.desc())
        )
        latest: dict[uuid.UUID, CompassEvaluation] = {}
        for evaluation in evaluations:
            latest.setdefault(evaluation.role_id, evaluation)
        return latest

    def _count_recruiter_contacts(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> int:
        filters = [
            ApplicationNote.user_id == user_id,
            ApplicationNote.deleted_at.is_(None),
            ApplicationNote.note_type == "recruiter",
        ]
        if workspace_id is not None:
            filters.append(ApplicationNote.workspace_id == workspace_id)
        return len(list(self.db.scalars(select(ApplicationNote.id).where(*filters))))

    def _count_completed_followups(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> int:
        filters = [
            ApplicationReminder.user_id == user_id,
            ApplicationReminder.completed_at.is_not(None),
        ]
        if workspace_id is not None:
            filters.append(ApplicationReminder.workspace_id == workspace_id)
        return len(list(self.db.scalars(select(ApplicationReminder.id).where(*filters))))


def _metric(value: int | float | None, label: str, basis: str) -> dict[str, Any]:
    return {"value": value, "label": label, "basis": basis}


def _rate(
    numerator: int,
    denominator: int,
    *,
    label: str,
    basis: str,
) -> dict[str, Any]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": round(numerator / denominator, 4) if denominator else None,
        "label": label,
        "basis": basis,
    }


def _has_reached(application: Application, stage: str) -> bool:
    if stage == application.current_state:
        return True
    if stage == ApplicationWorkflowState.APPLIED.value and application.applied_at is not None:
        return True
    if stage == ApplicationWorkflowState.INTERVIEWING.value and application.interview_stages:
        return True
    return any(history.to_state == stage for history in application.state_history)


def _has_response(application: Application) -> bool:
    if application.current_state in RESPONSE_STATES:
        return True
    if application.interview_stages:
        return True
    return any(history.to_state in RESPONSE_STATES for history in application.state_history)


def _first_stage_at(application: Application, stage: str) -> datetime | None:
    candidates = [
        history.changed_at for history in application.state_history if history.to_state == stage
    ]
    if stage == ApplicationWorkflowState.APPLIED.value and application.applied_at is not None:
        candidates.append(application.applied_at)
    if stage == ApplicationWorkflowState.INTERVIEWING.value:
        candidates.extend(
            stage_record.created_at for stage_record in application.interview_stages
        )
    return min(candidates) if candidates else None


def _average_response_latency(applications: list[Application]) -> float | None:
    durations: list[float] = []
    for application in applications:
        applied_at = _first_stage_at(application, ApplicationWorkflowState.APPLIED.value)
        response_at = _first_stage_at(
            application,
            ApplicationWorkflowState.INTERVIEWING.value,
        )
        if applied_at is not None and response_at is not None and response_at >= applied_at:
            durations.append((response_at - applied_at).total_seconds() / 86400)
    if not durations:
        return None
    return round(sum(durations) / len(durations), 1)


def _stage_conversions(applications: list[Application]) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    for from_stage, to_stage in STAGE_PAIRS:
        denominator = sum(1 for application in applications if _has_reached(application, from_stage))
        numerator = sum(1 for application in applications if _has_reached(application, to_stage))
        metrics.append(
            {
                "from_stage": from_stage,
                "to_stage": to_stage,
                "numerator": numerator,
                "denominator": denominator,
                "rate": round(numerator / denominator, 4) if denominator else None,
                "basis": f"Applications that reached {to_stage} divided by applications that reached {from_stage}.",
            }
        )
    return metrics


def _stage_durations(applications: list[Application]) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    for from_stage, to_stage in STAGE_PAIRS:
        durations: list[float] = []
        for application in applications:
            from_at = _first_stage_at(application, from_stage)
            to_at = _first_stage_at(application, to_stage)
            if from_at is not None and to_at is not None and to_at >= from_at:
                durations.append((to_at - from_at).total_seconds() / 86400)
        metrics.append(
            {
                "from_stage": from_stage,
                "to_stage": to_stage,
                "average_days": round(sum(durations) / len(durations), 1)
                if durations
                else None,
                "sample_size": len(durations),
                "basis": f"Average elapsed days between first {from_stage} and first {to_stage} timestamps.",
            }
        )
    return metrics


def _compass_response_rates(
    applications: list[Application],
    latest_compass: dict[uuid.UUID, CompassEvaluation],
) -> list[dict[str, Any]]:
    buckets: dict[str, list[Application]] = defaultdict(list)
    for application in applications:
        evaluation = latest_compass.get(application.role_id)
        if evaluation is None or evaluation.overall_score is None:
            continue
        score = float(evaluation.overall_score)
        if score >= 75:
            buckets["high_compass_fit"].append(application)
        elif score < 60:
            buckets["low_compass_fit"].append(application)
    return [_segment_metric(name, values, "Latest COMPASS overall score bucket.") for name, values in buckets.items()]


def _compensation_response_rates(
    applications: list[Application],
    latest_compass: dict[uuid.UUID, CompassEvaluation],
) -> list[dict[str, Any]]:
    buckets: dict[str, list[Application]] = defaultdict(list)
    for application in applications:
        evaluation = latest_compass.get(application.role_id)
        if evaluation is None:
            continue
        alignment = evaluation.compensation_alignment or {}
        status = str(
            alignment.get("status")
            or alignment.get("alignment")
            or alignment.get("label")
            or ""
        ).lower()
        if status in {"aligned", "strong", "meets_target", "above_target"}:
            buckets["compensation_aligned"].append(application)
        elif status in {"below_target", "under_target", "misaligned", "weak"}:
            buckets["compensation_risk"].append(application)
    return [_segment_metric(name, values, "Latest COMPASS compensation alignment bucket.") for name, values in buckets.items()]


def _segment_metric(
    name: str,
    applications: list[Application],
    basis: str,
) -> dict[str, Any]:
    responses = sum(1 for application in applications if _has_response(application))
    total = len(applications)
    return {
        "segment": name,
        "responses": responses,
        "total": total,
        "response_rate": round(responses / total, 4) if total else None,
        "basis": basis,
    }


def _focus_signals(
    *,
    applications: list[Application],
    submitted: list[Application],
    responded: list[Application],
    latest_compass: dict[uuid.UUID, CompassEvaluation],
) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    if len(submitted) >= 3:
        rate = len(responded) / len(submitted)
        if rate < 0.15:
            signals.append(
                governed_insight(
                    category="application_workflow",
                    label="Low observed response rate",
                    message="Recent traction appears limited; review fit and source quality before increasing application volume.",
                    basis="Interviews or positive responses divided by submitted applications.",
                    confidence="weak" if len(submitted) < 8 else "moderate",
                    source_inputs={"submitted": len(submitted), "responses": len(responded)},
                )
            )
    high_fit_apps = [
        application
        for application in applications
        if _score(latest_compass.get(application.role_id)) is not None
        and _score(latest_compass.get(application.role_id)) >= 75
    ]
    if high_fit_apps and sum(1 for app in high_fit_apps if _has_response(app)) > 0:
        signals.append(
            governed_insight(
                category="fit_alignment",
                label="High-fit opportunities are producing traction",
                message="Prioritize opportunities with similar COMPASS fit signals before expanding the search.",
                basis="At least one high-COMPASS-fit opportunity has reached an interview or offer signal.",
                confidence="weak" if len(high_fit_apps) < 5 else "moderate",
                source_inputs={"high_fit_opportunities": len(high_fit_apps)},
            )
        )
    return signals


def _score(evaluation: CompassEvaluation | None) -> float | None:
    if evaluation is None or evaluation.overall_score is None:
        return None
    value: Decimal = evaluation.overall_score
    return float(value)


def _insufficient_data(
    *,
    applications: list[Application],
    submitted: list[Application],
    latest_compass: dict[uuid.UUID, CompassEvaluation],
    durations: list[dict[str, Any]],
) -> list[str]:
    messages: list[str] = []
    if len(applications) < 3:
        messages.append("At least three tracked opportunities are recommended for meaningful search analytics.")
    if len(submitted) < 3:
        messages.append("Submission conversion is based on a thin sample.")
    if not latest_compass:
        messages.append("COMPASS response comparisons need completed COMPASS evaluations.")
    if all(metric["sample_size"] == 0 for metric in durations):
        messages.append("Average days between stages need timestamped stage transitions.")
    return messages
