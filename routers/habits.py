import psycopg2
from schemas import HabitCreate
from fastapi import APIRouter, HTTPException, Request
from database import get_connection
from typing import Optional
from auth import extract_token_from_header, verify_token, ensure_habit_valid

router = APIRouter()


# TODO: update HTTP date from GMT to PST
@router.post("/habits", status_code=201)
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


@router.get("/habits", status_code=200)
def get_habits(
    request: Request, status: Optional[str] = None
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


@router.post("/habits/{habit_id}/complete", status_code=201)
# habit_id is a path param in the URL
def mark_habit_complete(habit_id: int, request: Request):
    token = extract_token_from_header(request)
    user_id = verify_token(token)["user_id"]  # verify token before proceeding

    conn = get_connection()
    cursor = conn.cursor()
    try:
        ensure_habit_valid(cursor, user_id, habit_id)
        cursor.execute(
            "INSERT INTO completions (habit_id) VALUES (%s) RETURNING completion_id;",
            (habit_id,),
        )
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


# deletes the specified habit's completion row for current date
@router.delete("/habits/{habit_id}/complete")
def mark_habit_incomplete(habit_id: int, request: Request):
    token = extract_token_from_header(request)
    user_id = verify_token(token)["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # TODO: should ensure_habit_valid be inside or outside try block?
        ensure_habit_valid(cursor, user_id, habit_id)
        cursor.execute(
            "DELETE FROM completions WHERE habit_id = %s AND completion_date = CURRENT_DATE;",
            (habit_id,),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return {
                "message": f"Nothing to unmark. Habit #id{habit_id} has not been completed yet today."
            }
        return {"message": f"Habit id#{habit_id} has been marked as incomplete today."}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail="Something went wrong")
    finally:
        cursor.close()
        conn.close()


# TODO: implement DELETE/habits/:id route
# @app.delete("/habits/{id}") # soft delete aka update is_active flag to false
