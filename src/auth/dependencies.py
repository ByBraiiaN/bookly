from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_access_token
from src.db.redis import is_jti_in_blocklist


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        creds = await super().__call__(request)

        if not creds:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )

        token = creds.credentials

        token_data = decode_access_token(token)

        if not self.verify_token(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token"
            )
        
        if await is_jti_in_blocklist(token_data.get("jti")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token has been revoked"
            )

        self.verify_token_data(token_data)

        return token_data

    def verify_token(self, token: str) -> bool:
        payload = decode_access_token(token)

        return bool(payload and "user" in payload)

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Subclasses must implement this method to verify token data")

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh tokens cannot be used for authentication"
            )
        
class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access tokens cannot be used for refreshing"
            )