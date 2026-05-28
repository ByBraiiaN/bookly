from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel import text, SQLModel
from src.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    connect_args={"ssl": True}
)

async def init_db():
    async with engine.begin() as conn:
        from src.books.models import Book
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    Session = sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with Session() as session:
        yield session