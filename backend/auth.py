"""
Lightweight JWT auth for MSME360.

Two roles: `customer` (MSMEs) and `officer` (bank staff).
Password hashing is bcrypt via passlib; tokens are HS256 JWTs signed with the
JWT_SECRET env var. A dev secret is used if unset — a warning is printed at
import so this can't slip past code review unnoticed.

Users are stored in the same SQLite as the rest of the app.
"""

from __future__ import annotations

import os
import sqlite3
import warnings
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from db import DB_PATH

Role = Literal["customer", "officer"]

# ----- Config -----
_DEV_SECRET = "DEV_ONLY_INSECURE_CHANGE_ME"
JWT_SECRET = os.environ.get("JWT_SECRET", _DEV_SECRET)
if JWT_SECRET == _DEV_SECRET:
    warnings.warn(
        "JWT_SECRET not set — using a well-known dev secret. "
        "Set JWT_SECRET in .env before any non-local deployment.",
        stacklevel=2,
    )
JWT_ALG = "HS256"
JWT_TTL_MINUTES = int(os.environ.get("JWT_TTL_MINUTES", "60"))

# pbkdf2_sha256 has no external C dependency and works cleanly on Python 3.13.
# passlib's bcrypt backend has an upstream incompatibility with bcrypt>=5 where
# `detect_wrap_bug` reads `__about__.__version__` which no longer exists.
_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# ----- Pydantic wire types -----
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    username: str
    expires_at: str  # ISO-8601


class UserInfo(BaseModel):
    username: str
    role: Role


# ----- DB helpers -----
def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_auth_tables() -> None:
    """Create users table + seed two demo accounts.

    Demo accounts are only seeded when the table is empty; production
    deployments should replace them via a real user-provisioning flow.
    """
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('customer', 'officer')),
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            now = datetime.now(timezone.utc).isoformat()
            demo = [
                ("officer_demo", _pwd.hash("officer123"), "officer", now),
                ("customer_demo", _pwd.hash("customer123"), "customer", now),
            ]
            cur.executemany(
                "INSERT INTO users VALUES (?, ?, ?, ?)", demo
            )
        conn.commit()
    finally:
        conn.close()


def create_user(username: str, password: str, role: Role) -> None:
    conn = _conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?)",
                (username, _pwd.hash(password), role, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Username already exists")
    finally:
        conn.close()


def _get_user_row(username: str) -> Optional[sqlite3.Row]:
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cur.fetchone()
    finally:
        conn.close()


# ----- Token issuance / verification -----
def create_access_token(username: str, role: Role) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(minutes=JWT_TTL_MINUTES)
    payload = {"sub": username, "role": role, "exp": expires}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return token, expires


def authenticate(username: str, password: str) -> Optional[UserInfo]:
    row = _get_user_row(username)
    if not row:
        return None
    if not _pwd.verify(password, row["password_hash"]):
        return None
    return UserInfo(username=row["username"], role=row["role"])


def _decode(token: str) -> UserInfo:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload.get("sub")
    role = payload.get("role")
    if not username or role not in ("customer", "officer"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token"
        )
    return UserInfo(username=username, role=role)


# ----- FastAPI Depends -----
def get_current_user(
    request: Request, token: Optional[str] = Depends(_oauth2)
) -> UserInfo:
    # Support both `Authorization: Bearer …` and a raw header for TestClient.
    if not token:
        auth = request.headers.get("Authorization") or ""
        if auth.lower().startswith("bearer "):
            token = auth.split(None, 1)[1]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _decode(token)


def require_officer(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    if user.role != "officer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Officer role required for this action",
        )
    return user


def require_customer(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    if user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer role required for this action",
        )
    return user
