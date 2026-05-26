from __future__ import annotations

import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.constants import ApplicationWorkflowState
from app.models import (
    Application,
    ArtifactPerformanceRecord,
    Role,
    CompassEvaluation,
    User,
    Workspace,
)
from app.schemas.strategy import (
    CareerStrategySummary,
    CompensationAlignmentSummary,
    CrossTrackStrategyComparison,
    CrossTrackStrategyTrack,
    RoleMarketPositioningSummary,
    SearchTrackStrategySummary,
    StrategyActionCandidate,
    StrategyConfidence,
    StrategyInsufficientDataItem,
    StrategyRetrospective,
    StrategySampleSize,
    StrategySignal,
)
from app.services.artifact_performance import ArtifactPerformanceService
from app.services.compensation_intelligence import CompensationIntelligenceService
from app.services.current_user import CurrentUserResolutionError, resolve_current_user
from app.services.historical_learning import HistoricalLearningService
from app.services.recommendations import RecommendationService
from app.services.search_analytics import SearchAnalyticsService
from app.services.search_health import SearchHealthService
from app.services.source_intelligence import SourceIntelligenceService
from app.services.compass_insights import CompassInsightsService


SUBMITTED_STATES = {
    ApplicationWorkflowState.APPLIED.value,
    ApplicationWorkflowState.INTERVIEWING.value,
    ApplicationWorkflowState.OFFER.value,
    ApplicationWorkflowState.REJECTED.value,
    ApplicationWorkflowState.WITHDRAWN.value,
}
RESPONSE_STATES = {
    ApplicationWorkflowState.INTERVIEWING.value,
    ApplicationWorkflowState.OFFER.value,
}


class CareerStrategyError(Exception):
    pass


class CareerStrategySeedMissingError(CareerStrategyError):
    pass


class CareerStrategyWorkspaceNotFoundError(CareerStrategyError):
    pass


class CareerStrategyService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise CareerStrategySeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def get_workspace_strategy(
        self,
        *,
        workspace_id: uuid.UUID,
    ) -> SearchTrackStrategySummary:
        user = self.get_default_user()
        workspace = self._workspace(user.id, workspace_id)
        if workspace is None:
            raise CareerStrategyWorkspaceNotFoundError("Workspace not found")
        return self._build_workspace_summary(user=user, workspace=workspace)

    def get_career_strategy(
        self,
        *,
        include_cross_track: bool = False,
    ) -> CareerStrategySummary:
        user = self.get_default_user()
        workspaces = self._workspaces(user.id)
        tracks = [
            self._build_workspace_summary(user=user, workspace=workspace)
            for workspace in workspaces
        ]
        comparison = (
            self._build_cross_track_comparison(tracks)
            if include_cross_track
            else None
        )
        active = tracks[0] if tracks else None
        return CareerStrategySummary(
            generated_at=_now(),
            summary=(
                f"{len(tracks)} local search track strategy summaries are available."
                if tracks
                else "No local search tracks are available for strategy synthesis."
            ),
            workspace_id=active.workspace_id if active else None,
            workspace_name=active.workspace_name if active else None,
            active_track=active,
            tracks=tracks,
            cross_track_comparison=comparison,
            warnings=[
                "Strategy synthesis is read-only and based only on stored Careero data.",
                "No external market data, external mutation, or durable strategy records are created.",
            ],
        )

    def _build_workspace_summary(
        self,
        *,
        user: User,
        workspace: Workspace,
    ) -> SearchTrackStrategySummary:
        roles = self._roles(user_id=user.id, workspace_id=workspace.id)
        applications = self._applications(user_id=user.id, workspace_id=workspace.id)
        latest_compass = self._latest_compass_by_role(
            user_id=user.id,
            workspace_id=workspace.id,
        )
        artifact_records = self._artifact_records(
            user_id=user.id,
            workspace_id=workspace.id,
        )

        analytics = SearchAnalyticsService(self.db).get_search_analytics(
            workspace_id=workspace.id
        )
        compass = CompassInsightsService(self.db).get_compass_insights(
            workspace_id=workspace.id
        )
        compensation = CompensationIntelligenceService(
            self.db
        ).get_compensation_intelligence(workspace_id=workspace.id)
        source = SourceIntelligenceService(self.db).get_source_intelligence(
            workspace_id=workspace.id
        )
        health = SearchHealthService(self.db).get_search_health(
            workspace_id=workspace.id
        )
        recommendations = RecommendationService(self.db).list_recommendations(
            workspace_id=workspace.id
        )
        historical = HistoricalLearningService(self.db).get_historical_learning(
            workspace_id=workspace.id
        )
        artifacts = ArtifactPerformanceService(self.db).get_performance(
            workspace_id=workspace.id
        )

        submitted = [application for application in applications if _is_submitted(application)]
        responses = [application for application in applications if _has_response(application)]
        sample_size = StrategySampleSize(
            opportunities=len(roles),
            applications=len(applications),
            submitted_applications=len(submitted),
            responses=len(responses),
            compass_evaluations=len(latest_compass),
            artifact_performance_records=len(artifact_records),
        )
        confidence = _confidence(sample_size)
        insufficient_data = _insufficient_data(sample_size)
        known_uncertainty = _known_uncertainty(sample_size)
        signals = [
            *_signals_from_search_health(health.get("signals", []), sample_size),
            *_signals_from_analytics(analytics.get("signals", []), sample_size),
            *_signals_from_compass(compass.get("insights", []), sample_size),
            *_signals_from_compensation(compensation.get("insights", []), sample_size),
            *_signals_from_source(source.get("insights", []), sample_size),
            *_signals_from_artifacts(artifacts.get("insights", []), sample_size),
        ]
        skill_gap_themes = _skill_gap_themes(latest_compass.values(), sample_size)
        narrative_themes = _career_narrative_themes(latest_compass.values(), sample_size)
        compensation_alignment = _compensation_alignment(compensation, sample_size)
        positioning = _role_market_positioning(
            workspace=workspace,
            roles=roles,
            evaluations=latest_compass.values(),
            sample_size=sample_size,
        )
        retrospective = _retrospective(
            workspace=workspace,
            sample_size=sample_size,
            signals=signals,
            historical=historical,
        )
        action_candidates = _action_candidates(
            sample_size=sample_size,
            signals=signals,
            skill_gap_themes=skill_gap_themes,
            recommendations=recommendations.get("recommendations", []),
        )
        warnings = [
            "This is based on your stored Careero data, not external market data.",
            "Strategy actions are advisory; this endpoint does not create automation suggestions or mutate records.",
        ]
        if artifact_records:
            warnings.append(
                "Artifact performance is correlational only and does not prove causation."
            )
        if any(
            "internal title-scope heuristics" in str(item.get("basis", "")).lower()
            for item in compensation.get("insights", [])
        ):
            warnings.append(
                "Some compensation notes use internal title-scope heuristics against stored stated ranges."
            )
        source_inputs = {
            "workspace": str(workspace.id),
            "analytics": "/api/analytics/search",
            "compass": "/api/analytics/compass",
            "source": "/api/analytics/sources",
            "compensation": "/api/analytics/compensation",
            "searchHealth": "/api/analytics/search-health",
            "recommendations": "/api/recommendations",
            "history": "/api/analytics/history",
            "artifactPerformance": "/api/analytics/artifacts",
        }
        return SearchTrackStrategySummary(
            workspace_id=workspace.id,
            workspace_name=workspace.title,
            generated_at=_now(),
            summary=_summary_for(sample_size, signals),
            basis=(
                "Derived from workspace-scoped opportunities, applications, latest COMPASS evaluations, "
                "search analytics, source intelligence, compensation intelligence, search health, "
                "recommendations, historical learning, and artifact performance."
            ),
            confidence=confidence,
            sample_size=sample_size,
            source_inputs=source_inputs,
            known_uncertainty=known_uncertainty,
            insufficient_data=insufficient_data,
            signals=signals,
            compensation_alignment=compensation_alignment,
            skill_gap_themes=skill_gap_themes,
            role_market_positioning=positioning,
            career_narrative_themes=narrative_themes,
            retrospective=retrospective,
            action_candidates=action_candidates,
            warnings=warnings,
        )

    def _build_cross_track_comparison(
        self,
        tracks: list[SearchTrackStrategySummary],
    ) -> CrossTrackStrategyComparison:
        sample_size = sum(track.sample_size.applications for track in tracks)
        confidence = StrategyConfidence(
            confidence=(
                "insufficient_data"
                if len(tracks) < 2
                else "weak"
                if sample_size < 6
                else "moderate"
            ),
            basis="Compares derived read-only strategy summaries across local workspaces.",
            sample_size=sample_size,
            source_inputs={"tracks": len(tracks)},
            known_uncertainty=[
                "Cross-track comparison is internal and depends on consistent tracking."
            ],
            insufficient_data=["few_applications"] if sample_size < 6 else [],
        )
        comparison_tracks = [
            CrossTrackStrategyTrack(
                workspace_id=track.workspace_id,
                workspace_name=track.workspace_name,
                summary=track.summary,
                sample_size=track.sample_size.model_dump(mode="json", by_alias=True),
                signal_count=len(track.signals),
                warning_count=len(track.warnings),
            )
            for track in tracks
        ]
        insufficient = []
        if len(tracks) < 2:
            insufficient.append(
                StrategyInsufficientDataItem(
                    reason="few_opportunities",
                    message="At least two workspaces are needed for cross-track comparison.",
                    source_inputs={"tracks": len(tracks)},
                )
            )
        signals: list[StrategySignal] = []
        if len(tracks) >= 2:
            strongest = max(
                tracks,
                key=lambda track: (
                    track.sample_size.responses,
                    track.sample_size.submitted_applications,
                    track.sample_size.opportunities,
                ),
            )
            signals.append(
                StrategySignal(
                    id="cross-track-traction",
                    category="workspace",
                    label="Strongest observed internal traction",
                    message=(
                        f"{strongest.workspace_name} has the strongest stored response count "
                        "among local tracks. Treat this as an internal comparison only."
                    ),
                    basis="Compares stored response counts across workspace summaries.",
                    severity="info",
                    confidence=confidence,
                    source_inputs={"workspaceId": str(strongest.workspace_id)},
                )
            )
        return CrossTrackStrategyComparison(
            generated_at=_now(),
            basis="Compares local search tracks from derived workspace strategy summaries.",
            confidence=confidence,
            tracks=comparison_tracks,
            signals=signals,
            insufficient_data=insufficient,
            warnings=["This is an internal comparison, not external market data."],
        )

    def _workspace(
        self,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> Workspace | None:
        return self.db.scalar(
            select(Workspace).where(
                Workspace.id == workspace_id,
                Workspace.user_id == user_id,
            )
        )

    def _workspaces(self, user_id: uuid.UUID) -> list[Workspace]:
        return list(
            self.db.scalars(
                select(Workspace)
                .where(Workspace.user_id == user_id)
                .order_by(Workspace.created_at.asc(), Workspace.id.asc())
            )
        )

    def _roles(self, *, user_id: uuid.UUID, workspace_id: uuid.UUID) -> list[Role]:
        return list(
            self.db.scalars(
                select(Role)
                .where(
                    Role.user_id == user_id,
                    Role.workspace_id == workspace_id,
                    Role.deleted_at.is_(None),
                )
                .options(joinedload(Role.company), joinedload(Role.source))
            )
        )

    def _applications(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> list[Application]:
        return list(
            self.db.scalars(
                select(Application)
                .where(
                    Application.user_id == user_id,
                    Application.workspace_id == workspace_id,
                    Application.deleted_at.is_(None),
                )
                .options(
                    joinedload(Application.role),
                    selectinload(Application.state_history),
                    selectinload(Application.interview_stages),
                )
            )
        )

    def _latest_compass_by_role(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> dict[uuid.UUID, CompassEvaluation]:
        latest: dict[uuid.UUID, CompassEvaluation] = {}
        for evaluation in self.db.scalars(
            select(CompassEvaluation)
            .where(
                CompassEvaluation.user_id == user_id,
                CompassEvaluation.workspace_id == workspace_id,
                CompassEvaluation.deleted_at.is_(None),
                CompassEvaluation.evaluation_status == "completed",
            )
            .order_by(CompassEvaluation.role_id, CompassEvaluation.created_at.desc())
        ):
            latest.setdefault(evaluation.role_id, evaluation)
        return latest

    def _artifact_records(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> list[ArtifactPerformanceRecord]:
        return list(
            self.db.scalars(
                select(ArtifactPerformanceRecord).where(
                    ArtifactPerformanceRecord.user_id == user_id,
                    ArtifactPerformanceRecord.workspace_id == workspace_id,
                )
            )
        )


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _confidence(sample_size: StrategySampleSize) -> StrategyConfidence:
    reasons: list[str] = []
    if sample_size.opportunities == 0:
        level = "insufficient_data"
        reasons.append("empty_workspace")
    elif sample_size.applications < 3 or sample_size.compass_evaluations < 3:
        level = "weak"
        if sample_size.applications < 3:
            reasons.append("few_applications")
        if sample_size.compass_evaluations < 3:
            reasons.append("missing_compass_evaluations")
    elif sample_size.responses < 1:
        level = "weak"
        reasons.append("few_outcomes")
    elif sample_size.applications >= 8 and sample_size.responses >= 3:
        level = "high"
    else:
        level = "moderate"
    return StrategyConfidence(
        confidence=level,
        basis="Confidence is derived from local sample size, completed COMPASS coverage, and observed workflow outcomes.",
        sample_size=sample_size.applications,
        source_inputs=sample_size.model_dump(mode="json", by_alias=True),
        known_uncertainty=_known_uncertainty(sample_size),
        insufficient_data=reasons,
    )


def _signal_confidence(
    sample_size: StrategySampleSize,
    *,
    sample_override: int | None = None,
) -> StrategyConfidence:
    base = _confidence(sample_size)
    if sample_override is not None:
        base.sample_size = sample_override
    return base


def _insufficient_data(
    sample_size: StrategySampleSize,
) -> list[StrategyInsufficientDataItem]:
    items: list[StrategyInsufficientDataItem] = []
    if sample_size.opportunities == 0:
        items.append(
            StrategyInsufficientDataItem(
                reason="empty_workspace",
                message="This workspace does not have saved opportunities yet.",
                source_inputs={"opportunities": 0},
            )
        )
    if 0 < sample_size.opportunities < 3:
        items.append(
            StrategyInsufficientDataItem(
                reason="few_opportunities",
                message="Strategy synthesis is thin with fewer than three saved opportunities.",
                source_inputs={"opportunities": sample_size.opportunities},
            )
        )
    if sample_size.applications < 3:
        items.append(
            StrategyInsufficientDataItem(
                reason="few_applications",
                message="Outcome interpretation is limited until at least three applications are tracked.",
                source_inputs={"applications": sample_size.applications},
            )
        )
    if sample_size.responses == 0:
        items.append(
            StrategyInsufficientDataItem(
                reason="few_outcomes",
                message="No positive response or interview outcomes are stored yet.",
                source_inputs={"responses": 0},
            )
        )
    if sample_size.compass_evaluations == 0:
        items.append(
            StrategyInsufficientDataItem(
                reason="missing_compass_evaluations",
                message="Completed COMPASS evaluations are needed for fit and gap themes.",
                source_inputs={"compassEvaluations": 0},
            )
        )
    if sample_size.artifact_performance_records == 0:
        items.append(
            StrategyInsufficientDataItem(
                reason="missing_artifact_performance",
                message="No artifact performance records are stored for this track.",
                source_inputs={"artifactPerformanceRecords": 0},
            )
        )
    return items


def _known_uncertainty(sample_size: StrategySampleSize) -> list[str]:
    uncertainty = [
        "Careero is using stored local evidence only.",
        "This synthesis does not use external market data.",
    ]
    if sample_size.responses < 3:
        uncertainty.append("Outcome signals are weak because response history is thin.")
    if sample_size.artifact_performance_records:
        uncertainty.append("Artifact performance is correlation, not proof of causation.")
    return uncertainty


def _summary_for(
    sample_size: StrategySampleSize,
    signals: list[StrategySignal],
) -> str:
    if sample_size.opportunities == 0:
        return "There is not enough stored Careero data to judge this search strategy yet."
    if sample_size.responses == 0:
        return (
            "Based on your stored Careero data, this track has saved opportunities "
            "but too little outcome evidence to say whether the strategy is working."
        )
    caution_count = sum(1 for signal in signals if signal.severity == "caution")
    if caution_count:
        return (
            "Based on your stored Careero data, this strategy has usable evidence "
            "and some caution signals worth reviewing before expanding the track."
        )
    return (
        "Based on your stored Careero data, this track has early traction signals. "
        "Continue treating conclusions as directional until the sample grows."
    )


def _signals_from_search_health(
    raw: Iterable[dict[str, Any]],
    sample_size: StrategySampleSize,
) -> list[StrategySignal]:
    return [
        _signal(
            id_prefix="search-health",
            category="search_health",
            item=item,
            sample_size=sample_size,
            message_key="gentle_guidance",
        )
        for item in raw
    ]


def _signals_from_analytics(
    raw: Iterable[dict[str, Any]],
    sample_size: StrategySampleSize,
) -> list[StrategySignal]:
    return [
        _signal(
            id_prefix="analytics",
            category="historical",
            item=item,
            sample_size=sample_size,
        )
        for item in raw
    ]


def _signals_from_compass(
    raw: Iterable[dict[str, Any]],
    sample_size: StrategySampleSize,
) -> list[StrategySignal]:
    return [
        _signal(
            id_prefix="compass",
            category="compass",
            item=item,
            sample_size=sample_size,
        )
        for item in raw
    ]


def _signals_from_compensation(
    raw: Iterable[dict[str, Any]],
    sample_size: StrategySampleSize,
) -> list[StrategySignal]:
    return [
        _signal(
            id_prefix="compensation",
            category="compensation",
            item=item,
            sample_size=sample_size,
        )
        for item in raw
    ]


def _signals_from_source(
    raw: Iterable[dict[str, Any]],
    sample_size: StrategySampleSize,
) -> list[StrategySignal]:
    return [
        _signal(
            id_prefix="source",
            category="source",
            item=item,
            sample_size=sample_size,
        )
        for item in raw
    ]


def _signals_from_artifacts(
    raw: Iterable[dict[str, Any]],
    sample_size: StrategySampleSize,
) -> list[StrategySignal]:
    return [
        _signal(
            id_prefix="artifact",
            category="artifact",
            item=item,
            sample_size=sample_size,
        )
        for item in raw
    ]


def _signal(
    *,
    id_prefix: str,
    category: str,
    item: dict[str, Any],
    sample_size: StrategySampleSize,
    message_key: str = "message",
) -> StrategySignal:
    label = str(item.get("label") or item.get("title") or id_prefix)
    severity = str(item.get("severity") or "info")
    if severity not in {"info", "caution", "positive"}:
        severity = "info"
    return StrategySignal(
        id=f"{id_prefix}:{_slug(label)}",
        category=category,
        label=label,
        message=str(item.get(message_key) or item.get("message") or item.get("reason") or label),
        basis=str(item.get("basis") or "Derived from stored Careero data."),
        severity=severity,
        confidence=_signal_confidence(sample_size),
        source_inputs=dict(item.get("source_inputs") or {}),
    )


def _skill_gap_themes(
    evaluations: Iterable[CompassEvaluation],
    sample_size: StrategySampleSize,
) -> list[StrategySignal]:
    counts: Counter[str] = Counter()
    for evaluation in evaluations:
        counts.update(str(keyword).strip().lower() for keyword in evaluation.missing_keywords or [] if str(keyword).strip())
        for concern in evaluation.concerns or []:
            if isinstance(concern, dict):
                message = str(concern.get("message") or concern.get("label") or "").strip()
                if message:
                    counts[message.lower()] += 1
    return [
        StrategySignal(
            id=f"skill-gap:{_slug(label)}",
            category="compass",
            label=label,
            message=f"{label} appears repeatedly in stored COMPASS gaps or ATS findings.",
            basis="Counts repeated missing keywords, concerns, and gap language from completed COMPASS evaluations.",
            severity="caution",
            confidence=_signal_confidence(sample_size, sample_override=count),
            source_inputs={"occurrences": count},
        )
        for label, count in counts.most_common(5)
        if count >= 2
    ]


def _career_narrative_themes(
    evaluations: Iterable[CompassEvaluation],
    sample_size: StrategySampleSize,
) -> list[StrategySignal]:
    counts: Counter[str] = Counter()
    for evaluation in evaluations:
        if evaluation.overall_score is None or float(evaluation.overall_score) < 70:
            continue
        for strength in evaluation.strengths or []:
            if isinstance(strength, dict):
                label = str(strength.get("label") or strength.get("code") or strength.get("message") or "").strip()
                if label:
                    counts[label.lower()] += 1
    return [
        StrategySignal(
            id=f"narrative:{_slug(label)}",
            category="compass",
            label=label,
            message=f"{label} appears in higher-fit stored COMPASS strengths.",
            basis="Counts repeated strengths from completed high-fit COMPASS evaluations.",
            severity="positive",
            confidence=_signal_confidence(sample_size, sample_override=count),
            source_inputs={"occurrences": count},
        )
        for label, count in counts.most_common(5)
    ]


def _compensation_alignment(
    compensation: dict[str, Any],
    sample_size: StrategySampleSize,
) -> CompensationAlignmentSummary:
    insights = compensation.get("insights", [])
    observations = compensation.get("observations", [])
    if insights:
        summary = " ".join(str(item.get("message", "")) for item in insights[:2]).strip()
    elif observations:
        summary = (
            "Stored stated compensation ranges are available for internal comparison. "
            "No compensation strategy caution is active from current data."
        )
    else:
        summary = "No stated compensation ranges are stored for this workspace yet."
    return CompensationAlignmentSummary(
        summary=summary,
        basis=(
            "Compares stored stated compensation ranges against workspace target preferences. "
            "This is an internal/local heuristic, not external market data."
        ),
        confidence=_signal_confidence(sample_size, sample_override=len(observations)),
        observations=list(observations[:8]),
    )


def _role_market_positioning(
    *,
    workspace: Workspace,
    roles: list[Role],
    evaluations: Iterable[CompassEvaluation],
    sample_size: StrategySampleSize,
) -> RoleMarketPositioningSummary:
    categories = Counter(_role_category(role) for role in roles)
    themes = [category for category, _count in categories.most_common(4)]
    high_fit = sum(
        1
        for evaluation in evaluations
        if evaluation.overall_score is not None and float(evaluation.overall_score) >= 75
    )
    if not roles:
        summary = "No saved opportunities are available for internal role positioning yet."
    elif themes:
        top = themes[0].replace("_", " ")
        summary = (
            f"Stored opportunities in {workspace.title} appear concentrated around {top}. "
            f"{high_fit} completed COMPASS evaluations are currently high-fit."
        )
    else:
        summary = "Stored opportunities are too broad to identify a clear internal positioning theme."
    return RoleMarketPositioningSummary(
        summary=summary,
        basis="Uses stored opportunity titles, workspace type, metadata, and COMPASS scores only.",
        confidence=_signal_confidence(sample_size, sample_override=len(roles)),
        themes=themes,
    )


def _retrospective(
    *,
    workspace: Workspace,
    sample_size: StrategySampleSize,
    signals: list[StrategySignal],
    historical: dict[str, Any],
) -> StrategyRetrospective:
    caution = sum(1 for signal in signals if signal.severity == "caution")
    if sample_size.opportunities == 0:
        summary = "This track has not accumulated enough stored evidence for a retrospective."
    elif sample_size.responses == 0:
        summary = (
            "This track has activity but no stored response outcomes yet. A retrospective should focus on fit, source quality, and whether the track boundaries are intentional."
        )
    elif caution:
        summary = (
            "This track has enough evidence for a light retrospective, with caution signals around selectivity, compensation, source, or gap themes."
        )
    else:
        summary = (
            "This track has early positive evidence, but conclusions should remain directional until more outcomes are stored."
        )
    notes = [
        f"Workspace status: {workspace.status}.",
        "No durable retrospective record is created by this synthesis.",
    ]
    notes.extend(str(message) for message in historical.get("insufficient_data", [])[:2])
    return StrategyRetrospective(
        summary=summary,
        basis="Synthesizes local workspace evidence from opportunities, applications, COMPASS, historical learning, and outcomes.",
        confidence=_confidence(sample_size),
        notes=notes,
    )


def _action_candidates(
    *,
    sample_size: StrategySampleSize,
    signals: list[StrategySignal],
    skill_gap_themes: list[StrategySignal],
    recommendations: list[dict[str, Any]],
) -> list[StrategyActionCandidate]:
    candidates: list[StrategyActionCandidate] = []
    if sample_size.opportunities and sample_size.applications < 3:
        candidates.append(
            _action(
                "review-search-boundaries",
                "review_search_focus",
                "Review search-track boundaries",
                "The workspace has saved opportunities but limited workflow outcomes.",
                "Insufficient application outcome sample for stronger strategy synthesis.",
                sample_size,
                {"applications": sample_size.applications},
            )
        )
    if any(signal.category == "compensation" for signal in signals):
        candidates.append(
            _action(
                "review-compensation-target",
                "review_compensation_target",
                "Review compensation target and fallback boundaries",
                "Stored compensation signals suggest the target or opportunity mix may need review.",
                "Derived from stored stated compensation ranges and workspace preferences.",
                sample_size,
                {},
            )
        )
    if skill_gap_themes:
        candidates.append(
            _action(
                "review-skill-gap-plan",
                "review_skill_gap_plan",
                "Review repeated skill-gap themes",
                "Repeated COMPASS gaps may point to a resume positioning or target-scope issue.",
                "Derived from repeated missing keywords and COMPASS gaps.",
                sample_size,
                {"themes": [theme.label for theme in skill_gap_themes[:5]]},
            )
        )
    if any(item.get("recommendation_type") == "artifact" for item in recommendations):
        candidates.append(
            _action(
                "review-artifact-strategy",
                "review_artifact_strategy",
                "Review artifact strategy",
                "Artifact performance has a directional signal. Treat it as correlation only.",
                "Derived from existing read-only recommendation output.",
                sample_size,
                {},
            )
        )
    if any(signal.category == "source" for signal in signals):
        candidates.append(
            _action(
                "review-source-strategy",
                "review_source_strategy",
                "Review source strategy",
                "Stored source traction differs across sources with enough local evidence to review.",
                "Derived from private source intelligence.",
                sample_size,
                {},
            )
        )
    return candidates[:6]


def _action(
    candidate_id: str,
    category: str,
    title: str,
    rationale: str,
    basis: str,
    sample_size: StrategySampleSize,
    source_inputs: dict[str, Any],
) -> StrategyActionCandidate:
    return StrategyActionCandidate(
        id=candidate_id,
        category=category,
        title=title,
        rationale=rationale,
        basis=basis,
        confidence=_signal_confidence(sample_size),
        source_inputs=source_inputs,
        advisory_only=True,
    )


def _role_category(role: Role) -> str:
    metadata = role.parse_metadata or {}
    for key in ("roleCategory", "employmentType", "seniority"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower().replace(" ", "_")
    title = role.title.lower()
    if any(term in title for term in ["manager", "director", "head of", "vp"]):
        return "leadership"
    if any(term in title for term in ["platform", "infrastructure", "devops"]):
        return "infrastructure"
    if any(term in title for term in ["data", "analytics", "machine learning"]):
        return "data"
    if any(term in title for term in ["contract", "consultant", "fractional"]):
        return "contract_consulting"
    return "software_engineering"


def _is_submitted(application: Application) -> bool:
    return application.current_state in SUBMITTED_STATES or application.applied_at is not None


def _has_response(application: Application) -> bool:
    return application.current_state in RESPONSE_STATES or bool(application.interview_stages)


def _slug(value: str) -> str:
    return "-".join(
        part
        for part in "".join(char.lower() if char.isalnum() else " " for char in value).split()
        if part
    )[:80]
