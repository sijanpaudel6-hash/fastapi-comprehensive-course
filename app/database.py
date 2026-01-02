from sqlmodel import Field, Session, SQLModel, create_engine
from .config import settings
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLModel_DATABASE_URL = f'postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
SQLModel_DATABASE_URL = DATABASE_URL

engine = create_engine(SQLModel_DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session