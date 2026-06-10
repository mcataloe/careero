import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Opportunity, Role


class RoleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        company_id: uuid.UUID,
        source_id: uuid.UUID | None,
        title: str,
        job_url: str | None = None,
        location: str | None = None,
        remote_type: str | None = None,
        compensation_min=None,
        compensation_max=None,
        compensation_currency: str | None = None,
        raw_description: str | None = None,
        normalized_description: str | None = None,
        parse_metadata: dict | None = None,
        status: str = "found",
        date_found=None,
        date_posted=None,
    ) -> Role:
        role = Role(
            user_id=user_id,
            workspace_id=workspace_id,
            company_id=company_id,
            source_id=source_id,
            title=title,
            job_url=job_url,
            location=location,
            remote_type=remote_type,
            compensation_min=compensation_min,
            compensation_max=compensation_max,
            compensation_currency=compensation_currency,
            raw_description=raw_description,
            normalized_description=normalized_description,
            parse_metadata=parse_metadata or {},
            status=status,
            date_found=date_found,
            date_posted=date_posted,
        )
        self.db.add(role)
        self.db.flush()
        self.db.refresh(role)
        return role

    def get_by_id_for_user(
        self,
        *,
        role_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Role | None:
        statement = select(Role).where(
            Role.id == role_id,
            Role.user_id == user_id,
            Role.deleted_at.is_(None),
        )
        return self.db.scalar(statement)

    def list_for_user(self, *, user_id: uuid.UUID) -> list[Role]:
        statement = (
            select(Role)
            .where(
                Role.user_id == user_id,
                Role.deleted_at.is_(None),
                Role.status != "archived",
            )
            .order_by(Role.date_found.desc(), Role.created_at.desc())
        )
        return list(self.db.scalars(statement))


OpportunityRepository = RoleRepository
