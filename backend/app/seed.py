import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import SOURCE_DISPLAY_NAMES, SourceType
from app.database import SessionLocal
from app.models import JobSource, User

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


def seed_default_job_sources(db: Session, user: User) -> list[JobSource]:
    sources: list[JobSource] = []

    for source_type, display_name in SOURCE_DISPLAY_NAMES.items():
        source = db.scalar(
            select(JobSource).where(
                JobSource.user_id == user.id,
                JobSource.source_type == source_type.value,
            )
        )

        if source is None:
            source = JobSource(
                user_id=user.id,
                name=display_name,
                source_type=source_type.value,
            )
            db.add(source)
        else:
            source.name = display_name

        sources.append(source)

    db.commit()
    for source in sources:
        db.refresh(source)
    return sources


def seed_local_data(db: Session) -> tuple[User, list[JobSource]]:
    user = seed_default_local_user(db)
    sources = seed_default_job_sources(db, user)
    return user, sources


def main() -> None:
    with SessionLocal() as db:
        user, sources = seed_local_data(db)
        print(f"Seeded default local user: {user.email} ({user.id})")
        print(f"Seeded {len(sources)} default job sources")


if __name__ == "__main__":
    main()
