import psycopg2
from fastapi import APIRouter, HTTPException
from schemas import LoginRequest, UserCreate
from database import get_connection
from auth import verify_password, generate_token, hash_password, ensure_habit_valid

router = APIRouter()


@router.post("/logins")
def login(credentials: LoginRequest):
    username = credentials.username
    password = credentials.password

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        existing_user = cursor.fetchone()

        if not existing_user:
            raise HTTPException(status_code=401, detail="Invalid credentials.")

        hashed_password = existing_user[2]  # hashed_password is element 2 in tuple
        match = verify_password(password, hashed_password)

        if match:
            user_id = existing_user[0]
            payload = {
                "user_id": user_id,
                "username": username,
            }  # TODO: make payload include issued at timestamp, expiration etc
            token = generate_token(payload)
            print("tokenn:", token)
            return token
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials.")
    except psycopg2.Error as e:
        return {"error": "Unable to log in due to a database error."}, 500
    finally:
        cursor.close()
        conn.close()


@router.post("/users", status_code=201)  # returns 201 when user is created successfully
def create_user(user: UserCreate):
    username = user.username
    password = user.password

    conn = get_connection()  # opens fresh connection
    cursor = conn.cursor()  # creates cursor that runs SQL query

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed_password = hash_password(password)

        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING user_id;",
            (username, hashed_password),
        )

        user_id = cursor.fetchone()[0]  # returns first val in tuple aka user_id
        conn.commit()  # makes insert SQL statement permanent

        return {"user_id": user_id, "username": username}
    except psycopg2.Error as e:
        return {"error": "Unable to create new user due to database error."}, 500
    finally:
        cursor.close()
        conn.close()
