"""Global error handling middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.infrastructure.logging.error_logger import error_logger
from app.exceptions.base import BaseAPIException


async def error_handler_middleware(request: Request, call_next):
    """Global error handler middleware."""
    try:
        response = await call_next(request)
        return response
    except BaseAPIException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    except Exception as e:
        error_logger.log_error(e, {"path": request.url.path, "method": request.method})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )
