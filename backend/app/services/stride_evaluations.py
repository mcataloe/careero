import uuid
import logging
import time
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import Settings, get_settings
from app.constants import RoleStatus, StrideEvaluationStatus
from app.models import ActivityLog, ResumeSourceVersion, Role, StrideEvaluation, User
from app.schemas.stride_evaluations import StrideEvaluationCreate
from app.seed import DEFAULT_LOCAL_USER_ID
from app.services.evaluation_hashing import (
    evaluation_input_hash,
    resume_source_hash,
    role_content_hash,
)
from app.services.stride_ai import OpenAIStrideEvaluator, merge_ai_analysis
from app.services.stride_prompt import PROMPT_VERSION
from app.services.stride_rules import RULESET_VERSION, evaluate_role


logger = logging.getLogger(__name__)


class StrideEvaluationError(Exception):
    pass


class StrideEvaluationSeedMissingError(StrideEvaluationError):
    pass


class StrideEvaluationRoleNotFoundError(StrideEvaluationError):
    pass


class StrideEvaluationNotFoundError(StrideEvaluationError):
    pass


@dataclass(frozen=True)
class StrideEvaluationCreateResult:
    evaluation: StrideEvaluation
    reused_cache: bool


class StrideEvaluationService:
    def __init__(
        self,
        db: Session,
        settings: Settings | None = None,
        ai_evaluator: OpenAIStrideEvaluator | None = None,
    ) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.ai_evaluator = ai_evaluator or OpenAIStrideEvaluator(self.settings)

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
    ) -> StrideEvaluationCreateResult:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise StrideEvaluationRoleNotFoundError("Role not found")

        active_resume_source = self._get_active_resume_source_version(user.id)
        role_hash = role_content_hash(role)
        source_hash = resume_source_hash(active_resume_source)
        input_hash = evaluation_input_hash(
            role_hash=role_hash,
            source_hash=source_hash,
            user_notes=payload.user_notes,
            user_context=payload.user_context,
            prompt_version=PROMPT_VERSION,
            ruleset_version=RULESET_VERSION,
            ai_enabled=self.settings.enable_ai_evaluations,
            model_name=self.settings.openai_default_evaluation_model,
        )

        if not payload.force:
            cached = self._get_cached_evaluation(
                user_id=user.id,
                role_id=role.id,
                input_hash=input_hash,
            )
            if cached is not None:
                self._add_activity(
                    user_id=user.id,
                    entity_id=cached.id,
                    action="stride_evaluation.cached_result_reused",
                    details={
                        "role_id": str(role.id),
                        "evaluation_input_hash": input_hash,
                    },
                )
                self.db.commit()
                logger.info(
                    "STRIDE evaluation cache reused",
                    extra={
                        "role_id": str(role.id),
                        "evaluation_id": str(cached.id),
                        "ai_status": cached.ai_status,
                    },
                )
                return StrideEvaluationCreateResult(
                    evaluation=cached,
                    reused_cache=True,
                )

        evaluation_id = uuid.uuid4()
        self._add_activity(
            user_id=user.id,
            entity_id=evaluation_id,
            action="stride_evaluation.started",
            details={
                "role_id": str(role.id),
                "evaluation_input_hash": input_hash,
                "force": payload.force,
            },
        )
        started_at = time.perf_counter()
        try:
            baseline = evaluate_role(
                role,
                payload.user_context,
                payload.user_notes,
            )
            ai_metadata = self.ai_evaluator.enrich(
                role=role,
                payload=payload,
                baseline=baseline,
                active_resume_source=active_resume_source,
            )
            evaluation_data = merge_ai_analysis(
                baseline,
                ai_metadata,
                active_resume_source=active_resume_source,
            )
            latency_ms = max(0, round((time.perf_counter() - started_at) * 1000))
            ai_status = ai_metadata.get("ai_status")
            error_message = (
                ai_metadata.get("ai_failure_reason")
                if ai_status == "failed"
                else None
            )

            raw = dict(evaluation_data["raw_evaluation_json"])
            raw["prompt_version"] = PROMPT_VERSION
            raw["ruleset_version"] = RULESET_VERSION
            raw["role_content_hash"] = role_hash
            raw["source_hash"] = source_hash
            raw["evaluation_input_hash"] = input_hash
            raw["run_metadata"] = {
                "model_used": ai_metadata.get("ai_model"),
                "prompt_version": PROMPT_VERSION,
                "ruleset_version": RULESET_VERSION,
                "input_token_estimate": ai_metadata.get("ai_input_token_estimate"),
                "output_token_estimate": ai_metadata.get("ai_output_token_estimate"),
                "latency_ms": latency_ms,
                "ai_enabled": self.settings.enable_ai_evaluations,
                "ai_status": ai_status,
                "error_type": ai_metadata.get("ai_error_type"),
            }
            evaluation_data["raw_evaluation_json"] = raw

            evaluation = StrideEvaluation(
                id=evaluation_id,
                user_id=user.id,
                role_id=role.id,
                model_used=ai_metadata.get("ai_model"),
                prompt_version=PROMPT_VERSION,
                ruleset_version=RULESET_VERSION,
                input_token_estimate=ai_metadata.get("ai_input_token_estimate"),
                output_token_estimate=ai_metadata.get("ai_output_token_estimate"),
                latency_ms=latency_ms,
                ai_enabled=self.settings.enable_ai_evaluations,
                ai_status=ai_status,
                error_message=error_message,
                role_content_hash=role_hash,
                source_hash=source_hash,
                evaluation_input_hash=input_hash,
                **evaluation_data,
            )
            self.db.add(evaluation)
            self.db.flush()
            if ai_status == "failed":
                self._add_activity(
                    user_id=user.id,
                    entity_id=evaluation.id,
                    action="stride_evaluation.failed",
                    details={
                        "role_id": str(role.id),
                        "error_type": ai_metadata.get("ai_error_type"),
                    },
                )
            self._add_activity(
                user_id=user.id,
                entity_id=evaluation.id,
                action="stride_evaluation.completed",
                details={
                    "role_id": str(role.id),
                    "ai_status": ai_status,
                    "latency_ms": latency_ms,
                    "evaluation_input_hash": input_hash,
                },
            )
            self.db.commit()
            logger.info(
                "STRIDE evaluation completed",
                extra={
                    "role_id": str(role.id),
                    "evaluation_id": str(evaluation.id),
                    "ai_status": ai_status,
                    "latency_ms": latency_ms,
                },
            )
            return StrideEvaluationCreateResult(
                evaluation=self.get_by_id(evaluation.id),
                reused_cache=False,
            )
        except Exception as exc:
            self.db.rollback()
            self._add_activity(
                user_id=user.id,
                entity_id=evaluation_id,
                action="stride_evaluation.failed",
                details={
                    "role_id": str(role.id),
                    "error_type": type(exc).__name__,
                },
            )
            self.db.commit()
            logger.warning(
                "STRIDE evaluation failed before persistence: %s",
                type(exc).__name__,
                extra={"role_id": str(role.id), "evaluation_id": str(evaluation_id)},
            )
            raise

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

    def _get_active_resume_source_version(
        self,
        user_id: uuid.UUID,
    ) -> ResumeSourceVersion | None:
        statement = (
            select(ResumeSourceVersion)
            .options(joinedload(ResumeSourceVersion.source))
            .where(
                ResumeSourceVersion.user_id == user_id,
                ResumeSourceVersion.is_active.is_(True),
            )
            .order_by(
                ResumeSourceVersion.updated_at.desc(),
                ResumeSourceVersion.id.desc(),
            )
            .limit(1)
        )
        return self.db.scalar(statement)

    def _get_cached_evaluation(
        self,
        *,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        input_hash: str,
    ) -> StrideEvaluation | None:
        statement = (
            select(StrideEvaluation)
            .where(
                StrideEvaluation.user_id == user_id,
                StrideEvaluation.role_id == role_id,
                StrideEvaluation.deleted_at.is_(None),
                StrideEvaluation.evaluation_status
                == StrideEvaluationStatus.COMPLETED.value,
                StrideEvaluation.evaluation_input_hash == input_hash,
            )
            .order_by(StrideEvaluation.created_at.desc(), StrideEvaluation.id.desc())
            .limit(1)
        )
        return self.db.scalar(statement)

    def _add_activity(
        self,
        *,
        user_id: uuid.UUID,
        entity_id: uuid.UUID,
        action: str,
        details: dict,
    ) -> None:
        self.db.add(
            ActivityLog(
                user_id=user_id,
                entity_type="stride_evaluation",
                entity_id=entity_id,
                action=action,
                details=details,
            )
        )
