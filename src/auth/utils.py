import uuid
from passlib.context import CryptContext
from datetime import datetime, timedelta
from src.config import settings
import jwt
import logging
from itsdangerous import URLSafeTimedSerializer

password_context = CryptContext(schemes=["bcrypt"])

ACCESS_TOKEN_EXPIRY = 3600

def generate_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)

def create_access_token(user_data: dict, expires_delta: timedelta = None, refresh_token: bool = False) -> str:
    payload = {}

    payload['user'] = user_data
    payload['exp'] = datetime.utcnow() + (expires_delta or timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh_token

    token = jwt.encode(
        payload=payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.PyJWTError as e:
        logging.exception(f"JWT error: {str(e)}")
        return None

serializer = URLSafeTimedSerializer(
    settings.JWT_SECRET_KEY, salt="email-confirmation"
)

def create_url_safe_token(data: dict, expires_sec: int = 3600) -> str:
    return serializer.dumps(data)

def decode_url_safe_token(token: str, max_age: int = 3600) -> dict:
    try:
        data = serializer.loads(token)
        return data
    except Exception as e:
        logging.exception(f"Token decoding error: {str(e)}")
        return None