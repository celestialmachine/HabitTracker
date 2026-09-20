from fastapi import HTTPException, Request

import jwt
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")


def hash_password(password):
    password_bytes = password.encode("utf-8")
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt=bcrypt.gensalt())
    hashed_password_str = hashed_password_bytes.decode(
        "utf-8"
    )  # bytes -> str necessary bc my DB requires password_hash to be a str type
    return hashed_password_str


def verify_password(password, hashed_password):
    password_bytes = password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)


def generate_token(payload):
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def extract_token_from_header(request: Request):
    auth_header = request.headers["Authorization"]
    token = auth_header.split(" ")[1]
    return token


def verify_token(token: str) -> dict:
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")
