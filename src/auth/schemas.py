from pydantic import BaseModel, EmailStr, Field
import uuid
from src.books.schemas import Book
from src.reviews.schemas import ReviewModel
from typing import List
from datetime import datetime

class UserCreateModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=12)
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1, max_length=25)
    last_name: str = Field(..., min_length=1, max_length=25)

class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    is_verified: bool
    created_at: datetime
    update_at: datetime

class UserBooksModel(UserModel):
    books: List[Book]
    reviews: List[ReviewModel]

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class EmailModel(BaseModel):
    addresses: List[str]

class PasswordResetModel(BaseModel):
    email: EmailStr

class PasswordResetConfirmModel(BaseModel):
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)