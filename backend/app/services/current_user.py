from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import User
from app.seed import (
    DEFAULT_LOCAL_USER_DISPLAY_NAME,
    DEFAULT_LOCAL_USER_EMAIL,
    DEFAULT_LOCAL_USER_ID,
)


class CurrentUserResolutionError(Exception):
    pass


@dataclass(frozen=True)
class CurrentUserContext:
    user_id: uuid.UUID
    email: str | None = None
    display_name: str | None = None
    mode: str = "local"


class LocalUserContext(CurrentUserContext):
    def __init__(
        self,
        *,
        user_id: uuid.UUID = DEFAULT_LOCAL_USER_ID,
        email: str | None = DEFAULT_LOCAL_USER_EMAIL,
        display_name: str | None = DEFAULT_LOCAL_USER_DISPLAY_NAME,
    ) -> None:
        super().__init__(
            user_id=user_id,
            email=email,
            display_name=display_name,
            mode="local",
        )


def get_current_user_context() -> CurrentUserContext:
    """Return the local seeded user context; this is not production auth."""
    return LocalUserContext()


def resolve_current_user(
    db: Session,
    current_user_context: CurrentUserContext | None = None,
) -> User:
    context = current_user_context or get_current_user_context()
    user = db.get(User, context.user_id)
    if user is None or user.deleted_at is not None:
        raise CurrentUserResolutionError(
            "Current local user is missing; run python -m app.seed"
        )
    return user
