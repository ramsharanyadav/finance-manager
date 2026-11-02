
import pytest

from pydantic import ValidationError

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    RefreshTokenRequest,
)


def test_valid_registration():

    user = UserRegister(
        full_name="Rahul Sharma",
        email="rahul@example.com",
        password="StrongPassword123!",
    )

    assert user.full_name == "Rahul Sharma"
    assert user.email == "rahul@example.com"


def test_invalid_registration_email():

    with pytest.raises(ValidationError):

        UserRegister(
            full_name="Rahul Sharma",
            email="invalid-email",
            password="StrongPassword123!",
        )


def test_short_registration_password():

    with pytest.raises(ValidationError):

        UserRegister(
            full_name="Rahul Sharma",
            email="rahul@example.com",
            password="short",
        )


def test_valid_login():

    login = UserLogin(
        email="rahul@example.com",
        password="StrongPassword123!",
    )

    assert login.email == "rahul@example.com"


def test_invalid_refresh_token():

    with pytest.raises(ValidationError):

        RefreshTokenRequest(
            refresh_token="short",
        )
