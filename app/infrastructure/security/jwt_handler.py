"""JWT token handling for authentication."""

from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config.settings import get_settings
import httpx


class JWTHandler:
    """JWT token handler."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def decode_token(self, token: str) -> dict:
        """Decode and verify JWT token locally."""
        try:
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    async def verify_token_with_service(self, token: str) -> Optional[dict]:
        """Verify token with external auth service."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.settings.AUTH_SERVICE_URL}/verify",
                    json={"token": token}
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify token locally (current implementation)."""
        try:
            return self.decode_token(token)
        except ValueError:
            return None


jwt_handler = JWTHandler()
