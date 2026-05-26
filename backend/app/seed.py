import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import SOURCE_DISPLAY_NAMES, SourceType
from app.database import SessionLocal
from app.models import JobSource, User, Workspace

DEFAULT_LOCAL_USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
DEFAULT_WORKSPACE_ID = uuid.UUID("00000000-0000-4000-8000-000000000101")
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
            email_normalized=DEFAULT_LOCAL_USER_EMAIL,
            username="local-user",
            username_normalized="local-user",
            display_name=DEFAULT_LOCAL_USER_DISPLAY_NAME,
            auth_method="local_seeded",
            account_status="active",
        )
        db.add(user)
    else:
        user.email = DEFAULT_LOCAL_USER_EMAIL
        user.email_normalized = DEFAULT_LOCAL_USER_EMAIL
        user.username = user.username or "local-user"
        user.username_normalized = user.username_normalized or "local-user"
        user.display_name = DEFAULT_LOCAL_USER_DISPLAY_NAME
        user.auth_method = "local_seeded"
        user.account_status = "active"

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


def seed_default_workspace(db: Session, user: User) -> Workspace:
    workspace = db.get(Workspace, DEFAULT_WORKSPACE_ID)
    if workspace is None:
        workspace = db.scalar(
            select(Workspace).where(
                Workspace.user_id == user.id,
                Workspace.workspace_metadata["isDefault"].as_boolean().is_(True),
            )
        )

    if workspace is None:
        workspace = Workspace(
            id=DEFAULT_WORKSPACE_ID,
            user_id=user.id,
            title="Default workspace",
            description="Default local workspace for Careero.",
            workspace_type="full_time_individual_contributor",
            status="active",
            preferences={},
            ai_context_summary=None,
            tags=[],
            workspace_metadata={"isDefault": True},
        )
        db.add(workspace)
    else:
        workspace.user_id = user.id
        workspace.title = workspace.title or "Default workspace"
        workspace.workspace_type = (
            workspace.workspace_type or "full_time_individual_contributor"
        )
        workspace.workspace_metadata = {
            **(workspace.workspace_metadata or {}),
            "isDefault": True,
        }

    db.commit()
    db.refresh(workspace)
    return workspace


def seed_local_data(db: Session) -> tuple[User, list[JobSource]]:
    user = seed_default_local_user(db)
    sources = seed_default_job_sources(db, user)
    seed_default_workspace(db, user)
    return user, sources


def main() -> None:
    with SessionLocal() as db:
        user, sources = seed_local_data(db)
        workspace = seed_default_workspace(db, user)
        print(f"Seeded default local user: {user.email} ({user.id})")
        print(f"Seeded {len(sources)} default job sources")
        print(f"Seeded default workspace: {workspace.title} ({workspace.id})")


if __name__ == "__main__":
    main()
