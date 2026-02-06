"""Base exception classes."""

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for API errors."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(BaseAPIException):
    """Resource not found exception."""
    
    def __init__(self, resource: str):
        super().__init__(
            detail=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedException(BaseAPIException):
    """Unauthorized access exception."""
    
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class ForbiddenException(BaseAPIException):
    """Forbidden access exception."""
    
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN
        )
