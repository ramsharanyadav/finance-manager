
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    password_hash,
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from app.core.exceptions import (
    AppException,
    ConflictException,
    UnauthorizedException,
    BadRequestException,
)
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    ChangePasswordRequest,
)


class AuthService:

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    # -----------------------------------------------
    # Create access and refresh tokens during login
    # -----------------------------------------------

    @staticmethod
    def _create_tokens(
        db: Session,
        user,
    ) -> TokenResponse:

        now = AuthService._now()
        raw_refresh_token = generate_refresh_token()

        RefreshTokenRepository.create(
            db,
            user_id=user.id,
            token_hash=hash_refresh_token(raw_refresh_token),
            family_id=uuid4(),
            expires_at=now + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            ),
        )

        access_token = create_access_token(
            subject=str(user.id)
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    # -----------------------------------------------
    # Registration
    # -----------------------------------------------

    @staticmethod
    def register_user(
        db: Session,
        data: UserRegister,
    ):

        email = str(data.email).strip().lower()

        try:
            existing_user = UserRepository.get_by_email(
                db, email
            )

            if existing_user:
                raise ConflictException(
                    "An account with this email already exists"
                )

            user_role = RoleRepository.get_by_name(
                db, "USER"
            )

            if user_role is None:
                raise AppException(
                    "Default USER role is not configured"
                )

            user = UserRepository.create(
                db,
                full_name=data.full_name,
                email=email,
                password_hash=password_hash(
                    data.password.get_secret_value()
                ),
            )

            UserRepository.assign_role(
                db, user, user_role
            )

            db.commit()
            db.refresh(user)

            return user

        except IntegrityError as exc:
            db.rollback()
            raise ConflictException(
                "An account with this email already exists"
            ) from exc

        except Exception:
            db.rollback()
            raise

    # -----------------------------------------------
    # Login
    # -----------------------------------------------

    @staticmethod
    def login_user(
        db: Session,
        data: UserLogin,
    ) -> TokenResponse:

        try:
            email = str(data.email).strip().lower()

            user = UserRepository.get_by_email(
                db, email
            )

            if user is None or not verify_password(
                data.password.get_secret_value(),
                user.password_hash,
            ):
                raise UnauthorizedException(
                    "Invalid email or password"
                )

            if not user.is_active:
                raise UnauthorizedException(
                    "Invalid email or password"
                )

            tokens = AuthService._create_tokens(
                db, user
            )

            db.commit()

            return tokens

        except Exception:
            db.rollback()
            raise

    # -----------------------------------------------
    # Refresh Token Rotation
    # -----------------------------------------------

    @staticmethod
    def refresh_tokens(
        db: Session,
        raw_token: str,
    ) -> TokenResponse:

        now = AuthService._now()

        try:
            token_hash = hash_refresh_token(raw_token)

            old_token = RefreshTokenRepository.get_by_hash(
                db,
                token_hash,
                lock=True,
            )

            if old_token is None:
                raise UnauthorizedException(
                    "Invalid refresh token"
                )

            # Reuse detection: an already-revoked token
            # has been presented again.
            if old_token.revoked_at is not None:
                RefreshTokenRepository.revoke_family(
                    db,
                    old_token.family_id,
                    now,
                )
                db.commit()

                raise UnauthorizedException(
                    "Refresh token reuse detected. Please log in again."
                )

            if old_token.expires_at <= now:
                RefreshTokenRepository.revoke(
                    db, old_token, now
                )
                db.commit()

                raise UnauthorizedException(
                    "Refresh token has expired"
                )

            user = UserRepository.get_by_id(
                db, old_token.user_id
            )

            if user is None or not user.is_active:
                RefreshTokenRepository.revoke_family(
                    db,
                    old_token.family_id,
                    now,
                )
                db.commit()

                raise UnauthorizedException(
                    "Invalid refresh token"
                )

            # Generate replacement refresh token.
            new_raw_token = generate_refresh_token()

            new_record = RefreshTokenRepository.create(
                db,
                user_id=user.id,
                token_hash=hash_refresh_token(new_raw_token),
                family_id=old_token.family_id,
                expires_at=now + timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS
                ),
            )

            # Link old token to replacement.
            RefreshTokenRepository.mark_rotated(
                db,
                old_token,
                new_record.id,
                now,
            )

            access_token = create_access_token(
                subject=str(user.id)
            )

            response = TokenResponse(
                access_token=access_token,
                refresh_token=new_raw_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

            db.commit()

            return response

        except Exception:
            db.rollback()
            raise

    # -----------------------------------------------
    # Logout
    # -----------------------------------------------

    @staticmethod
    def logout_user(
        db: Session,
        raw_token: str,
    ) -> None:

        try:
            token_hash = hash_refresh_token(raw_token)

            token = RefreshTokenRepository.get_by_hash(
                db,
                token_hash,
                lock=True,
            )

            if token is not None and token.revoked_at is None:
                RefreshTokenRepository.revoke(
                    db,
                    token,
                    AuthService._now(),
                )

            db.commit()

        except Exception:
            db.rollback()
            raise

    # -----------------------------------------------
    # Change Password
    # -----------------------------------------------

    @staticmethod
    def change_password(
        db: Session,
        user,
        data: ChangePasswordRequest,
    ) -> None:

        try:
            current_password = (
                data.current_password.get_secret_value()
            )
            new_password = (
                data.new_password.get_secret_value()
            )

            if not verify_password(
                current_password,
                user.password_hash,
            ):
                raise BadRequestException(
                    "Current password is incorrect"
                )

            if current_password == new_password:
                raise BadRequestException(
                    "New password must be different"
                )

            new_hash = password_hash(new_password)

            UserRepository.update_password(
                db,
                user,
                new_hash,
            )

            # Invalidate all refresh sessions after password change.
            RefreshTokenRepository.revoke_all_for_user(
                db,
                user.id,
                AuthService._now(),
            )

            db.commit()

        except Exception:
            db.rollback()
            raise