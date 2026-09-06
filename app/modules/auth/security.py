from datetime import UTC, datetime, timedelta
from typing import Annotated, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db_session
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")

INVITATION_TOKEN_EXPIRE_HOURS = 72


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def create_invitation_token(name: str, email: str, role: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(hours=INVITATION_TOKEN_EXPIRE_HOURS)

    payload = {
        "type": "invitation",
        "name": name,
        "email": email,
        "role": role,
        "exp": expires_at,
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_invitation_token(token: str) -> dict:
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    if payload.get("type") != "invitation":
        raise InvalidTokenError("Invalid invitation token.")

    return payload


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    user_repository = UserRepository(session)
    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive.")

    return user


def require_roles(*allowed_roles: str) -> Callable:
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action.")

        return current_user

    return role_checker