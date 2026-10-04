import pytest
from fastapi import HTTPException, Request
from auth import (
    hash_password,
    verify_password,
    generate_token,
    verify_token,
)
from datetime import datetime, timedelta


def test_hash_and_verify_correct_password():
    password = "password123"
    hashed_password = hash_password(password)
    assert verify_password(password, hashed_password)


def test_hash_and_verify_incorrect_password():
    password = "password123"
    hashed_password = hash_password(password)
    assert not verify_password("wrongpassword", hashed_password)


def test_generate_and_verify_valid_token():
    token = generate_token({"user_id": 1, "username": "user1"})
    decoded = verify_token(token)
    assert decoded["user_id"] == 1
    assert decoded["username"] == "user1"


def test_verify_tampered_token_raises_error():
    token = generate_token({"user_id": 1, "username": "user1"})
    tampered_token = token[:-5] + "aaaaa"
    with pytest.raises(HTTPException) as exc_info:
        verify_token(tampered_token)
    assert exc_info.value.status_code == 401


# TODO: test expired token
