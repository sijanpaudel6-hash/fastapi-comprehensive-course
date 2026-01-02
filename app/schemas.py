from sqlmodel import SQLModel
from pydantic import EmailStr
from typing import Literal

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    id: int | None = None

class Vote(SQLModel):
    post_id: int
    dir: Literal[0, 1]