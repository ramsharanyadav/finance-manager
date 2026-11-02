
from app.core.security import (
    password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_refresh_token,
)


def test_password_hashing():
    password = "StrongPassword123!"

    hashed = password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_access_token():
    user_id = "test-user-123"

    token = create_access_token(user_id)

    payload = decode_access_token(token)

    assert payload["sub"] == user_id
    assert payload["type"] == "access"


def test_refresh_token():
    token = generate_refresh_token()

    hashed = hash_refresh_token(token)

    assert token != hashed
    assert len(hashed) == 64
    assert hash_refresh_token(token) == hashed
