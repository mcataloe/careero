from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, FormatChecker
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import Settings, get_settings
from app.constants import RoleStatus
from app.models import (
    GeneratedArtifact,
    ResumeSourceVersion,
    Role,
    StrideEvaluation,
    User,
)
from app.schemas.cover_letter_artifacts import CoverLetterArtifactGenerateRequest
from app.seed import DEFAULT_LOCAL_USER_ID
from app.services.activity_log import ActivityLogService
from app.services.cover_letter_artifact_ai import (
    CoverLetterArtifactGenerationUnavailableError,
    CoverLetterArtifactOutputValidationError,
    CoverLetterArtifactProviderError as AICoverLetterArtifactProviderError,
    OpenAICoverLetterArtifactGenerator,
)
from app.services.cover_letter_artifact_prompt import PROMPT_VERSION
from app.services.evaluation_hashing import resume_source_hash, role_content_hash


class CoverLetterArtifactError(Exception):
    pass


class CoverLetterArtifactSeedMissingError(CoverLetterArtifactError):
    pass


class CoverLetterArtifactRoleNotFoundError(CoverLetterArtifactError):
    pass


class CoverLetterArtifactEvaluationNotFoundError(CoverLetterArtifactError):
    pass


class CoverLetterArtifactSourceNotFoundError(CoverLetterArtifactError):
    pass


class CoverLetterArtifactUnavailableError(CoverLetterArtifactError):
    pass


class CoverLetterArtifactProviderError(CoverLetterArtifactError):
    pass


class CoverLetterArtifactValidationError(CoverLetterArtifactError):
    pass


class CoverLetterArtifactTruthfulnessError(CoverLetterArtifactValidationError):
    pass


class CoverLetterArtifactService:
    def __init__(
        self,
        db: Session,
        settings: Settings | None = None,
        generator: OpenAICoverLetterArtifactGenerator | None = None,
    ) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.generator = generator or OpenAICoverLetterArtifactGenerator(self.settings)
        self.activity_log = ActivityLogService(db)
        self._schema_validator = _cover_letter_artifact_validator()

    def get_default_user(self) -> User:
        user = self.db.get(User, DEFAULT_LOCAL_USER_ID)
        if user is None or user.deleted_at is not None:
            raise CoverLetterArtifactSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            )
        return user

    def generate_for_role(
        self,
        *,
        role_id: uuid.UUID,
        payload: CoverLetterArtifactGenerateRequest,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise CoverLetterArtifactRoleNotFoundError("Role not found")

        evaluation = self._get_evaluation(
            user_id=user.id,
            role_id=role.id,
            evaluation_id=payload.evaluation_id,
        )
        if payload.evaluation_id is not None and evaluation is None:
            raise CoverLetterArtifactEvaluationNotFoundError(
                "STRIDE evaluation not found"
            )

        source_version = self._get_source_version(
            user_id=user.id,
            source_version_id=payload.source_version_id,
        )
        if payload.source_version_id is not None and source_version is None:
            raise CoverLetterArtifactSourceNotFoundError(
                "Resume source version not found"
            )

        artifact_id = uuid.uuid4()
        self._log_activity(
            user_id=user.id,
            entity_id=artifact_id,
            action="cover_letter_artifact.started",
            details={
                "role_id": str(role.id),
                "evaluation_id": str(evaluation.id) if evaluation is not None else None,
                "workspace_id": str(payload.workspace_id),
                "source_version_id": (
                    str(source_version.id) if source_version is not None else None
                ),
                "tone": payload.tone,
            },
        )
        self.db.commit()

        try:
            ai_result = self.generator.generate(
                role=role,
                tone=payload.tone,
                evaluation=evaluation,
                source_version=source_version,
            )
            artifact = self._build_artifact_contract(
                artifact_id=artifact_id,
                workspace_id=payload.workspace_id,
                role=role,
                evaluation=evaluation,
                source_version=source_version,
                tone=payload.tone,
                ai_result=ai_result,
                user_id=user.id,
            )
            self._validate_contract(artifact)

            persisted = GeneratedArtifact(
                id=artifact_id,
                user_id=user.id,
                role_id=role.id,
                artifact_type="cover_letter",
                title=artifact["title"],
                content=artifact["content"],
                artifact_metadata={
                    "contract": artifact,
                    "source_resume": _source_resume_metadata(source_version),
                    "target_evaluation_id": (
                        str(evaluation.id) if evaluation is not None else None
                    ),
                    "workspace_id": str(payload.workspace_id),
                    "tone": payload.tone,
                },
            )
            self.db.add(persisted)
            self._log_activity(
                user_id=user.id,
                entity_id=artifact_id,
                action="cover_letter_artifact.completed",
                details={
                    "role_id": str(role.id),
                    "evaluation_id": (
                        str(evaluation.id) if evaluation is not None else None
                    ),
                    "workspace_id": str(payload.workspace_id),
                    "revision_number": artifact["revision"]["revisionNumber"],
                    "tone": payload.tone,
                },
            )
            self.db.commit()
            return artifact
        except CoverLetterArtifactGenerationUnavailableError as exc:
            self._rollback_and_log_failure(
                user_id=user.id,
                entity_id=artifact_id,
                role_id=role.id,
                error_type=type(exc).__name__,
            )
            raise CoverLetterArtifactUnavailableError(str(exc)) from exc
        except CoverLetterArtifactOutputValidationError as exc:
            self._rollback_and_log_failure(
                user_id=user.id,
                entity_id=artifact_id,
                role_id=role.id,
                error_type=type(exc).__name__,
            )
            raise CoverLetterArtifactValidationError(str(exc)) from exc
        except AICoverLetterArtifactProviderError as exc:
            self._rollback_and_log_failure(
                user_id=user.id,
                entity_id=artifact_id,
                role_id=role.id,
                error_type=type(exc).__name__,
            )
            raise CoverLetterArtifactProviderError(str(exc)) from exc
        except CoverLetterArtifactValidationError:
            self._rollback_and_log_failure(
                user_id=user.id,
                entity_id=artifact_id,
                role_id=role.id,
                error_type="CoverLetterArtifactValidationError",
            )
            raise
        except Exception as exc:
            self._rollback_and_log_failure(
                user_id=user.id,
                entity_id=artifact_id,
                role_id=role.id,
                error_type=type(exc).__name__,
            )
            raise CoverLetterArtifactProviderError(
                "Cover letter artifact generation failed"
            ) from exc

    def _build_artifact_contract(
        self,
        *,
        artifact_id: uuid.UUID,
        workspace_id: uuid.UUID,
        role: Role,
        evaluation: StrideEvaluation | None,
        source_version: ResumeSourceVersion | None,
        tone: str,
        ai_result: dict[str, Any],
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        output = ai_result["output"]
        self._enforce_truthfulness(
            output=output,
            source_text=source_version.raw_text if source_version is not None else None,
            evaluation=evaluation,
        )
        now = _iso_now()
        source_hash = resume_source_hash(source_version)
        input_hash = _prefixed_hash(
            {
                "role_content_hash": role_content_hash(role),
                "source_hash": source_hash,
                "evaluation_id": str(evaluation.id) if evaluation is not None else None,
                "prompt_version": PROMPT_VERSION,
                "model_name": ai_result["model"],
                "tone": tone,
            }
        )
        prior = self._latest_prior_artifact(
            user_id=user_id,
            role_id=role.id,
            workspace_id=workspace_id,
        )
        prior_contract = (
            prior.artifact_metadata.get("contract")
            if prior is not None and prior.artifact_metadata
            else None
        )
        prior_revision = (
            prior_contract.get("revision", {}).get("revisionNumber")
            if isinstance(prior_contract, dict)
            else None
        )
        revision_number = int(prior_revision or 0) + 1
        warnings = list(output.get("warnings", []))
        warnings.extend(output.get("limitations", []))
        if evaluation is None:
            warnings.append("Generated without a STRIDE evaluation.")
        if source_version is None:
            warnings.append("Generated without a resume/profile source.")

        return {
            "contractVersion": "careero.contracts.v1",
            "id": str(artifact_id),
            "workspaceId": str(workspace_id),
            "opportunityId": str(role.id),
            "title": output["title"].strip(),
            "content": output["content"].strip(),
            "tone": tone,
            "generationMetadata": {
                "generatedBy": "ai",
                "modelMetadata": {
                    "provider": "openai",
                    "model": ai_result["model"],
                    "promptVersion": PROMPT_VERSION,
                    "rulesetVersion": (
                        evaluation.ruleset_version if evaluation is not None else None
                    ),
                    "inputTokenEstimate": ai_result.get("input_token_estimate"),
                    "outputTokenEstimate": ai_result.get("output_token_estimate"),
                    "latencyMs": ai_result.get("latency_ms"),
                },
                "promptVersion": PROMPT_VERSION,
                "inputHash": input_hash,
                "groundingSourceIds": _grounding_source_ids(source_version),
                "warnings": warnings,
            },
            "editHistory": [],
            "exportMetadata": [],
            "revision": {
                "revisionId": str(uuid.uuid4()),
                "parentArtifactId": str(prior.id) if prior is not None else None,
                "revisionNumber": revision_number,
                "changeSummary": "Initial cover letter artifact."
                if revision_number == 1
                else "Regenerated cover letter artifact.",
                "createdAt": now,
            },
            "metadata": {
                "targetEvaluationId": str(evaluation.id) if evaluation is not None else None,
                "sourceResume": _source_resume_metadata(source_version),
                "generationStatus": ai_result.get("status"),
                "toneStandard": "neutral_professional",
                "contentHash": _prefixed_hash(output["content"]),
            },
            "createdAt": now,
            "updatedAt": now,
        }

    def _enforce_truthfulness(
        self,
        *,
        output: dict[str, Any],
        source_text: str | None,
        evaluation: StrideEvaluation | None,
    ) -> None:
        unsupported_claims = [
            claim.strip()
            for claim in output.get("unsupported_claims", [])
            if claim and claim.strip()
        ]
        if unsupported_claims:
            raise CoverLetterArtifactTruthfulnessError(
                "Cover letter generator reported unsupported claims"
            )

        content = output["content"].casefold()
        banned_openings = ("i'm excited to apply", "i am excited to apply", "i am thrilled", "i'm thrilled")
        if any(phrase in content for phrase in banned_openings):
            raise CoverLetterArtifactValidationError(
                "Cover letter tone is not neutral professional"
            )

        if source_text is None or evaluation is None:
            return

        source = source_text.casefold()
        for keyword in evaluation.missing_keywords or []:
            normalized = str(keyword).strip().casefold()
            if normalized and normalized in content and normalized not in source:
                raise CoverLetterArtifactTruthfulnessError(
                    "Generated cover letter included a missing keyword unsupported by source"
                )

    def _validate_contract(self, artifact: dict[str, Any]) -> None:
        try:
            self._schema_validator.validate(artifact)
        except JsonSchemaValidationError as exc:
            raise CoverLetterArtifactValidationError(
                f"Cover letter artifact contract validation failed: {exc.message}"
            ) from exc

    def _get_active_role(self, *, role_id: uuid.UUID, user_id: uuid.UUID) -> Role | None:
        return self.db.scalar(
            select(Role)
            .options(joinedload(Role.company), joinedload(Role.source))
            .where(
                Role.id == role_id,
                Role.user_id == user_id,
                Role.deleted_at.is_(None),
                Role.status != RoleStatus.ARCHIVED.value,
            )
        )

    def _get_evaluation(
        self,
        *,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        evaluation_id: uuid.UUID | None,
    ) -> StrideEvaluation | None:
        filters = [
            StrideEvaluation.user_id == user_id,
            StrideEvaluation.role_id == role_id,
            StrideEvaluation.deleted_at.is_(None),
        ]
        if evaluation_id is not None:
            filters.append(StrideEvaluation.id == evaluation_id)
        statement = (
            select(StrideEvaluation)
            .where(*filters)
            .order_by(StrideEvaluation.created_at.desc(), StrideEvaluation.id.desc())
            .limit(1)
        )
        return self.db.scalar(statement)

    def _get_source_version(
        self,
        *,
        user_id: uuid.UUID,
        source_version_id: uuid.UUID | None,
    ) -> ResumeSourceVersion | None:
        filters = [ResumeSourceVersion.user_id == user_id]
        if source_version_id is None:
            filters.append(ResumeSourceVersion.is_active.is_(True))
        else:
            filters.append(ResumeSourceVersion.id == source_version_id)
        return self.db.scalar(
            select(ResumeSourceVersion)
            .options(joinedload(ResumeSourceVersion.source))
            .where(*filters)
            .order_by(
                ResumeSourceVersion.updated_at.desc(),
                ResumeSourceVersion.id.desc(),
            )
            .limit(1)
        )

    def _latest_prior_artifact(
        self,
        *,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> GeneratedArtifact | None:
        statement = (
            select(GeneratedArtifact)
            .where(
                GeneratedArtifact.user_id == user_id,
                GeneratedArtifact.role_id == role_id,
                GeneratedArtifact.artifact_type == "cover_letter",
                GeneratedArtifact.deleted_at.is_(None),
            )
            .order_by(GeneratedArtifact.created_at.desc(), GeneratedArtifact.id.desc())
        )
        for artifact in self.db.scalars(statement):
            contract = artifact.artifact_metadata.get("contract")
            if isinstance(contract, dict) and contract.get("workspaceId") == str(
                workspace_id
            ):
                return artifact
        return None

    def _rollback_and_log_failure(
        self,
        *,
        user_id: uuid.UUID,
        entity_id: uuid.UUID,
        role_id: uuid.UUID,
        error_type: str,
    ) -> None:
        self.db.rollback()
        self._log_activity(
            user_id=user_id,
            entity_id=entity_id,
            action="cover_letter_artifact.failed",
            details={
                "role_id": str(role_id),
                "error_type": error_type,
            },
        )
        self.db.commit()

    def _log_activity(
        self,
        *,
        user_id: uuid.UUID,
        entity_id: uuid.UUID,
        action: str,
        details: dict[str, Any],
    ) -> None:
        self.activity_log.append(
            user_id=user_id,
            entity_type="cover_letter_artifact",
            entity_id=entity_id,
            action=action,
            details=details,
        )


def _cover_letter_artifact_validator() -> Draft7Validator:
    schema_path = (
        Path(__file__).resolve().parents[3]
        / "packages"
        / "contracts"
        / "generated"
        / "json-schema"
        / "cover-letter-artifact.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema, format_checker=FormatChecker())


def _source_resume_metadata(
    source_version: ResumeSourceVersion | None,
) -> dict[str, Any] | None:
    if source_version is None:
        return None
    return {
        "source_id": str(source_version.source_id),
        "source_name": source_version.source.name if source_version.source else None,
        "source_type": source_version.source.source_type
        if source_version.source
        else None,
        "version_id": str(source_version.id),
        "version_label": source_version.version_label,
        "content_hash": resume_source_hash(source_version),
    }


def _grounding_source_ids(source_version: ResumeSourceVersion | None) -> list[str]:
    if source_version is None:
        return []
    return [str(source_version.source_id), str(source_version.id)]


def _prefixed_hash(payload: Any) -> str:
    encoded = (
        payload.encode("utf-8")
        if isinstance(payload, str)
        else json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    )
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
