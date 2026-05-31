from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .schemas import UserCreateModel, UserModel, UserLoginModel, UserBooksModel
from .services import UserService
from .utils import create_access_token, decode_access_token, verify_password
from datetime import timedelta, datetime
from .dependencies import AccessTokenBearer, RefreshTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(allowed_roles=["user", "admin"])

REFRESH_TOKEN_EXPIRY = timedelta(days=2)

@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):    
    user = await user_service.get_user_by_email(user_data.email, session)
    if user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with this email already exists")
    
    new_user = await user_service.create_user(user_data, session)

    if not new_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user account")
    
    return new_user

@auth_router.post("/login")
async def login_user(credentials: UserLoginModel, session: AsyncSession = Depends(get_session)):
    user = await user_service.get_user_by_email(credentials.email, session)
    print(user)
    if not user: # or not user.is_verified
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or account not verified")
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    access_token = create_access_token(
        user_data={"uid": str(user.uid), "email": user.email, "role": user.role},
    )
    refresh_token = create_access_token(
        user_data={"uid": str(user.uid), "email": user.email}, expires_delta=REFRESH_TOKEN_EXPIRY, refresh_token=True
    )
    
    return JSONResponse(
        content={
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "uid": str(user.uid),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }
    )

@auth_router.get("/refresh_token")
async def refresh_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details.get("exp")

    if datetime.utcfromtimestamp(expiry_timestamp) < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired")

    new_access_token = create_access_token(user_data=token_details.get("user"))
    
    return JSONResponse(
        content={
            "message": "Access token refreshed successfully",
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    )

@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user_profile(current_user: dict = Depends(get_current_user), _:bool = Depends(role_checker)):
    return current_user

@auth_router.get("/logout")
async def logout_user(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details.get("jti")
    await add_jti_to_blocklist(jti)
    
    return JSONResponse(content={"message": "Logoged out successfully"})