from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .schemas import UserCreateModel, UserModel, UserLoginModel, UserBooksModel, EmailModel, PasswordResetModel, PasswordResetConfirmModel
from .services import UserService
from .utils import create_access_token, decode_access_token, verify_password, create_url_safe_token, decode_url_safe_token, generate_password_hash
from datetime import timedelta, datetime
from .dependencies import AccessTokenBearer, RefreshTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.mail import mail, create_message
from src.config import settings
from src.errors import (
    UserAlreadyExists,
    UserNotFound,
    InvalidCredentials,
    InvalidToken
)


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(allowed_roles=["user", "admin"])

REFRESH_TOKEN_EXPIRY = timedelta(days=2)

@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    addresses = emails.addresses

    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"

    message = create_message(subject=subject, recipients=addresses, body=html)
    
    await mail.send_message(message)

    return {"message": "Email sent successfully"}

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):    
    user = await user_service.get_user_by_email(user_data.email, session)
    if user:
        raise UserAlreadyExists()
    
    new_user = await user_service.create_user(user_data, session)

    if not new_user:
        raise InvalidCredentials()
    
    token = create_url_safe_token({'email': user_data.email})
    link = f"https://{settings.DOMAIN_NAME}/api/v1/auth/verify_email/{token}"
    html_message = f"""
    <h1>Verify Your Email</h1>
    <p>Click the link below to verify your email address:</p>
    <a href="{link}">Verify Email</a>
    """
    message = create_message(subject="Verify Your Email", recipients=[user_data.email], body=html_message)
    await mail.send_message(message)

    return {
        "message": "Account created successfully! Check your email to verify your account.",
        "user": new_user
        }

@auth_router.get("/verify_email/{token}")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    try:
        token_data = decode_url_safe_token(token)
        email = token_data.get("email")
    except Exception:
        raise InvalidToken()
    
    user = await user_service.get_user_by_email(email, session)
    if not user:
        raise UserNotFound()
    
    if user.is_verified:
        return {"message": "Email already verified."}
    
    await user_service.update_user(user, {"is_verified": True}, session)
    
    return JSONResponse(content={"message": "Email verified successfully!"}, status_code=status.HTTP_200_OK)

@auth_router.post("/login")
async def login_user(credentials: UserLoginModel, session: AsyncSession = Depends(get_session)):
    user = await user_service.get_user_by_email(credentials.email, session)
    print(user)
    if not user: # or not user.is_verified
        raise UserNotFound()
    
    if not verify_password(credentials.password, user.password_hash):
        raise InvalidCredentials()
    
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
        raise InvalidToken()

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

@auth_router.post("/password-reset-request")
async def password_reset(request: PasswordResetModel):
    email = request.email
    
    token = create_url_safe_token({'email': email})
    link = f"http://{settings.DOMAIN_NAME}/api/v1/auth/password-reset/{token}"
    html_message = f"""
    <h1>Reset your password</h1>
    <p>Click the link below to reset your password:</p>
    <a href="{link}">Reset Password</a>
    """
    message = create_message(subject="Password Reset Request", recipients=[request.email], body=html_message)
    await mail.send_message(message)

    return JSONResponse(content={"message": "Password reset email sent successfully"}, status_code=status.HTTP_200_OK)

@auth_router.post("/password-reset/{token}")
async def password_reset_confirm(token: str, request: PasswordResetConfirmModel, session: AsyncSession = Depends(get_session)):
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")    

    try:
        token_data = decode_url_safe_token(token)
        email = token_data.get("email")
    except Exception:
        raise InvalidToken()
    
    user = await user_service.get_user_by_email(email, session)
    if not user:
        raise UserNotFound()
    
    new_password_hash = generate_password_hash(request.new_password)
    await user_service.update_user(user, {"password_hash": new_password_hash}, session)
    
    return JSONResponse(content={"message": "Password reset successfully!"}, status_code=status.HTTP_200_OK)