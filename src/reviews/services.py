from fastapi import HTTPException
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from src.db.models import Review
from src.auth.services import UserService
from src.books.services import BookService
from .schemas import ReviewCreateModel

book_service = BookService()
user_service = UserService()

class ReviewService:
    async def get_reviews_by_book(self, book_uid: str, session: AsyncSession):
        statement = select(Review).where(Review.book_uid == book_uid)
        result = await session.exec(statement)
        return result.all()

    async def create_review(self, review_data: ReviewCreateModel, book_uid: str, user_email: str, session: AsyncSession):
        try:
            book = await book_service.get_book_by_id(book_uid, session)
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            user = await user_service.get_user_by_email(user_email, session)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")


            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict)
            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()
            #await session.refresh(new_review)
            return new_review

        except Exception as e:
            print(f"Error creating review: {e}")
            logging.error(f"Error creating review: {e}")
            raise HTTPException(status_code=500, detail="Error creating review")

        

        