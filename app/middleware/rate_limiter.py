"""Rate limiting middleware."""

from fastapi import Request, HTTPException, status
from collections import defaultdict
from datetime import datetime, timedelta
from app.config.settings import get_settings


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.settings = get_settings()
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limit."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        if len(self.requests[client_id]) >= self.settings.RATE_LIMIT_PER_MINUTE:
            return False
        
        self.requests[client_id].append(now)
        return True


rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    client_id = request.client.host
    
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    response = await call_next(request)
    return response
