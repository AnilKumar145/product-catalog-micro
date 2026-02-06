"""Audit logging middleware."""

from fastapi import Request
from app.infrastructure.logging.audit_logger import audit_logger


async def audit_middleware(request: Request, call_next):
    """Middleware to log all API requests for audit purposes."""
    user_id = None
    
    if hasattr(request.state, "user"):
        user_id = request.state.user.get("user_id")
    
    response = await call_next(request)
    
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        audit_logger.log(
            user_id=user_id,
            action=request.method,
            resource=request.url.path,
            details={
                "status_code": response.status_code,
                "client": request.client.host
            }
        )
    
    return response
