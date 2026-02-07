"""Alternative authentication using external auth service."""

from fastapi import Depends, Header, HTTPException, status
from typing import Optional
from app.infrastructure.security.jwt_handler import jwt_handler


async def get_current_user_from_service(authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency to verify user with external auth service.
    Use this instead of get_current_user if you want to call AUTH_SERVICE_URL.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    
    # Call external auth service
    payload = await jwt_handler.verify_token_with_service(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload
