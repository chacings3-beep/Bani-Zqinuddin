import os
import secrets

from fastapi import Cookie, HTTPException, status


ADMIN_SESSIONS: set[str] = set()


def verify_pin(pin: str) -> bool:
    configured_pin = os.environ.get("ADMIN_PIN", "")
    return bool(configured_pin) and secrets.compare_digest(pin, configured_pin)


def create_session() -> str:
    token = secrets.token_urlsafe(32)
    ADMIN_SESSIONS.add(token)
    return token


def require_admin(admin_session: str | None = Cookie(default=None)) -> str:
    if not admin_session or admin_session not in ADMIN_SESSIONS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin perlu login")
    return admin_session


def revoke_session(token: str | None) -> None:
    if token:
        ADMIN_SESSIONS.discard(token)