from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from .schemas import BookCreateModel, BookUpdateModel
from src.db.models import Book
from datetime import datetime

class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book_by_id(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book or None
    
    async def get_books_by_user(self, user_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def create_book(self, book_data: BookCreateModel, user_uid: str, session: AsyncSession):
        book_data_dict = book_data.model_dump()        
        new_book = Book(**book_data_dict)
        new_book.published_date = datetime.strptime(book_data_dict["published_date"], "%Y-%m-%d")
        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()
        #await session.refresh(new_book)
        return new_book

    async def update_book(self, book_uid: str, book_data: BookUpdateModel, session: AsyncSession):
        updated_book = await self.get_book_by_id(book_uid, session)
        if not updated_book:
            return None
        
        update_data_dict = book_data.model_dump()
        for key, value in update_data_dict.items():
            setattr(updated_book, key, value)
        await session.commit()
        #await session.refresh(updated_book)
        return updated_book

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book_by_id(book_uid, session)
        if not book_to_delete:
            return None
        
        await session.delete(book_to_delete)
        await session.commit()
        return book_to_delete
        