from fastapi import APIRouter, HTTPException, status
from src.books.book_data import books
from src.books.schemas import Book, BookUpdate

book_router = APIRouter()

@book_router.get("/", response_model=list[Book])
async def get_all_books():
    return books

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(book: Book) -> Book:
    books.append(book.model_dump()) #.model_dump() is optional, python can convert the pydantic model to dict automatically
    return book

@book_router.get("/{book_id}", response_model=Book)
async def get_book_by_id(book_id: int) -> Book:
    for book in books:
        if book["id"] == book_id:
            return book
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.patch("/{book_id}", response_model=Book)
async def update_book(book_id: int, book_update: BookUpdate) -> Book:
    for book in books:
        if book["id"] == book_id:
            book["title"] = book_update.title
            book["author"] = book_update.author
            book["publisher"] = book_update.publisher
            book["page_count"] = book_update.page_count
            book["language"] = book_update.language
            return book
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return {}
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
