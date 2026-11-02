import hashlib
import secrets
import uuid
import jwt

from datetime import datetime, timedelta, timezone

from pwdlib import PasswordHash

from app.core.config import settings

# --------------------------------------------------
# Password Hashing
# --------------------------------------------------

password_hasher = PasswordHash.recommended()

def password_hash(password: str) -> str:
    """
    Hash a plain-text password using Argon2.
    Never store the original password.
    """
    return password_hasher.hash(password)

def verify_password(
    plain_password: str,
    hashed_password: str
)->bool:
    """
    Verify a plain-text password against its stored hash.
    """

    return password_hasher.verify(
        plain_password,
        hashed_password
    )

# --------------------------------------------------
# JWT Access Token
# --------------------------------------------------

def create_access_token(subject: str) -> str:
    """
    Generate a short-lived JWT access token.
    """

    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
        "jti": str(uuid.uuid4()),
        "iss": settings.JWT_ISSUER,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )

def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.
    Raises jwt.InvalidTokenError for invalid tokens.
    """

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM],
        issuer=settings.JWT_ISSUER,
        options={
            "require": [
                "sub",
                "iat",
                "exp",
                "jti",
                "iss",
                "type",
            ]
        }
    )

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type")

    return payload

# --------------------------------------------------
# Refresh Token
# --------------------------------------------------

def generate_refresh_token() -> str:
    """
    Generate a cryptographically secure opaque token.
    Return the raw token only once to the client.
    """
    return secrets.token_urlsafe(64)


def hash_refresh_token(refresh_token: str) -> str:
    """
    Hash the refresh token before storing it in PostgreSQL.
    """
    return hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()