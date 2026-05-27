from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.services.auth import (
    AuthService,
    DuplicateIdentityError,
    GENERIC_LOGIN_ERROR,
    InactiveAccountError,
    InvalidCredentialsError,
    PasswordPolicyError,
    RegistrationDisabledError,
    safe_user_response,
)
from app.services.current_user import (
    CurrentUserContext,
    LocalUserContext,
    reset_request_current_user_context,
    set_request_current_user_context,
)


router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=256)


class AuthUserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    auth_method: str
    account_status: str
    created_at: str


def _cookie_name(settings: Settings) -> str:
    return settings.auth_session_cookie_name


def _set_session_cookie(
    response: Response,
    *,
    settings: Settings,
    token: str,
) -> None:
    response.set_cookie(
        key=_cookie_name(settings),
        value=token,
        max_age=settings.auth_session_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )


def _clear_session_cookie(response: Response, *, settings: Settings) -> None:
    response.delete_cookie(
        key=_cookie_name(settings),
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )


def _token_from_request(request: Request, settings: Settings) -> str | None:
    return request.cookies.get(_cookie_name(settings))


def _client_host(request: Request) -> str | None:
    return request.client.host if request.client is not None else None


def _user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


def _serialize_user(user) -> dict:
    payload = {}
    for key, value in safe_user_response(user).items():
        if value is None:
            payload[key] = None
        elif hasattr(value, "isoformat"):
            payload[key] = value.isoformat()
        else:
            payload[key] = str(value)
    return payload


async def require_authenticated_current_user_context(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[CurrentUserContext, None]:
    if not settings.enable_password_auth:
        context = LocalUserContext()
    else:
        context = AuthService(db, settings).current_user_context_from_session(
            _token_from_request(request, settings)
        )
        if context is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

    token = set_request_current_user_context(context)
    try:
        yield context
    finally:
        reset_request_current_user_context(token)


@router.post(
    "/register",
    response_model=AuthUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not settings.enable_password_auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password authentication is disabled",
        )
    try:
        result = AuthService(db, settings).register_user(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            password=payload.password,
            user_agent=_user_agent(request),
            ip_hint=_client_host(request),
        )
    except RegistrationDisabledError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except DuplicateIdentityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except PasswordPolicyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    _set_session_cookie(response, settings=settings, token=result.token)
    return _serialize_user(result.user)


@router.post("/login", response_model=AuthUserResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not settings.enable_password_auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password authentication is disabled",
        )
    try:
        result = AuthService(db, settings).login(
            email=payload.email,
            password=payload.password,
            user_agent=_user_agent(request),
            ip_hint=_client_host(request),
        )
    except (InvalidCredentialsError, InactiveAccountError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=GENERIC_LOGIN_ERROR,
        )

    _set_session_cookie(response, settings=settings, token=result.token)
    return _serialize_user(result.user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    AuthService(db, settings).revoke_session(_token_from_request(request, settings))
    _clear_session_cookie(response, settings=settings)
    response.status_code = status.HTTP_204_NO_CONTENT
    return None


@router.get("/me", response_model=AuthUserResponse)
def me(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    user = AuthService(db, settings).user_from_session(
        _token_from_request(request, settings)
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return _serialize_user(user)
