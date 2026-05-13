import uuid

from sqlalchemy.orm import Session

from app.models import Role
from app.repositories.roles import RoleRepository


class RoleService:
    def __init__(self, db: Session) -> None:
        self.repository = RoleRepository(db)

    def create_role(
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
        return self.repository.create(
            user_id=user_id,
            company_id=company_id,
            title=title,
            description=description,
            location=location,
            employment_type=employment_type,
            source_url=source_url,
        )

    def get_role_for_user(
        self,
        *,
        role_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Role | None:
        return self.repository.get_by_id_for_user(role_id=role_id, user_id=user_id)
