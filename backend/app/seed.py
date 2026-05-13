import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User

DEFAULT_LOCAL_USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
DEFAULT_LOCAL_USER_EMAIL = "local-user@careero.local"
DEFAULT_LOCAL_USER_DISPLAY_NAME = "Local User"


def seed_default_local_user(db: Session) -> User:
    user = db.scalar(
        select(User).where(
            (User.id == DEFAULT_LOCAL_USER_ID) | (User.email == DEFAULT_LOCAL_USER_EMAIL)
        )
    )

    if user is None:
        user = User(
            id=DEFAULT_LOCAL_USER_ID,
            email=DEFAULT_LOCAL_USER_EMAIL,
            display_name=DEFAULT_LOCAL_USER_DISPLAY_NAME,
        )
        db.add(user)
    else:
        user.email = DEFAULT_LOCAL_USER_EMAIL
        user.display_name = DEFAULT_LOCAL_USER_DISPLAY_NAME

    db.commit()
    db.refresh(user)
    return user


def main() -> None:
    with SessionLocal() as db:
        user = seed_default_local_user(db)
        print(f"Seeded default local user: {user.email} ({user.id})")


if __name__ == "__main__":
    main()
