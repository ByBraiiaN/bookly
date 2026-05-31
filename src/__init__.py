from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.books.router import book_router
from src.auth.router import auth_router
from src.reviews.router import review_router
from src.tags.router import tag_router
from src.db.main import init_db
from .errors import register_all_errors

@asynccontextmanager
async def lifespan(app: FastAPI):    
    print("Starting up...")
    from src.db.models import User, Book
    
    await init_db() # Disabled automatic database initialization, Alembic will handle this instead
    yield
    # Perform any shutdown tasks here (e.g., disconnect from the database)
    print("Shutting down...")

version = "v1"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
"""

version_prefix =f"/api/{version}"

app = FastAPI(
    title="Bookly API",
    description="A simple API for managing books",
    version=version,
    #,lifespan=lifespan
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Braian",
        "url": "",
        "email": "",
    },
    terms_of_service="httpS://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

register_all_errors(app)

app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])
app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"{version_prefix}/reviews", tags=["reviews"])
app.include_router(tag_router, prefix=f"{version_prefix}/tags", tags=["tags"])