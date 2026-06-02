from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.db.models import User
from .schemas import UserCreateModel
from .utils import generate_password_hash

class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user or None

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(user_data_dict["password"])
        new_user.role = "user"
        print("usuario creado:")
        print(new_user)

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for key, value in user_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)
        return user