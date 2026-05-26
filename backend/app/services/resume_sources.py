import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import ResumeSource, ResumeSourceVersion, User
from app.schemas.resume_sources import (
    ResumeSourceCreate,
    ResumeSourceUpdate,
    ResumeSourceVersionCreate,
)
from app.services.activity_log import ActivityLogService
from app.services.current_user import CurrentUserResolutionError, resolve_current_user


class ResumeSourceError(Exception):
    pass


class ResumeSourceSeedMissingError(ResumeSourceError):
    pass


class ResumeSourceNotFoundError(ResumeSourceError):
    pass


class ResumeSourceVersionNotFoundError(ResumeSourceError):
    pass


class ActiveResumeSourceNotFoundError(ResumeSourceError):
    pass


class ResumeSourceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.activity_log = ActivityLogService(db)

    def get_default_user(self) -> User:
        try:
            return resolve_current_user(self.db)
        except CurrentUserResolutionError as exc:
            raise ResumeSourceSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            ) from exc

    def create_source(self, payload: ResumeSourceCreate) -> dict[str, Any]:
        user = self.get_default_user()
        source = ResumeSource(
            user_id=user.id,
            name=payload.name.strip(),
            source_type=payload.source_type.value,
        )
        self.db.add(source)
        self.db.flush()
        version = self._create_version(
            user_id=user.id,
            source_id=source.id,
            payload=ResumeSourceVersionCreate(
                version_label=payload.version_label,
                raw_text=payload.raw_text,
                normalized_summary=payload.normalized_summary,
                is_active=payload.is_active,
            ),
        )
        self._log_activity(
            user_id=user.id,
            entity_id=source.id,
            action="resume_source.created",
            details={"version_id": str(version.id)},
        )
        self.db.commit()
        return self.get_source(source.id)

    def list_sources(self) -> list[dict[str, Any]]:
        user = self.get_default_user()
        sources = list(
            self.db.scalars(
                select(ResumeSource)
                .where(ResumeSource.user_id == user.id)
                .order_by(ResumeSource.created_at.desc(), ResumeSource.id.desc())
            )
        )
        return [self._serialize_source(source) for source in sources]

    def get_source(self, source_id: uuid.UUID) -> dict[str, Any]:
        user = self.get_default_user()
        source = self._get_source(source_id=source_id, user_id=user.id)
        if source is None:
            raise ResumeSourceNotFoundError("Resume source not found")
        return self._serialize_source(source)

    def update_source(
        self,
        source_id: uuid.UUID,
        payload: ResumeSourceUpdate,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        source = self._get_source(source_id=source_id, user_id=user.id)
        if source is None:
            raise ResumeSourceNotFoundError("Resume source not found")

        updates = payload.model_dump(exclude_unset=True)
        changed_fields: list[str] = []
        if "name" in updates and updates["name"] is not None:
            next_name = updates["name"].strip()
            if source.name != next_name:
                source.name = next_name
                changed_fields.append("name")
        if "source_type" in updates and updates["source_type"] is not None:
            next_type = updates["source_type"].value
            if source.source_type != next_type:
                source.source_type = next_type
                changed_fields.append("source_type")

        if changed_fields:
            self._log_activity(
                user_id=user.id,
                entity_id=source.id,
                action="resume_source.updated",
                details={"changed_fields": sorted(changed_fields)},
            )
            self.db.commit()
        else:
            self.db.rollback()
        return self.get_source(source.id)

    def create_version(
        self,
        source_id: uuid.UUID,
        payload: ResumeSourceVersionCreate,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        source = self._get_source(source_id=source_id, user_id=user.id)
        if source is None:
            raise ResumeSourceNotFoundError("Resume source not found")

        version = self._create_version(
            user_id=user.id,
            source_id=source.id,
            payload=payload,
        )
        self._log_activity(
            user_id=user.id,
            entity_id=source.id,
            action="resume_source.version_created",
            details={"version_id": str(version.id)},
        )
        self.db.commit()
        return self._serialize_version(version)

    def get_active(self) -> dict[str, Any]:
        user = self.get_default_user()
        version = self._get_active_version(user.id)
        if version is None:
            raise ActiveResumeSourceNotFoundError("Active resume source not found")
        return {
            "source": self._serialize_source(version.source),
            "version": self._serialize_version(version),
        }

    def get_active_version_for_user(
        self,
        user_id: uuid.UUID,
    ) -> ResumeSourceVersion | None:
        return self._get_active_version(user_id)

    def activate_version(
        self,
        source_id: uuid.UUID,
        version_id: uuid.UUID,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        source = self._get_source(source_id=source_id, user_id=user.id)
        if source is None:
            raise ResumeSourceNotFoundError("Resume source not found")
        version = self._get_version(
            source_id=source.id,
            version_id=version_id,
            user_id=user.id,
        )
        if version is None:
            raise ResumeSourceVersionNotFoundError("Resume source version not found")

        self._deactivate_active_versions(user.id)
        version.is_active = True
        self._log_activity(
            user_id=user.id,
            entity_id=source.id,
            action="resume_source.version_activated",
            details={"version_id": str(version.id)},
        )
        self.db.commit()
        return self._serialize_version(version)

    def _create_version(
        self,
        *,
        user_id: uuid.UUID,
        source_id: uuid.UUID,
        payload: ResumeSourceVersionCreate,
    ) -> ResumeSourceVersion:
        if payload.is_active:
            self._deactivate_active_versions(user_id)
        version = ResumeSourceVersion(
            user_id=user_id,
            source_id=source_id,
            version_label=payload.version_label.strip(),
            raw_text=payload.raw_text,
            normalized_summary=payload.normalized_summary,
            is_active=payload.is_active,
        )
        self.db.add(version)
        self.db.flush()
        self.db.refresh(version)
        return version

    def _deactivate_active_versions(self, user_id: uuid.UUID) -> None:
        self.db.execute(
            update(ResumeSourceVersion)
            .where(
                ResumeSourceVersion.user_id == user_id,
                ResumeSourceVersion.is_active.is_(True),
            )
            .values(is_active=False)
        )
        self.db.flush()

    def _get_source(
        self,
        *,
        source_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ResumeSource | None:
        return self.db.scalar(
            select(ResumeSource).where(
                ResumeSource.id == source_id,
                ResumeSource.user_id == user_id,
            )
        )

    def _get_version(
        self,
        *,
        source_id: uuid.UUID,
        version_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ResumeSourceVersion | None:
        return self.db.scalar(
            select(ResumeSourceVersion).where(
                ResumeSourceVersion.id == version_id,
                ResumeSourceVersion.source_id == source_id,
                ResumeSourceVersion.user_id == user_id,
            )
        )

    def _get_active_version(self, user_id: uuid.UUID) -> ResumeSourceVersion | None:
        return self.db.scalar(
            select(ResumeSourceVersion)
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

    def _latest_version(self, source_id: uuid.UUID) -> ResumeSourceVersion | None:
        return self.db.scalar(
            select(ResumeSourceVersion)
            .where(ResumeSourceVersion.source_id == source_id)
            .order_by(
                ResumeSourceVersion.created_at.desc(),
                ResumeSourceVersion.id.desc(),
            )
            .limit(1)
        )

    def _active_version_for_source(
        self,
        source_id: uuid.UUID,
    ) -> ResumeSourceVersion | None:
        return self.db.scalar(
            select(ResumeSourceVersion).where(
                ResumeSourceVersion.source_id == source_id,
                ResumeSourceVersion.is_active.is_(True),
            )
        )

    def _serialize_source(self, source: ResumeSource) -> dict[str, Any]:
        return {
            "id": source.id,
            "name": source.name,
            "source_type": source.source_type,
            "created_at": source.created_at,
            "updated_at": source.updated_at,
            "latest_version": self._serialize_optional_version(
                self._latest_version(source.id)
            ),
            "active_version": self._serialize_optional_version(
                self._active_version_for_source(source.id)
            ),
        }

    def _serialize_optional_version(
        self,
        version: ResumeSourceVersion | None,
    ) -> dict[str, Any] | None:
        return self._serialize_version(version) if version is not None else None

    def _serialize_version(self, version: ResumeSourceVersion) -> dict[str, Any]:
        return {
            "id": version.id,
            "source_id": version.source_id,
            "version_label": version.version_label,
            "raw_text": version.raw_text,
            "normalized_summary": version.normalized_summary,
            "is_active": version.is_active,
            "created_at": version.created_at,
            "updated_at": version.updated_at,
        }

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
            entity_type="resume_source",
            entity_id=entity_id,
            action=action,
            details=details,
        )
