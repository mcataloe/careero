import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.constants import RoleStatus, StrideEvaluationStatus
from app.models import ActivityLog, Role, StrideEvaluation, User
from app.schemas.stride_evaluations import StrideEvaluationCreate
from app.seed import DEFAULT_LOCAL_USER_ID


class StrideEvaluationError(Exception):
    pass


class StrideEvaluationSeedMissingError(StrideEvaluationError):
    pass


class StrideEvaluationRoleNotFoundError(StrideEvaluationError):
    pass


class StrideEvaluationNotFoundError(StrideEvaluationError):
    pass


class StrideEvaluationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        user = self.db.get(User, DEFAULT_LOCAL_USER_ID)
        if user is None or user.deleted_at is not None:
            raise StrideEvaluationSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            )
        return user

    def create_for_role(
        self,
        *,
        role_id: uuid.UUID,
        payload: StrideEvaluationCreate,
    ) -> StrideEvaluation:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise StrideEvaluationRoleNotFoundError("Role not found")

        evaluation_data = self._evaluate_role(role=role, payload=payload)
        evaluation = StrideEvaluation(
            user_id=user.id,
            role_id=role.id,
            **evaluation_data,
        )
        self.db.add(evaluation)
        self.db.flush()
        self.db.add(
            ActivityLog(
                user_id=user.id,
                entity_type="stride_evaluation",
                entity_id=evaluation.id,
                action="stride_evaluation.created",
                details={"role_id": str(role.id)},
            )
        )
        self.db.commit()
        return self.get_by_id(evaluation.id)

    def get_latest_for_role(self, *, role_id: uuid.UUID) -> StrideEvaluation:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise StrideEvaluationRoleNotFoundError("Role not found")

        statement = (
            select(StrideEvaluation)
            .where(
                StrideEvaluation.user_id == user.id,
                StrideEvaluation.role_id == role.id,
                StrideEvaluation.deleted_at.is_(None),
            )
            .order_by(StrideEvaluation.created_at.desc(), StrideEvaluation.id.desc())
            .limit(1)
        )
        evaluation = self.db.scalar(statement)
        if evaluation is None:
            raise StrideEvaluationNotFoundError("STRIDE evaluation not found")
        return evaluation

    def list_evaluations(
        self,
        *,
        role_id: uuid.UUID | None = None,
        evaluation_status: StrideEvaluationStatus | None = None,
    ) -> list[StrideEvaluation]:
        user = self.get_default_user()
        filters = [
            StrideEvaluation.user_id == user.id,
            StrideEvaluation.deleted_at.is_(None),
        ]
        if role_id is not None:
            role = self._get_active_role(role_id=role_id, user_id=user.id)
            if role is None:
                raise StrideEvaluationRoleNotFoundError("Role not found")
            filters.append(StrideEvaluation.role_id == role.id)
        if evaluation_status is not None:
            filters.append(StrideEvaluation.evaluation_status == evaluation_status.value)

        statement = (
            select(StrideEvaluation)
            .where(*filters)
            .order_by(StrideEvaluation.created_at.desc(), StrideEvaluation.id.desc())
        )
        return list(self.db.scalars(statement))

    def get_by_id(self, evaluation_id: uuid.UUID) -> StrideEvaluation:
        user = self.get_default_user()
        statement = select(StrideEvaluation).where(
            StrideEvaluation.id == evaluation_id,
            StrideEvaluation.user_id == user.id,
            StrideEvaluation.deleted_at.is_(None),
        )
        evaluation = self.db.scalar(statement)
        if evaluation is None:
            raise StrideEvaluationNotFoundError("STRIDE evaluation not found")
        return evaluation

    def _get_active_role(self, *, role_id: uuid.UUID, user_id: uuid.UUID) -> Role | None:
        statement = (
            select(Role)
            .options(joinedload(Role.company), joinedload(Role.source))
            .where(
                Role.id == role_id,
                Role.user_id == user_id,
                Role.deleted_at.is_(None),
                Role.status != RoleStatus.ARCHIVED.value,
            )
        )
        return self.db.scalar(statement)

    def _evaluate_role(
        self,
        *,
        role: Role,
        payload: StrideEvaluationCreate,
    ) -> dict[str, Any]:
        not_evaluated = {
            "status": "not_evaluated",
            "reason": (
                "This phase does not connect resume data, external company data, "
                "or an AI evaluator."
            ),
        }
        summary = (
            f"Placeholder STRIDE evaluation for {role.title}"
            f" at {role.company.name}."
            " Structured scoring will be added in a later phase."
        )
        description_text = role.normalized_description or role.raw_description

        return {
            "evaluation_status": StrideEvaluationStatus.COMPLETED.value,
            "overall_score": None,
            "recommendation": None,
            "confidence_level": None,
            "summary": summary,
            "strengths": [],
            "concerns": [],
            "resume_alignment": not_evaluated,
            "compensation_alignment": not_evaluated,
            "seniority_alignment": not_evaluated,
            "remote_alignment": not_evaluated,
            "technical_alignment": not_evaluated,
            "company_risk": not_evaluated,
            "ats_keywords": [],
            "missing_keywords": [],
            "raw_evaluation_json": {
                "evaluator": "deterministic_placeholder",
                "version": "phase_2a",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "inputs": {
                    "role_id": str(role.id),
                    "title": role.title,
                    "company_name": role.company.name,
                    "description_present": bool(description_text),
                    "user_notes": payload.user_notes,
                    "user_context": payload.user_context,
                },
                "limitations": [
                    "No OpenAI call was made.",
                    "No resume facts were inferred.",
                    "No external company or compensation research was performed.",
                ],
            },
        }
