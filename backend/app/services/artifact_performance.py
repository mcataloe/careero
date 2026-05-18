from __future__ import annotations

import uuid
from collections import defaultdict
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.constants import ApplicationWorkflowState
from app.models import (
    Application,
    ApplicationNote,
    ArtifactPerformanceRecord,
    GeneratedArtifact,
    Role,
    StrideEvaluation,
    User,
)
from app.seed import DEFAULT_LOCAL_USER_ID


POSITIVE_RESPONSE_STATES = {
    ApplicationWorkflowState.INTERVIEWING.value,
    ApplicationWorkflowState.OFFER.value,
}
INTERVIEW_STATES = {
    ApplicationWorkflowState.INTERVIEWING.value,
    ApplicationWorkflowState.OFFER.value,
}


class ArtifactPerformanceError(Exception):
    pass


class ArtifactPerformanceSeedMissingError(ArtifactPerformanceError):
    pass


class ArtifactPerformanceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        user = self.db.get(User, DEFAULT_LOCAL_USER_ID)
        if user is None or user.deleted_at is not None:
            raise ArtifactPerformanceSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            )
        return user

    def record_generated_artifact(
        self,
        *,
        artifact: GeneratedArtifact,
        role: Role,
        evaluation: StrideEvaluation | None,
    ) -> ArtifactPerformanceRecord:
        application = self._application_for_role(role)
        contract = artifact.artifact_metadata.get("contract", {})
        revision = contract.get("revision", {}) if isinstance(contract, dict) else {}
        record = ArtifactPerformanceRecord(
            user_id=artifact.user_id,
            workspace_id=artifact.workspace_id,
            role_id=role.id,
            application_id=application.id if application is not None else None,
            artifact_id=artifact.id,
            artifact_type=artifact.artifact_type,
            variant_name=_variant_name(artifact),
            version_label=_version_label(revision),
            targeted_role_category=_role_category(role),
            application_state_when_used=(
                application.current_state if application is not None else None
            ),
            response_outcome=_response_outcome(application),
            interview_outcome=_interview_outcome(application),
            recruiter_engagement_outcome=_recruiter_outcome(self.db, application),
            stride_alignment=_stride_alignment(evaluation),
            generated_at=artifact.created_at,
            submitted_at=application.applied_at if application is not None else None,
            record_metadata={
                "source": "artifact_generation",
                "artifactTitle": artifact.title,
            },
        )
        self.db.add(record)
        return record

    def get_performance(
        self,
        *,
        workspace_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        records = self._records(user_id=user.id, workspace_id=workspace_id)
        synced = [self._with_current_outcomes(record) for record in records]
        summary = summarize_artifact_records(synced)
        return {
            "workspace_id": workspace_id,
            "summary": summary["summary"],
            "by_variant": summary["by_variant"],
            "by_role_category": summary["by_role_category"],
            "insights": summary["insights"],
            "insufficient_data": summary["insufficient_data"],
        }

    def _application_for_role(self, role: Role) -> Application | None:
        return self.db.scalar(
            select(Application)
            .where(
                Application.role_id == role.id,
                Application.user_id == role.user_id,
                Application.deleted_at.is_(None),
            )
            .order_by(Application.created_at.desc(), Application.id.desc())
            .limit(1)
        )

    def _records(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID | None,
    ) -> list[ArtifactPerformanceRecord]:
        filters = [ArtifactPerformanceRecord.user_id == user_id]
        if workspace_id is not None:
            filters.append(ArtifactPerformanceRecord.workspace_id == workspace_id)
        return list(self.db.scalars(select(ArtifactPerformanceRecord).where(*filters)))

    def _with_current_outcomes(
        self,
        record: ArtifactPerformanceRecord,
    ) -> ArtifactPerformanceRecord:
        if record.application_id is None:
            return record
        application = self.db.scalar(
            select(Application)
            .where(Application.id == record.application_id)
            .options(selectinload(Application.interview_stages))
        )
        if application is None:
            return record
        record.response_outcome = _response_outcome(application)
        record.interview_outcome = _interview_outcome(application)
        record.recruiter_engagement_outcome = _recruiter_outcome(self.db, application)
        record.submitted_at = application.applied_at
        return record


def summarize_artifact_records(
    records: Iterable[ArtifactPerformanceRecord],
) -> dict[str, Any]:
    items = list(records)
    return {
        "summary": [
            _metric("All artifacts", items, basis="All artifact performance records."),
            *_summary_by_type(items),
        ],
        "by_variant": _grouped_metrics(
            items,
            key=lambda item: (item.artifact_type, item.variant_name),
            label=lambda key: f"{key[0]}: {key[1]}",
            basis="Observed outcomes grouped by artifact type and variant name.",
        ),
        "by_role_category": _grouped_metrics(
            items,
            key=lambda item: item.targeted_role_category or "uncategorized",
            label=lambda key: str(key),
            basis="Observed outcomes grouped by targeted role category.",
        ),
        "insights": _insights(items),
        "insufficient_data": _insufficient_data(items),
    }


def _summary_by_type(items: list[ArtifactPerformanceRecord]) -> list[dict[str, Any]]:
    by_type: dict[str, list[ArtifactPerformanceRecord]] = defaultdict(list)
    for item in items:
        by_type[item.artifact_type].append(item)
    return [
        _metric(artifact_type, values, basis=f"All {artifact_type} performance records.")
        for artifact_type, values in sorted(by_type.items())
    ]


def _grouped_metrics(items, *, key, label, basis: str) -> list[dict[str, Any]]:
    grouped: dict[Any, list[ArtifactPerformanceRecord]] = defaultdict(list)
    for item in items:
        grouped[key(item)].append(item)
    metrics = [_metric(label(group_key), values, basis=basis) for group_key, values in grouped.items()]
    return sorted(metrics, key=lambda metric: (-metric["total"], metric["label"]))


def _metric(
    label: str,
    records: list[ArtifactPerformanceRecord],
    *,
    basis: str,
) -> dict[str, Any]:
    total = len(records)
    responses = sum(1 for record in records if record.response_outcome == "positive_response")
    interviews = sum(1 for record in records if record.interview_outcome == "interview_received")
    first = records[0] if records else None
    return {
        "label": label,
        "artifact_type": first.artifact_type if first is not None else None,
        "variant_name": first.variant_name if first is not None else None,
        "role_category": first.targeted_role_category if first is not None else None,
        "total": total,
        "responses": responses,
        "interviews": interviews,
        "response_rate": round(responses / total, 4) if total else None,
        "interview_rate": round(interviews / total, 4) if total else None,
        "basis": basis,
    }


def _insights(records: list[ArtifactPerformanceRecord]) -> list[dict[str, Any]]:
    insights: list[dict[str, Any]] = []
    by_variant = _grouped_metrics(
        records,
        key=lambda item: (item.artifact_type, item.variant_name),
        label=lambda key: f"{key[0]}: {key[1]}",
        basis="Observed outcomes grouped by artifact type and variant name.",
    )
    meaningful = [metric for metric in by_variant if metric["total"] >= 3]
    if meaningful:
        best = max(meaningful, key=lambda metric: metric["response_rate"] or 0)
        insights.append(
            {
                "label": "Observed artifact traction",
                "message": f"{best['label']} has the strongest observed response rate among variants with at least three uses.",
                "basis": "Simple observed response rate by artifact variant. This is correlation, not proof.",
                "confidence": "weak" if best["total"] < 6 else "moderate",
            }
        )
    return insights


def _insufficient_data(records: list[ArtifactPerformanceRecord]) -> list[str]:
    messages: list[str] = []
    if len(records) < 3:
        messages.append("Artifact performance needs at least three recorded uses before comparison is useful.")
    if not any(record.response_outcome == "positive_response" for record in records):
        messages.append("No positive response outcomes are attached to artifact records yet.")
    return messages


def _variant_name(artifact: GeneratedArtifact) -> str:
    contract = artifact.artifact_metadata.get("contract", {})
    if isinstance(contract, dict):
        title = contract.get("title")
        if title:
            return str(title)
    return artifact.title


def _version_label(revision: dict[str, Any]) -> str | None:
    revision_number = revision.get("revisionNumber")
    return f"v{revision_number}" if revision_number is not None else None


def _role_category(role: Role) -> str:
    metadata = role.parse_metadata or {}
    for key in ("roleCategory", "seniority", "employmentType"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    title = role.title.lower()
    if any(term in title for term in ["manager", "director", "head of"]):
        return "leadership"
    if any(term in title for term in ["platform", "infrastructure", "devops"]):
        return "infrastructure"
    if any(term in title for term in ["frontend", "full stack", "backend"]):
        return "software_engineering"
    return "general"


def _response_outcome(application: Application | None) -> str | None:
    if application is None:
        return None
    if application.current_state in POSITIVE_RESPONSE_STATES or application.interview_stages:
        return "positive_response"
    if application.current_state == ApplicationWorkflowState.REJECTED.value:
        return "rejected"
    return "pending"


def _interview_outcome(application: Application | None) -> str | None:
    if application is None:
        return None
    if application.current_state in INTERVIEW_STATES or application.interview_stages:
        return "interview_received"
    return "none_recorded"


def _recruiter_outcome(db: Session, application: Application | None) -> str | None:
    if application is None:
        return None
    note_id = db.scalar(
        select(ApplicationNote.id)
        .where(
            ApplicationNote.application_id == application.id,
            ApplicationNote.deleted_at.is_(None),
            ApplicationNote.note_type == "recruiter",
        )
        .limit(1)
    )
    return "recruiter_engaged" if note_id is not None else "none_recorded"


def _stride_alignment(evaluation: StrideEvaluation | None) -> dict[str, Any]:
    if evaluation is None:
        return {}
    return {
        "overall_score": float(evaluation.overall_score)
        if evaluation.overall_score is not None
        else None,
        "recommendation": evaluation.recommendation,
        "confidence_level": evaluation.confidence_level,
        "ats_keywords": evaluation.ats_keywords,
        "missing_keywords": evaluation.missing_keywords,
    }
