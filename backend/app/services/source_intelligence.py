from __future__ import annotations

import uuid
from collections import defaultdict
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.constants import ApplicationWorkflowState, SOURCE_DISPLAY_NAMES
from app.models import Application, ApplicationNote, Role, CompassEvaluation, User
from app.services.current_user import CurrentUserResolutionError, resolve_current_user
from app.services.insight_governance import generated_timestamp, governed_insight


RESPONSE_STATES = {
    ApplicationWorkflowState.INTERVIEWING.value,
    ApplicationWorkflowState.OFFER.value,
}
SUBMITTED_STATES = {
    ApplicationWorkflowState.APPLIED.value,
    ApplicationWorkflowState.INTERVIEWING.value,
    ApplicationWorkflowState.OFFER.value,
    ApplicationWorkflowState.REJECTED.value,
    ApplicationWorkflowState.WITHDRAWN.value,
}


class SourceIntelligenceError(Exception):
    pass


class SourceIntelligenceSeedMissingError(SourceIntelligenceError):
    pass


class SourceIntelligenceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise SourceIntelligenceSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def get_source_intelligence(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        roles = self._roles(user_id=user.id, workspace_id=workspace_id)
        applications = self._applications(user_id=user.id, workspace_id=workspace_id)
        latest_compass = self._latest_compass_by_role(
            user_id=user.id,
            workspace_id=workspace_id,
        )
        summaries = summarize_source_performance(
            roles=roles,
            applications=applications,
            latest_compass=latest_compass,
        )
        return {
            "generated_at": generated_timestamp(),
            "workspace_id": workspace_id,
            "summaries": summaries,
            "insights": _source_insights(summaries),
            "insufficient_data": _insufficient_data(summaries),
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
        return list(
            self.db.scalars(
                select(Role).where(*filters).options(joinedload(Role.source))
            )
        )

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
                .options(
                    joinedload(Application.role).joinedload(Role.source),
                    selectinload(Application.interview_stages),
                    selectinload(Application.note_entries),
                )
            )
        )

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
        latest: dict[uuid.UUID, CompassEvaluation] = {}
        for evaluation in self.db.scalars(
            select(CompassEvaluation)
            .where(*filters)
            .order_by(CompassEvaluation.role_id, CompassEvaluation.created_at.desc())
        ):
            latest.setdefault(evaluation.role_id, evaluation)
        return latest


def summarize_source_performance(
    *,
    roles: Iterable[Role],
    applications: Iterable[Application],
    latest_compass: dict[uuid.UUID, CompassEvaluation],
) -> list[dict[str, Any]]:
    roles_by_source: dict[str, list[Role]] = defaultdict(list)
    for role in roles:
        roles_by_source[_normalized_source_type(role)].append(role)

    applications_by_source: dict[str, list[Application]] = defaultdict(list)
    for application in applications:
        applications_by_source[_normalized_source_type(application.role)].append(application)

    source_types = sorted(set(roles_by_source) | set(applications_by_source))
    return [
        _source_metric(
            source_type,
            roles_by_source[source_type],
            applications_by_source[source_type],
            latest_compass,
        )
        for source_type in source_types
    ]


def _source_metric(
    source_type: str,
    roles: list[Role],
    applications: list[Application],
    latest_compass: dict[uuid.UUID, CompassEvaluation],
) -> dict[str, Any]:
    submitted = [application for application in applications if _is_submitted(application)]
    responses = [application for application in submitted if _has_response(application)]
    interviews = [application for application in submitted if _has_interview(application)]
    scores = [
        float(evaluation.overall_score)
        for role in roles
        if (evaluation := latest_compass.get(role.id)) is not None
        and evaluation.overall_score is not None
    ]
    comp_aligned = sum(
        1
        for role in roles
        if _compensation_aligned(latest_compass.get(role.id))
    )
    recruiter_contacts = sum(_recruiter_contacts(application) for application in applications)
    return {
        "source_type": source_type,
        "label": _source_label(source_type),
        "opportunities": len(roles),
        "applications": len(submitted),
        "responses": len(responses),
        "interviews": len(interviews),
        "response_rate": round(len(responses) / len(submitted), 4)
        if submitted
        else None,
        "interview_rate": round(len(interviews) / len(submitted), 4)
        if submitted
        else None,
        "average_compass_score": round(sum(scores) / len(scores), 1)
        if scores
        else None,
        "recruiter_contacts": recruiter_contacts,
        "compensation_aligned": comp_aligned,
        "basis": "Private source summary derived from saved roles, application states, recruiter notes, and completed COMPASS evaluations.",
    }


def _source_insights(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible = [summary for summary in summaries if summary["applications"] >= 2]
    if not eligible:
        return []
    best = max(eligible, key=lambda summary: summary["response_rate"] or 0)
    return [
        governed_insight(
            category="source_intelligence",
            label="Highest observed source traction",
            message=f"{best['label']} currently has the strongest observed response rate among sources with at least two submitted applications.",
            basis="Simple private conversion by source type; this is not a public recruiter or source rating.",
            confidence="weak" if best["applications"] < 5 else "moderate",
            source_inputs={"source_type": best["source_type"], "applications": best["applications"], "response_rate": best["response_rate"]},
        )
    ]


def _insufficient_data(summaries: list[dict[str, Any]]) -> list[str]:
    if sum(summary["applications"] for summary in summaries) < 3:
        return ["Source intelligence needs at least three submitted applications before comparison is useful."]
    return []


def _normalized_source_type(role: Role) -> str:
    source_type = role.source.source_type if role.source is not None else None
    if source_type in {"linkedin_manual"}:
        return "linkedin"
    if source_type in {"greenhouse", "lever", "ashby", "workable"}:
        return "company_site"
    if source_type:
        return source_type
    return "other"


def _source_label(source_type: str) -> str:
    for enum_value, label in SOURCE_DISPLAY_NAMES.items():
        if enum_value.value == source_type:
            return label
    return source_type.replace("_", " ").title()


def _is_submitted(application: Application) -> bool:
    return application.current_state in SUBMITTED_STATES or application.applied_at is not None


def _has_response(application: Application) -> bool:
    return application.current_state in RESPONSE_STATES or bool(application.interview_stages)


def _has_interview(application: Application) -> bool:
    return _has_response(application)


def _recruiter_contacts(application: Application) -> int:
    return sum(
        1
        for note in application.note_entries
        if note.deleted_at is None and note.note_type == "recruiter"
    )


def _compensation_aligned(evaluation: CompassEvaluation | None) -> bool:
    if evaluation is None:
        return False
    alignment = evaluation.compensation_alignment or {}
    status = str(
        alignment.get("status")
        or alignment.get("alignment")
        or alignment.get("label")
        or ""
    ).lower()
    return status in {"aligned", "strong", "meets_target", "above_target"}
