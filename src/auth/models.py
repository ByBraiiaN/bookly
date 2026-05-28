from sqlmodel import SQLModel, Field, Column, Relationship
import uuid
from typing import List
from src.books import models as book_models
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column = Column(
            pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4
        )
    )
    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    role: str = Field(
        sa_column = Column(pg.VARCHAR(20), default="user", nullable=False)
    )
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List[book_models.Book] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    
def __repr__(self):
    return f"<User {self.username} ({self.email})>"