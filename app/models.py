from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import Column, DateTime, func, Boolean, text
from pydantic import EmailStr

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False)
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
    posts: list["Post"] = Relationship(back_populates="owner")

class BaseModel(SQLModel):
    title: str
    content: str
    published: bool = Field(
    default=True,
    sa_column=Column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
)

class Post(BaseModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
 
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
    owner_id: int = Field(foreign_key="user.id", ondelete="CASCADE", nullable=False)

    owner: User = Relationship(back_populates="posts")

class PostCreate(BaseModel):
    pass

class PostUpdate(SQLModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None

class PostPublic(BaseModel):
    id: int
    created_at: datetime
    owner_id: int




class UserCreate(SQLModel):
    email: EmailStr
    password: str

class UserPublic(SQLModel):
    id: int
    email: EmailStr
    created_at: datetime


class UserPublicWithPosts(UserPublic):
    posts: list[PostPublic] = []

class PostWithOwner(PostPublic):
    owner: UserPublic | None = None

class PostWithVotes(SQLModel):
    post: PostPublic
    votes: int

class PostWithOwnerVotes(SQLModel):
    post: PostWithOwner
    votes: int



class Vote(SQLModel, table=True):
    post_id: int = Field(foreign_key="post.id", primary_key=True, ondelete="CASCADE")
    user_id: int = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")