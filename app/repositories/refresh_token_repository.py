
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:

    @staticmethod
    def create(
        db: Session,
        *,
        user_id: UUID,
        token_hash: str,
        family_id: UUID,
        expires_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> RefreshToken:

        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(refresh_token)
        db.flush()

        return refresh_token

    @staticmethod
    def get_by_hash(
        db: Session,
        token_hash: str,
        *,
        lock: bool = False,
    ) -> RefreshToken | None:

        statement = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )

        if lock:
            statement = statement.with_for_update()

        return db.scalar(statement)

    @staticmethod
    def mark_rotated(
        db: Session,
        old_token: RefreshToken,
        new_token_id: UUID,
        revoked_at: datetime,
    ) -> None:

        old_token.revoked_at = revoked_at
        old_token.replaced_by_id = new_token_id

        db.flush()

    @staticmethod
    def revoke(
        db: Session,
        refresh_token: RefreshToken,
        revoked_at: datetime,
    ) -> None:

        if refresh_token.revoked_at is None:
            refresh_token.revoked_at = revoked_at

        db.flush()

    @staticmethod
    def revoke_family(
        db: Session,
        family_id: UUID,
        revoked_at: datetime,
    ) -> int:

        statement = (
            update(RefreshToken)
            .where(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
        )

        result = db.execute(statement)

        return result.rowcount or 0
