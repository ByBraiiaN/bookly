from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker
from src.books.schemas import Book
from src.db.main import get_session

from .schemas import TagModel, TagAddModel, TagCreateModel
from .services import TagService
from src.errors import (
    TagNotFound,
    TagAlreadyExists,
    BookNotFound
)

tag_router = APIRouter()
tag_service = TagService()
role_checker = RoleChecker([''])

@tag_router.get("/", response_model=List[TagModel])
async def get_tags(session: AsyncSession = Depends(get_session)):
    tags = await tag_service.get_tags(session)
    return tags

@tag_router.post("/", response_model=TagModel, status_code=status.HTTP_201_CREATED)
async def add_tag(tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)) -> TagModel:
    new_tag = await tag_service.add_tag(tag_data, session)
    return new_tag

@tag_router.post("/book/{book_uid}/tags", response_model=Book)
async def add_tags_to_book(
    book_uid: str,
    tag_data: TagAddModel,
    session: AsyncSession = Depends(get_session)
) -> Book:
    updated_book = await tag_service.add_tags_to_book(book_uid, tag_data, session)
    if not updated_book:
        raise BookNotFound()
    
    return updated_book

@tag_router.put("/{tag_uid}", response_model=TagModel)
async def update_tag(
    tag_uid: str,
    tag_data: TagCreateModel,
    session: AsyncSession = Depends(get_session)
) -> TagModel:
    updated_tag = await tag_service.update_tag(tag_uid, tag_data, session)
    if not updated_tag:
        raise TagNotFound()
    
    return updated_tag

@tag_router.delete("/{tag_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_uid: str, session: AsyncSession = Depends(get_session)) -> None:
    updated_tag = await tag_service.delete_tag(tag_uid, session)
    if not updated_tag:
        raise TagNotFound()
