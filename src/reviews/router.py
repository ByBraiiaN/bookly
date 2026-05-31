from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User
from src.db.main import get_session
from src.auth.dependencies import get_current_user
from .schemas import ReviewCreateModel
from .services import ReviewService

review_router = APIRouter()
review_service = ReviewService()

@review_router.post("/book/{book_uid}", status_code=201)
async def add_review_to_book(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        new_review = await review_service.create_review(   
            review_data=review_data,     
            book_uid=book_uid,    
            user_email=current_user.email,                        
            session=session
        )

        return new_review
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))