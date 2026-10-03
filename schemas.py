from pydantic import BaseModel, field_validator


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
