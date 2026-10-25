"""JWT authentication and role checks for protected REST endpoints."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Officer

ROLES = frozenset({"officer", "supervisor", "admin"})
PASSWORD_HASH_ITERATIONS = 600_000
TOKEN_LIFETIME_MINUTES = int(os.environ.get("JWT_LIFETIME_MINUTES", "30"))
if TOKEN_LIFETIME_MINUTES < 1:
    raise RuntimeError("JWT_LIFETIME_MINUTES must be at least 1")
JWT_ISSUER = "awazrakshak"
JWT_AUDIENCE = "awazrakshak-api"
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Passwords must contain at least 12 characters")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
    )
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_HASH_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_text, digest_text = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, int(iterations)
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, UnicodeError):
        return False


def _jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET_KEY", "")
    if len(secret.encode("utf-8")) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT_SECRET_KEY must be configured with at least 32 bytes",
        )
    return secret


def create_access_token(officer: Officer) -> tuple[str, int]:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=TOKEN_LIFETIME_MINUTES)
    token = jwt.encode(
        {
            "sub": officer.id,
            "role": officer.role,
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
            "iat": now,
            "exp": expires,
        },
        _jwt_secret(),
        algorithm="HS256",
    )
    return token, int((expires - now).total_seconds())


def get_current_officer(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    db: Annotated[Session, Depends(get_db)],
) -> Officer:
    unauthenticated = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid bearer token required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.casefold() != "bearer":
        raise unauthenticated
    try:
        claims = jwt.decode(
            credentials.credentials,
            _jwt_secret(),
            algorithms=["HS256"],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={"require": ["sub", "role", "iat", "exp"]},
        )
    except HTTPException:
        raise
    except jwt.PyJWTError as exc:
        raise unauthenticated from exc
    officer = db.scalar(select(Officer).where(Officer.id == claims["sub"]))
    if (
        officer is None
        or not officer.active
        or officer.role not in ROLES
        or claims["role"] != officer.role
    ):
        raise unauthenticated
    return officer


def require_roles(*roles: str) -> Callable:
    allowed = frozenset(roles)

    def dependency(
        officer: Annotated[Officer, Depends(get_current_officer)],
    ) -> Officer:
        if officer.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This role is not permitted to perform the action",
            )
        return officer

    return dependency
