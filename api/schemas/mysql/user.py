from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserCreate(BaseModel):  # Register
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    def validate_password(cls, pw):
        if len(pw) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        if not re.search(r"\d", pw):
            raise ValueError("Password must contain at least one digit.")

        if not re.search(r"[A-Z]", pw):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", pw):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not re.search(r"[\W_]", pw):
            raise ValueError("Password must contain at least one special character.")

        return pw


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True
