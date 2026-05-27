from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel import text, SQLModel
from src.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=True,
    connect_args={"ssl": True}
)

async def init_db():
    async with engine.begin() as conn:
        from src.books.models import Book
        await conn.run_sync(SQLModel.metadata.create_all)