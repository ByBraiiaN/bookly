from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .schemas import Book, BookUpdateModel, BookCreateModel
from .services import BookService
from src.auth.dependencies import AccessTokenBearer, RoleChecker

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(allowed_roles=["user", "admin"]))

@book_router.get("/", response_model=list[Book])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)
):
    books = await book_service.get_all_books(session)
    return books

@book_router.get("/user/{user_uid}", response_model=list[Book])
async def get_user_books(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)
):
    books = await book_service.get_books_by_user(user_uid, session)
    return books

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book, dependencies=[role_checker])
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)
) -> Book:
    user_id = token_details.get("user").get("uid")
    book = await book_service.create_book(book_data, user_id, session)
    return book

@book_router.get("/{book_uid}", response_model=Book, dependencies=[role_checker])
async def get_book_by_id(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)
) -> Book:
    book = await book_service.get_book_by_id(book_uid, session)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@book_router.patch("/{book_uid}", status_code=status.HTTP_200_OK, response_model=Book, dependencies=[role_checker])
async def update_book(
    book_uid: str,
    book_update: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)
) -> Book:
    book = await book_service.update_book(book_uid, book_update, session)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)
) -> None:
    book = await book_service.delete_book(book_uid, session)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
