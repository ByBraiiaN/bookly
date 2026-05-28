from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.books.router import book_router
from src.auth.router import auth_router
from src.db.main import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):    
    print("Starting up...")
    #await init_db() # Disabled automatic database initialization, Alembic will handle this instead
    yield
    # Perform any shutdown tasks here (e.g., disconnect from the database)
    print("Shutting down...")

version = "v1"

app = FastAPI(
    title="Bookly API",
    description="A simple API for managing books",
    version=version,
    lifespan=lifespan
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])