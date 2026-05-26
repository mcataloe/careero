import uuid
import logging
import time
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import Settings, get_settings
from app.constants import RoleStatus, CompassEvaluationStatus
from app.models import ResumeSourceVersion, Role, CompassEvaluation, User
from app.schemas.compass_evaluations import CompassEvaluationCreate
from app.services.activity_log import ActivityLogService
from app.services.current_user import CurrentUserResolutionError, resolve_current_user
from app.services.evaluation_hashing import (
    evaluation_input_hash,
    resume_source_hash,
    role_content_hash,
)
from app.services.compass_ai import OpenAICompassEvaluator, merge_ai_analysis
from app.services.compass_prompt import PROMPT_VERSION
from app.services.compass_rules import RULESET_VERSION, evaluate_role
from app.services.workspace_context import (
    is_workspace_active_for_new_work,
    merge_workspace_context,
    workspace_prompt_context,
)


logger = logging.getLogger(__name__)


class CompassEvaluationError(Exception):
    pass


class CompassEvaluationSeedMissingError(CompassEvaluationError):
    pass


class CompassEvaluationRoleNotFoundError(CompassEvaluationError):
    pass


class CompassEvaluationWorkspaceInactiveError(CompassEvaluationError):
    pass


class CompassEvaluationNotFoundError(CompassEvaluationError):
    pass


@dataclass(frozen=True)
class CompassEvaluationCreateResult:
    evaluation: CompassEvaluation
    reused_cache: bool


class CompassEvaluationService:
    def __init__(
        self,
        db: Session,
        settings: Settings | None = None,
        ai_evaluator: OpenAICompassEvaluator | None = None,
    ) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.ai_evaluator = ai_evaluator or OpenAICompassEvaluator(self.settings)
        self.activity_log = ActivityLogService(db)

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise CompassEvaluationSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def create_for_role(
        self,
        *,
        role_id: uuid.UUID,
        payload: CompassEvaluationCreate,
    ) -> CompassEvaluationCreateResult:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise CompassEvaluationRoleNotFoundError("Role not found")
        if not is_workspace_active_for_new_work(role.workspace):
            raise CompassEvaluationWorkspaceInactiveError("Workspace is not active")

        workspace_context = workspace_prompt_context(role.workspace)
        effective_user_context = merge_workspace_context(
            workspace=role.workspace,
            request_context=payload.user_context,
        )
        active_resume_source = self._get_active_resume_source_version(user.id)
        role_hash = role_content_hash(role)
        source_hash = resume_source_hash(active_resume_source)
        input_hash = evaluation_input_hash(
            role_hash=role_hash,
            source_hash=source_hash,
            user_notes=payload.user_notes,
            user_context=effective_user_context,
            prompt_version=PROMPT_VERSION,
            ruleset_version=RULESET_VERSION,
            ai_enabled=self.settings.enable_ai_evaluations,
            model_name=self.settings.openai_default_evaluation_model,
            workspace_id=str(role.workspace_id),
            workspace_context=workspace_context,
        )

        if not payload.force:
            cached = self._get_cached_evaluation(
                user_id=user.id,
                workspace_id=role.workspace_id,
                role_id=role.id,
                input_hash=input_hash,
            )
            if cached is not None:
                self._add_activity(
                    user_id=user.id,
                    entity_id=cached.id,
                    action="compass_evaluation.cached_result_reused",
                    details={
                        "role_id": str(role.id),
                        "workspace_id": str(role.workspace_id),
                        "evaluation_input_hash": input_hash,
                    },
                )
                self.db.commit()
                logger.info(
                    "COMPASS evaluation cache reused",
                    extra={
                        "role_id": str(role.id),
                        "evaluation_id": str(cached.id),
                        "ai_status": cached.ai_status,
                    },
                )
                return CompassEvaluationCreateResult(
                    evaluation=cached,
                    reused_cache=True,
                )

        evaluation_id = uuid.uuid4()
        self._add_activity(
            user_id=user.id,
            entity_id=evaluation_id,
            action="compass_evaluation.started",
            details={
                "role_id": str(role.id),
                "workspace_id": str(role.workspace_id),
                "evaluation_input_hash": input_hash,
                "force": payload.force,
            },
        )
        started_at = time.perf_counter()
        try:
            baseline = evaluate_role(
                role,
                effective_user_context,
                payload.user_notes,
            )
            ai_metadata = self.ai_evaluator.enrich(
                role=role,
                payload=CompassEvaluationCreate(
                    user_notes=payload.user_notes,
                    user_context=effective_user_context,
                    force=payload.force,
                ),
                baseline=baseline,
                active_resume_source=active_resume_source,
                workspace_context=workspace_context,
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
            raw["workspace"] = workspace_context
            raw["request_user_context"] = payload.user_context
            raw["effective_user_context"] = effective_user_context
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

            evaluation = CompassEvaluation(
                id=evaluation_id,
                user_id=user.id,
                workspace_id=role.workspace_id,
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
                    action="compass_evaluation.failed",
                    details={
                        "role_id": str(role.id),
                        "workspace_id": str(role.workspace_id),
                        "error_type": ai_metadata.get("ai_error_type"),
                    },
                )
            self._add_activity(
                user_id=user.id,
                entity_id=evaluation.id,
                action="compass_evaluation.completed",
                details={
                    "role_id": str(role.id),
                    "workspace_id": str(role.workspace_id),
                    "ai_status": ai_status,
                    "latency_ms": latency_ms,
                    "evaluation_input_hash": input_hash,
                },
            )
            self.db.commit()
            logger.info(
                "COMPASS evaluation completed",
                extra={
                    "role_id": str(role.id),
                    "evaluation_id": str(evaluation.id),
                    "ai_status": ai_status,
                    "latency_ms": latency_ms,
                },
            )
            return CompassEvaluationCreateResult(
                evaluation=self.get_by_id(evaluation.id),
                reused_cache=False,
            )
        except Exception as exc:
            self.db.rollback()
            self._add_activity(
                user_id=user.id,
                entity_id=evaluation_id,
                action="compass_evaluation.failed",
                details={
                    "role_id": str(role.id),
                    "workspace_id": str(role.workspace_id),
                    "error_type": type(exc).__name__,
                },
            )
            self.db.commit()
            logger.warning(
                "COMPASS evaluation failed before persistence: %s",
                type(exc).__name__,
                extra={"role_id": str(role.id), "evaluation_id": str(evaluation_id)},
            )
            raise

    def get_latest_for_role(self, *, role_id: uuid.UUID) -> CompassEvaluation:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise CompassEvaluationRoleNotFoundError("Role not found")

        statement = (
            select(CompassEvaluation)
            .where(
                CompassEvaluation.user_id == user.id,
                CompassEvaluation.role_id == role.id,
                CompassEvaluation.deleted_at.is_(None),
            )
            .order_by(CompassEvaluation.created_at.desc(), CompassEvaluation.id.desc())
            .limit(1)
        )
        evaluation = self.db.scalar(statement)
        if evaluation is None:
            raise CompassEvaluationNotFoundError("COMPASS evaluation not found")
        return evaluation

    def list_evaluations(
        self,
        *,
        role_id: uuid.UUID | None = None,
        evaluation_status: CompassEvaluationStatus | None = None,
    ) -> list[CompassEvaluation]:
        user = self.get_default_user()
        filters = [
            CompassEvaluation.user_id == user.id,
            CompassEvaluation.deleted_at.is_(None),
        ]
        if role_id is not None:
            role = self._get_active_role(role_id=role_id, user_id=user.id)
            if role is None:
                raise CompassEvaluationRoleNotFoundError("Role not found")
            filters.append(CompassEvaluation.role_id == role.id)
        if evaluation_status is not None:
            filters.append(CompassEvaluation.evaluation_status == evaluation_status.value)

        statement = (
            select(CompassEvaluation)
            .where(*filters)
            .order_by(CompassEvaluation.created_at.desc(), CompassEvaluation.id.desc())
        )
        return list(self.db.scalars(statement))

    def get_by_id(self, evaluation_id: uuid.UUID) -> CompassEvaluation:
        user = self.get_default_user()
        statement = select(CompassEvaluation).where(
            CompassEvaluation.id == evaluation_id,
            CompassEvaluation.user_id == user.id,
            CompassEvaluation.deleted_at.is_(None),
        )
        evaluation = self.db.scalar(statement)
        if evaluation is None:
            raise CompassEvaluationNotFoundError("COMPASS evaluation not found")
        return evaluation

    def _get_active_role(self, *, role_id: uuid.UUID, user_id: uuid.UUID) -> Role | None:
        statement = (
            select(Role)
            .options(joinedload(Role.company), joinedload(Role.source))
            .options(joinedload(Role.workspace))
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
        workspace_id: uuid.UUID,
        role_id: uuid.UUID,
        input_hash: str,
    ) -> CompassEvaluation | None:
        statement = (
            select(CompassEvaluation)
            .where(
                CompassEvaluation.user_id == user_id,
                CompassEvaluation.workspace_id == workspace_id,
                CompassEvaluation.role_id == role_id,
                CompassEvaluation.deleted_at.is_(None),
                CompassEvaluation.evaluation_status
                == CompassEvaluationStatus.COMPLETED.value,
                CompassEvaluation.evaluation_input_hash == input_hash,
            )
            .order_by(CompassEvaluation.created_at.desc(), CompassEvaluation.id.desc())
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
        self.activity_log.append(
            user_id=user_id,
            entity_type="compass_evaluation",
            entity_id=entity_id,
            action=action,
            details=details,
        )
