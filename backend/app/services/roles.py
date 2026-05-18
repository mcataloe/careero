import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.constants import RoleStatus
from app.models import Company, JobSource, Role, User
from app.repositories.roles import RoleRepository
from app.schemas.roles import CompanyLookup, RoleCreate, RoleUpdate, SourceLookup
from app.seed import DEFAULT_LOCAL_USER_ID
from app.services.activity_log import ActivityLogService
from app.services.opportunity_intelligence import OpportunityIntelligenceService
from app.services.workspaces import (
    WorkspaceInactiveError,
    WorkspaceNotFoundError,
    WorkspaceService,
)


class RoleIntakeError(Exception):
    pass


class RoleNotFoundError(RoleIntakeError):
    pass


class RoleDependencyNotFoundError(RoleIntakeError):
    pass


class RoleSeedMissingError(RoleIntakeError):
    pass


class RoleWorkspaceNotFoundError(RoleIntakeError):
    pass


class RoleWorkspaceInactiveError(RoleIntakeError):
    pass


class RoleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = RoleRepository(db)
        self.activity_log = ActivityLogService(db)
        self.opportunity_intelligence = OpportunityIntelligenceService(db)

    def get_default_user(self) -> User:
        user = self.db.get(User, DEFAULT_LOCAL_USER_ID)
        if user is None or user.deleted_at is not None:
            raise RoleSeedMissingError("Default local user is missing; run python -m app.seed")
        return user

    def list_roles(self) -> list[Role]:
        user = self.get_default_user()
        statement = (
            select(Role)
            .options(
                joinedload(Role.company),
                joinedload(Role.source),
                joinedload(Role.workspace),
            )
            .where(
                Role.user_id == user.id,
                Role.deleted_at.is_(None),
                Role.status != RoleStatus.ARCHIVED.value,
            )
            .order_by(Role.date_found.desc(), Role.created_at.desc())
        )
        return list(self.db.scalars(statement))

    def get_role(self, role_id: uuid.UUID) -> Role:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise RoleNotFoundError("Role not found")
        return role

    def create_role(self, payload: RoleCreate) -> Role:
        user = self.get_default_user()
        company = self._resolve_company(user_id=user.id, company=payload.company)
        source = self._resolve_source(user_id=user.id, source=payload.source)
        try:
            workspace = WorkspaceService(self.db).resolve_active_workspace(
                user_id=user.id,
                workspace_id=payload.workspace_id,
            )
        except WorkspaceNotFoundError as exc:
            raise RoleWorkspaceNotFoundError("Workspace not found") from exc
        except WorkspaceInactiveError as exc:
            raise RoleWorkspaceInactiveError("Workspace is not active") from exc

        role = self.repository.create(
            user_id=user.id,
            workspace_id=workspace.id,
            company_id=company.id,
            source_id=source.id,
            title=payload.title,
            job_url=payload.job_url,
            location=payload.location,
            remote_type=payload.remote_type,
            compensation_min=payload.compensation_min,
            compensation_max=payload.compensation_max,
            compensation_currency=payload.compensation_currency,
            raw_description=payload.raw_description,
            normalized_description=payload.normalized_description,
            parse_metadata=payload.parse_metadata,
            status=payload.status.value,
            date_found=payload.date_found or date.today(),
            date_posted=payload.date_posted,
        )
        self._log_activity(
            user_id=user.id,
            entity_id=role.id,
            action="role.created",
            details={"title": role.title, "workspace_id": str(workspace.id)},
        )
        self.opportunity_intelligence.refresh_role(role)
        self.db.commit()
        return self._load_role(role.id, user.id)

    def update_role(self, role_id: uuid.UUID, payload: RoleUpdate) -> Role:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise RoleNotFoundError("Role not found")

        updates = payload.model_dump(exclude_unset=True)
        changed_fields: list[str] = []

        company_payload = updates.pop("company", None)
        if company_payload is not None:
            company = self._resolve_company(
                user_id=user.id,
                company=CompanyLookup(**company_payload),
            )
            if role.company_id != company.id:
                role.company_id = company.id
                changed_fields.append("company_id")

        source_payload = updates.pop("source", None)
        if source_payload is not None:
            source = self._resolve_source(
                user_id=user.id,
                source=SourceLookup(**source_payload),
            )
            if role.source_id != source.id:
                role.source_id = source.id
                changed_fields.append("source_id")

        for field_name, value in updates.items():
            if field_name == "status" and value is not None:
                value = value.value if hasattr(value, "value") else value
            if getattr(role, field_name) != value:
                setattr(role, field_name, value)
                changed_fields.append(field_name)

        if changed_fields:
            self.opportunity_intelligence.refresh_role(role)
            self._log_activity(
                user_id=user.id,
                entity_id=role.id,
                action="role.updated",
                details={"changed_fields": sorted(changed_fields)},
            )
            self.db.commit()
        else:
            self.db.rollback()

        return self._load_role(role.id, user.id)

    def refresh_opportunity_intelligence(self, role_id: uuid.UUID) -> Role:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise RoleNotFoundError("Role not found")
        self.opportunity_intelligence.refresh_role(role)
        self._log_activity(
            user_id=user.id,
            entity_id=role.id,
            action="role.opportunity_intelligence.refreshed",
            details={},
        )
        self.db.commit()
        return self._load_role(role.id, user.id)

    def archive_role(self, role_id: uuid.UUID) -> Role:
        user = self.get_default_user()
        role = self._get_active_role(role_id=role_id, user_id=user.id)
        if role is None:
            raise RoleNotFoundError("Role not found")

        role.status = RoleStatus.ARCHIVED.value
        role.deleted_at = datetime.now(timezone.utc)
        self._log_activity(
            user_id=user.id,
            entity_id=role.id,
            action="role.archived",
            details={},
        )
        self.db.commit()
        self.db.refresh(role)
        return role

    def _get_active_role(self, *, role_id: uuid.UUID, user_id: uuid.UUID) -> Role | None:
        statement = (
            select(Role)
            .options(
                joinedload(Role.company),
                joinedload(Role.source),
                joinedload(Role.workspace),
            )
            .where(
                Role.id == role_id,
                Role.user_id == user_id,
                Role.deleted_at.is_(None),
                Role.status != RoleStatus.ARCHIVED.value,
            )
        )
        return self.db.scalar(statement)

    def _load_role(self, role_id: uuid.UUID, user_id: uuid.UUID) -> Role:
        role = self._get_active_role(role_id=role_id, user_id=user_id)
        if role is None:
            raise RoleNotFoundError("Role not found")
        return role

    def _resolve_company(self, *, user_id: uuid.UUID, company: CompanyLookup) -> Company:
        if company.id is not None:
            existing = self.db.get(Company, company.id)
            if (
                existing is None
                or existing.user_id != user_id
                or existing.deleted_at is not None
            ):
                raise RoleDependencyNotFoundError("Company not found")
            return existing

        assert company.name is not None
        name = company.name.strip()
        existing = self.db.scalar(
            select(Company).where(
                Company.user_id == user_id,
                Company.deleted_at.is_(None),
                func.lower(Company.name) == name.lower(),
            )
        )
        if existing is not None:
            if company.website_url and not existing.website_url:
                existing.website_url = company.website_url
            return existing

        created = Company(
            user_id=user_id,
            name=name,
            website_url=company.website_url,
        )
        self.db.add(created)
        self.db.flush()
        self.db.refresh(created)
        return created

    def _resolve_source(self, *, user_id: uuid.UUID, source: SourceLookup) -> JobSource:
        if source.id is not None:
            existing = self.db.get(JobSource, source.id)
            if (
                existing is None
                or existing.user_id != user_id
                or existing.deleted_at is not None
            ):
                raise RoleDependencyNotFoundError("Source not found")
            return existing

        assert source.source_type is not None
        existing = self.db.scalar(
            select(JobSource).where(
                JobSource.user_id == user_id,
                JobSource.deleted_at.is_(None),
                JobSource.source_type == source.source_type.value,
            )
        )
        if existing is None:
            raise RoleSeedMissingError(
                f"Seeded source is missing: {source.source_type.value}"
            )
        return existing

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
            entity_type="role",
            entity_id=entity_id,
            action=action,
            details=details,
        )
