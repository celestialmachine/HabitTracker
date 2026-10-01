# TODO: move routes into their own files
# TODO: move basemodels into their own files
# TODO: write API test scripts using requests library?

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from database import get_connection
from auth import (
    hash_password,
    verify_password,
    generate_token,
    verify_token,
    extract_token_from_header,
)
from pydantic import BaseModel, field_validator

import psycopg2

# creates an empty instance of FastAPI app which will hold all the routes
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows requests from any origin (fine for local dev)
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "welcome! habit tracker is alive"}


class UserCreate(BaseModel):
    username: str  # michy7
    password: str  # password123

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 5:
            raise ValueError("Password must be at least 5 characters.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit.")
        return value


class LoginRequest(BaseModel):
    username: str
    password: str


class HabitCreate(BaseModel):
    content: str


@app.post("/logins")
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


@app.post("/users", status_code=201)  # returns 201 when user is created successfully
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


# TODO: update HTTP date from GMT to PST
@app.post("/habits", status_code=201)
def create_habit(habit: HabitCreate, request: Request):
    content = habit.content
    token = extract_token_from_header(request)

    decoded_payload = verify_token(token)
    user_id = decoded_payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO habits (content, user_id) VALUES (%s, %s) RETURNING habit_id;",
            (content, user_id),
        )
        habit_id = cursor.fetchone()[0]  # returns first tuple val
        conn.commit()
        return {"message": "Habit successfully created!", "habit_id": habit_id}
    except:
        return {"message": "Something went wrong!"}
    finally:
        cursor.close()
        conn.close()


@app.get("/habits", status_code=200)
def get_habits(
    request: Request, status: str = None
):  # status is an optional query param that is appended after '?' in URL
    token = extract_token_from_header(request)
    decoded_payload = verify_token(token)
    user_id = decoded_payload["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if status == "complete":
            cursor.execute(
                "SELECT * FROM habits INNER JOIN completions ON habits.habit_id = completions.habit_id WHERE habits.user_id = %s AND habits.is_active = true AND completions.completion_date = CURRENT_DATE;",
                (user_id,),
            )
        elif status == "incomplete":
            cursor.execute(
                "SELECT * FROM habits LEFT JOIN completions ON habits.habit_id = completions.habit_id AND completions.completion_date = CURRENT_DATE WHERE user_id = %s AND completions.completion_id is NULL;",
                (user_id,),
            )
        else:
            cursor.execute(
                "SELECT * FROM habits WHERE user_id = %s AND is_active = TRUE;",
                (user_id,),
            )

        habits = cursor.fetchall()

        return habits
    except:
        return {"message": "Something went wrong"}
    finally:
        cursor.close()
        conn.close()


@app.post("/habits/{habit_id}/complete", status_code=201)
# habit_id is a path param in the URL
def mark_habit_complete(habit_id: int, request: Request):
    token = extract_token_from_header(request)
    user_id = verify_token(token)["user_id"]  # verify token before proceeding

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT user_id FROM habits WHERE habit_id = %s AND user_id = %s;",
            (
                habit_id,
                user_id,
            ),
        )
        match = cursor.fetchone()
        if match is None:
            raise HTTPException(
                status_code=404,
                detail=f"Habit id#{habit_id} not found.",
            )

        cursor.execute(
            "INSERT INTO completions (habit_id) VALUES (%s) RETURNING completion_id;",
            (habit_id,),
        )
        completion_id = cursor.fetchone()[0]
        conn.commit()
        return {"message": f"Habit id#{habit_id} has been marked as completed"}
    except psycopg2.errors.UniqueViolation as e:
        raise HTTPException(
            status_code=400,
            detail=f"Habit id#{habit_id} has already been marked as complete.",
        )
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail="Something went wrong")
    finally:
        cursor.close()
        conn.close()
