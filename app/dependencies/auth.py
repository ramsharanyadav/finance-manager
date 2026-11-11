
from uuid import UUID

import jwt

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.security import decode_access_token
from app.core.exceptions import (
    UnauthorizedException,
    ForbiddenException,
)
from app.repositories.user_repository import UserRepository


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
):

    if credentials is None:
        raise UnauthorizedException(
            "Authentication required"
        )

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        user_id = UUID(payload["sub"])

    except (jwt.exceptions.InvalidTokenError, ValueError, KeyError):
        raise UnauthorizedException(
            "Invalid or expired access token"
        )

    user = UserRepository.get_by_id(
        db, user_id
    )

    if user is None or not user.is_active:
        raise UnauthorizedException(
            "Invalid or inactive account"
        )

    return user


def require_permission(permission_code: str):

    def permission_checker(
        current_user=Depends(get_current_user),
    ):

        has_permission = any(
            permission.code == permission_code
            for role in current_user.roles
            for permission in role.permissions
        )

        if not has_permission:
            raise ForbiddenException(
                "You do not have permission to perform this action"
            )

        return current_user

    return permission_checker
