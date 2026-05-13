import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Role


class RoleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: uuid.UUID,
        company_id: uuid.UUID,
        title: str,
        description: str | None = None,
        location: str | None = None,
        employment_type: str | None = None,
        source_url: str | None = None,
    ) -> Role:
        role = Role(
            user_id=user_id,
            company_id=company_id,
            title=title,
            description=description,
            location=location,
            employment_type=employment_type,
            source_url=source_url,
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
