from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerifyMismatchError, VerificationError
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.constants import SOURCE_DISPLAY_NAMES
from app.models import AuthSession, JobSource, User, Workspace
from app.services.current_user import CurrentUserContext


LOCAL_PASSWORD_AUTH_METHOD = "local_password"
ACTIVE_ACCOUNT_STATUS = "active"
GENERIC_LOGIN_ERROR = "Invalid email or password"

_PASSWORD_HASHER = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)


class AuthError(Exception):
    pass


class RegistrationDisabledError(AuthError):
    pass


class DuplicateIdentityError(AuthError):
    pass


class PasswordPolicyError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class InactiveAccountError(AuthError):
    pass


@dataclass(frozen=True)
class AuthSessionResult:
    user: User
    token: str
    session: AuthSession


def normalize_email(value: str) -> str:
    return value.strip().lower()


def build_display_name(first_name: str, last_name: str) -> str:
    return f"{first_name.strip()} {last_name.strip()}".strip()


def hash_password(password: str) -> str:
    return _PASSWORD_HASHER.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return _PASSWORD_HASHER.verify(password_hash, password)
    except (InvalidHashError, VerificationError, VerifyMismatchError):
        return False


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def safe_user_response(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "displayName": user.display_name,
        "salutation": user.salutation,
        "pronouns": user.pronouns,
        "headshotUrl": user.headshot_url,
        "authMethod": user.auth_method,
        "accountStatus": user.account_status,
        "createdAt": user.created_at,
    }


class AuthService:
    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()

    def register_user(
        self,
        *,
        email: str,
        first_name: str,
        last_name: str,
        password: str,
        user_agent: str | None = None,
        ip_hint: str | None = None,
    ) -> AuthSessionResult:
        if not self.settings.allow_registration:
            raise RegistrationDisabledError("Registration is disabled")

        email_clean = email.strip()
        email_normalized = normalize_email(email_clean)
        first_name_clean = first_name.strip()
        last_name_clean = last_name.strip()
        display_name_clean = build_display_name(first_name_clean, last_name_clean)

        self._validate_email(email_clean)
        self._validate_profile_name("First name", first_name_clean)
        self._validate_profile_name("Last name", last_name_clean)
        self._validate_password(password)
        self._ensure_identity_available(email_normalized=email_normalized)

        now = datetime.now(timezone.utc)
        user = User(
            email=email_clean,
            email_normalized=email_normalized,
            first_name=first_name_clean,
            last_name=last_name_clean,
            display_name=display_name_clean,
            password_hash=hash_password(password),
            password_updated_at=now,
            auth_method=LOCAL_PASSWORD_AUTH_METHOD,
            account_status=ACTIVE_ACCOUNT_STATUS,
            failed_login_count=0,
        )
        self.db.add(user)
        self.db.flush()
        self._create_default_job_sources(user)
        self._create_default_workspace(user)
        result = self.create_session(
            user=user,
            user_agent=user_agent,
            ip_hint=ip_hint,
            commit=False,
        )
        user.last_login_at = now
        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(result.session)
        return result

    def login(
        self,
        *,
        email: str,
        password: str,
        user_agent: str | None = None,
        ip_hint: str | None = None,
    ) -> AuthSessionResult:
        identity = email.strip()
        if not identity or not password:
            raise InvalidCredentialsError(GENERIC_LOGIN_ERROR)

        normalized = normalize_email(identity)
        user = self.db.scalar(
            select(User).where(
                or_(
                    User.email_normalized == normalized,
                    User.email == normalized,
                )
            )
        )
        if user is None or not verify_password(password, user.password_hash):
            if user is not None:
                user.failed_login_count = (user.failed_login_count or 0) + 1
                self.db.commit()
            raise InvalidCredentialsError(GENERIC_LOGIN_ERROR)

        if user.deleted_at is not None or user.account_status != ACTIVE_ACCOUNT_STATUS:
            raise InactiveAccountError(GENERIC_LOGIN_ERROR)

        user.failed_login_count = 0
        user.last_login_at = datetime.now(timezone.utc)
        result = self.create_session(
            user=user,
            user_agent=user_agent,
            ip_hint=ip_hint,
            commit=False,
        )
        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(result.session)
        return result

    def create_session(
        self,
        *,
        user: User,
        user_agent: str | None = None,
        ip_hint: str | None = None,
        commit: bool = True,
    ) -> AuthSessionResult:
        now = datetime.now(timezone.utc)
        token = secrets.token_urlsafe(48)
        session = AuthSession(
            user_id=user.id,
            session_token_hash=hash_session_token(token),
            expires_at=now + timedelta(days=self.settings.auth_session_days),
            last_seen_at=now,
            user_agent=(user_agent or "")[:512] or None,
            ip_hint=(ip_hint or "")[:100] or None,
            session_metadata={},
        )
        self.db.add(session)
        if commit:
            self.db.commit()
            self.db.refresh(session)
        else:
            self.db.flush()
        return AuthSessionResult(user=user, token=token, session=session)

    def resolve_session(self, token: str | None) -> tuple[User, AuthSession] | None:
        if not token:
            return None
        token_hash = hash_session_token(token)
        now = datetime.now(timezone.utc)
        session = self.db.scalar(
            select(AuthSession).where(AuthSession.session_token_hash == token_hash)
        )
        if (
            session is None
            or session.revoked_at is not None
            or session.expires_at <= now
        ):
            return None
        user = self.db.get(User, session.user_id)
        if (
            user is None
            or user.deleted_at is not None
            or user.account_status != ACTIVE_ACCOUNT_STATUS
        ):
            return None
        session.last_seen_at = now
        self.db.commit()
        return user, session

    def current_user_context_from_session(
        self,
        token: str | None,
    ) -> CurrentUserContext | None:
        resolved = self.resolve_session(token)
        if resolved is None:
            return None
        user, _ = resolved
        return CurrentUserContext(
            user_id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            mode="authenticated",
        )

    def revoke_session(self, token: str | None) -> None:
        if not token:
            return
        session = self.db.scalar(
            select(AuthSession).where(
                AuthSession.session_token_hash == hash_session_token(token)
            )
        )
        if session is not None and session.revoked_at is None:
            session.revoked_at = datetime.now(timezone.utc)
            self.db.commit()

    def user_from_session(self, token: str | None) -> User | None:
        resolved = self.resolve_session(token)
        return resolved[0] if resolved is not None else None

    def _validate_email(self, email: str) -> None:
        if not email or "@" not in email or len(email) > 320:
            raise PasswordPolicyError("Enter a valid email address.")

    def _validate_profile_name(self, label: str, value: str) -> None:
        if not value:
            raise PasswordPolicyError(f"{label} is required.")
        if len(value) > 100:
            raise PasswordPolicyError(f"{label} must be 100 characters or fewer.")

    def _validate_password(self, password: str) -> None:
        if len(password) < self.settings.password_min_length:
            raise PasswordPolicyError(
                f"Password must be at least {self.settings.password_min_length} characters."
            )

    def _ensure_identity_available(
        self,
        *,
        email_normalized: str,
    ) -> None:
        existing = self.db.scalar(
            select(User.id).where(
                or_(
                    User.email_normalized == email_normalized,
                    User.email == email_normalized,
                )
            )
        )
        if existing is not None:
            raise DuplicateIdentityError("Email is already registered.")

    def _create_default_job_sources(self, user: User) -> None:
        for source_type, display_name in SOURCE_DISPLAY_NAMES.items():
            self.db.add(
                JobSource(
                    user_id=user.id,
                    name=display_name,
                    source_type=source_type.value,
                )
            )

    def _create_default_workspace(self, user: User) -> None:
        self.db.add(
            Workspace(
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
        )
