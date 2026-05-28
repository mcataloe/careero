from __future__ import annotations

import uuid
from collections import Counter
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.constants import ApplicationWorkflowState
from app.models import Application, Role, CompassEvaluation, User, Workspace
from app.services.current_user import CurrentUserResolutionError, resolve_current_user
from app.services.insight_governance import generated_timestamp, governed_insight


class CompassInsightsError(Exception):
    pass


class CompassInsightsSeedMissingError(CompassInsightsError):
    pass


class CompassInsightsWorkspaceNotFoundError(CompassInsightsError):
    pass


class CompassInsightsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise CompassInsightsSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def get_compass_insights(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        workspace = self._workspace(user.id, workspace_id)
        evaluations = self._evaluations(user_id=user.id, workspace_id=workspace_id)
        applications = self._applications(user_id=user.id, workspace_id=workspace_id)
        points = [_trend_point(evaluation) for evaluation in evaluations]
        insights = build_compass_trend_insights(
            points=points,
            applications=applications,
            workspace=workspace,
        )
        scores = [
            point["overall_score"]
            for point in points
            if point["overall_score"] is not None
        ]
        insufficient_data = []
        if len(points) < 3:
            insufficient_data.append(
                "At least three COMPASS evaluations are recommended for search-level trend insight."
            )
        if not scores:
            insufficient_data.append("Completed COMPASS evaluations need overall scores.")
        return {
            "generated_at": generated_timestamp(),
            "workspace_id": workspace_id,
            "average_compass_score": round(sum(scores) / len(scores), 1)
            if scores
            else None,
            "trend_points": points,
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
            raise CompassInsightsWorkspaceNotFoundError("Workspace not found")
        return workspace

    def _evaluations(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> list[CompassEvaluation]:
        filters = [
            CompassEvaluation.user_id == user_id,
            CompassEvaluation.deleted_at.is_(None),
            CompassEvaluation.evaluation_status == "completed",
        ]
        if workspace_id is not None:
            filters.append(CompassEvaluation.workspace_id == workspace_id)
        return list(
            self.db.scalars(
                select(CompassEvaluation)
                .where(*filters)
                .options(joinedload(CompassEvaluation.role))
                .order_by(CompassEvaluation.created_at.asc())
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
        return list(self.db.scalars(select(Application).where(*filters)))


def build_compass_trend_insights(
    *,
    points: list[dict[str, Any]],
    applications: list[Application],
    workspace: Workspace | None,
) -> list[dict[str, Any]]:
    insights: list[dict[str, Any]] = []
    insights.extend(_score_trend_insights(points))
    insights.extend(_compensation_drift_insights(points, workspace))
    insights.extend(_seniority_drift_insights(points, workspace))
    insights.extend(_search_focus_insights(points))
    insights.extend(_low_fit_submission_insights(points, applications))
    insights.extend(_contradictory_goal_insights(points, workspace))
    return insights


def _trend_point(evaluation: CompassEvaluation) -> dict[str, Any]:
    role = evaluation.role
    return {
        "role_id": evaluation.role_id,
        "created_at": evaluation.created_at.isoformat(),
        "overall_score": float(evaluation.overall_score)
        if evaluation.overall_score is not None
        else None,
        "compensation_midpoint": _compensation_midpoint(role),
        "seniority_level": _seniority_level(role.title),
        "role_category": _role_category(role),
    }


def _score_trend_insights(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scores = [point["overall_score"] for point in points if point["overall_score"] is not None]
    if len(scores) < 3:
        return [
            _insight(
                "COMPASS sample is thin",
                "Search-level COMPASS direction is still a weak signal.",
                "Fewer than three completed COMPASS scores are available.",
                "Insufficient Data",
                source_inputs={"score_count": len(scores)},
            )
        ]
    delta = scores[-1] - scores[0]
    if abs(delta) < 5:
        message = "Average fit appears broadly stable across evaluated roles."
    elif delta > 0:
        message = "Evaluated role fit is trending upward; compare newer roles to the earlier lower-fit group."
    else:
        message = "Evaluated role fit is trending downward; review whether search scope has drifted."
    return [
        _insight(
            "Average COMPASS fit over time",
            message,
            "Compares the first and latest COMPASS overall scores in evaluation order.",
            "Moderate Confidence" if len(scores) >= 6 else "Weak Signal",
            source_inputs={"first_score": scores[0], "latest_score": scores[-1], "count": len(scores)},
        )
    ]


def _compensation_drift_insights(
    points: list[dict[str, Any]],
    workspace: Workspace | None,
) -> list[dict[str, Any]]:
    values = [point["compensation_midpoint"] for point in points if point["compensation_midpoint"] is not None]
    if len(values) < 3:
        return []
    delta = values[-1] - values[0]
    target = _target_compensation(workspace)
    insights = []
    if delta < -15000:
        insights.append(
            _insight(
                "Compensation drift",
                "Stated compensation on evaluated roles is moving lower; treat this as a review prompt, not a market conclusion.",
                "Compares first and latest stated compensation midpoints from saved roles.",
                "Weak Signal",
                severity="caution",
                source_inputs={"first_midpoint": values[0], "latest_midpoint": values[-1]},
            )
        )
    if target is not None and values[-1] < target * 0.85:
        insights.append(
            _insight(
                "Compensation collapse risk",
                "The latest evaluated compensation midpoint is materially below the workspace target.",
                "Compares latest stated compensation midpoint to the workspace target compensation preference.",
                "Weak Signal",
                severity="caution",
                source_inputs={"latest_midpoint": values[-1], "target": target},
            )
        )
    return insights


def _seniority_drift_insights(
    points: list[dict[str, Any]],
    workspace: Workspace | None,
) -> list[dict[str, Any]]:
    levels = [point["seniority_level"] for point in points if point["seniority_level"] is not None]
    if len(levels) < 3:
        return []
    delta = levels[-1] - levels[0]
    target = _target_seniority_level(workspace)
    insights = []
    if abs(delta) >= 2:
        direction = "higher" if delta > 0 else "lower"
        insights.append(
            _insight(
                "Role-seniority drift",
                f"Evaluated roles are moving toward {direction} seniority titles.",
                "Compares title-derived seniority levels over evaluation order.",
                "Weak Signal",
                source_inputs={"first_level": levels[0], "latest_level": levels[-1]},
            )
        )
    if target is not None and abs(levels[-1] - target) >= 2:
        insights.append(
            _insight(
                "Target seniority mismatch",
                "Latest evaluated role seniority appears far from the workspace target seniority.",
                "Compares title-derived seniority against workspace target seniority preference.",
                "Weak Signal",
                severity="caution",
                source_inputs={"latest_level": levels[-1], "target_level": target},
            )
        )
    return insights


def _search_focus_insights(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(points) < 4:
        return []
    counts = Counter(point["role_category"] for point in points)
    category, count = counts.most_common(1)[0]
    share = count / len(points)
    if share >= 0.65:
        message = f"Search focus is relatively consistent around {category} roles."
    else:
        message = "Evaluated roles span several categories; review whether that breadth is intentional."
    return [
        _insight(
            "Search-focus consistency",
            message,
            "Uses title-derived role categories from evaluated opportunities.",
            "Weak Signal",
            source_inputs={"top_category": category, "share": round(share, 2), "total": len(points)},
        )
    ]


def _low_fit_submission_insights(
    points: list[dict[str, Any]],
    applications: list[Application],
) -> list[dict[str, Any]]:
    score_by_role = {point["role_id"]: point["overall_score"] for point in points}
    submitted = [
        application
        for application in applications
        if application.current_state
        in {
            ApplicationWorkflowState.APPLIED.value,
            ApplicationWorkflowState.INTERVIEWING.value,
            ApplicationWorkflowState.OFFER.value,
            ApplicationWorkflowState.REJECTED.value,
            ApplicationWorkflowState.WITHDRAWN.value,
        }
    ]
    low_fit = [
        application
        for application in submitted
        if score_by_role.get(application.role_id) is not None
        and score_by_role[application.role_id] < 60
    ]
    if len(submitted) >= 3 and len(low_fit) / len(submitted) >= 0.5:
        return [
            _insight(
                "Excessive low-fit submissions",
                "A large share of submitted applications are attached to low COMPASS-fit roles.",
                "Counts submitted applications whose latest available COMPASS score is below 60.",
                "Weak Signal",
                severity="caution",
                source_inputs={"low_fit_submissions": len(low_fit), "submitted": len(submitted)},
            )
        ]
    return []


def _contradictory_goal_insights(
    points: list[dict[str, Any]],
    workspace: Workspace | None,
) -> list[dict[str, Any]]:
    target = _target_seniority_level(workspace)
    if target is None or len(points) < 3:
        return []
    mismatches = [
        point
        for point in points
        if point["seniority_level"] is not None
        and abs(point["seniority_level"] - target) >= 2
    ]
    if len(mismatches) >= 2:
        return [
            _insight(
                "Contradictory search goals",
                "Several evaluated roles appear far from the workspace target seniority.",
                "Compares title-derived seniority with workspace preferences; this is advisory only.",
                "Weak Signal",
                severity="caution",
                source_inputs={"mismatches": len(mismatches), "target_level": target},
            )
        ]
    return []


def _insight(
    label: str,
    message: str,
    basis: str,
    confidence: str,
    *,
    severity: str = "info",
    source_inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return governed_insight(
        category="compass",
        label=label,
        message=message,
        basis=basis,
        confidence=confidence,
        severity=severity,
        source_inputs=source_inputs,
    )


def _compensation_midpoint(role: Role) -> float | None:
    if role.compensation_min is None and role.compensation_max is None:
        return None
    low = float(role.compensation_min or role.compensation_max or 0)
    high = float(role.compensation_max or role.compensation_min or 0)
    return (low + high) / 2


def _seniority_level(title: str) -> int:
    value = title.lower()
    if any(term in value for term in ["director", "head of", "vp"]):
        return 5
    if any(term in value for term in ["principal", "staff"]):
        return 4
    if "senior" in value:
        return 3
    if any(term in value for term in ["junior", "associate", "entry"]):
        return 1
    return 2


def _role_category(role: Role) -> str:
    title = role.title.lower()
    if any(term in title for term in ["manager", "director", "head of"]):
        return "leadership"
    if any(term in title for term in ["platform", "infrastructure", "devops"]):
        return "infrastructure"
    if any(term in title for term in ["data", "analytics", "machine learning"]):
        return "data"
    return "software_engineering"


def _target_compensation(workspace: Workspace | None) -> float | None:
    if workspace is None:
        return None
    compensation = (workspace.preferences or {}).get("targetCompensation")
    if isinstance(compensation, dict) and compensation.get("min") is not None:
        return float(compensation["min"])
    return None


def _target_seniority_level(workspace: Workspace | None) -> int | None:
    if workspace is None:
        return None
    target = (workspace.preferences or {}).get("targetSeniority")
    if isinstance(target, list) and target:
        target = target[0]
    if not isinstance(target, str):
        return None
    return _seniority_level(target)
