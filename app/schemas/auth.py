
from datetime import datetime
from uuid import UUID

from pydantic import (
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)

from app.schemas.common import BaseSchema


# --------------------------------------------------
# Registration
# --------------------------------------------------

class UserRegister(BaseSchema):

    full_name: str = Field(
        min_length=3,
        max_length=100,
        examples=["Rahul Sharma"],
    )

    email: EmailStr

    password: SecretStr = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:

        if not value.strip():
            raise ValueError("Full name cannot be empty")

        return value


# --------------------------------------------------
# Login
# --------------------------------------------------

class UserLogin(BaseSchema):

    email: EmailStr

    password: SecretStr


# --------------------------------------------------
# Token Response
# --------------------------------------------------

class TokenResponse(BaseSchema):

    access_token: str

    refresh_token: str

    token_type: str = "bearer"

    expires_in: int


# --------------------------------------------------
# Refresh Token Request
# --------------------------------------------------

class RefreshTokenRequest(BaseSchema):

    refresh_token: str = Field(
        min_length=32,
        max_length=512,
    )


# --------------------------------------------------
# Logout Request
# --------------------------------------------------

class LogoutRequest(BaseSchema):

    refresh_token: str = Field(
        min_length=32,
        max_length=512,
    )


# --------------------------------------------------
# User Response
# --------------------------------------------------

class UserResponse(BaseSchema):

    id: UUID

    full_name: str

    email: EmailStr

    is_active: bool

    is_verified: bool

    created_at: datetime


# --------------------------------------------------
# Change Password
# --------------------------------------------------

class ChangePasswordRequest(BaseSchema):

    current_password: SecretStr

    new_password: SecretStr = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: SecretStr) -> SecretStr:

        password = value.get_secret_value()

        if len(password.strip()) < 8:
            raise ValueError(
                "Password must contain at least 8 non-whitespace characters"
            )

        return value
