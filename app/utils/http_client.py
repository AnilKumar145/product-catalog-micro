"""Async HTTP client using httpx."""

import httpx
from typing import Optional, Dict, Any
from app.config.settings import get_settings


class AsyncHTTPClient:
    """Async HTTP client for external API calls."""
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.settings = get_settings()
    
    async def __aenter__(self):
        """Context manager entry."""
        self.client = httpx.AsyncClient(timeout=10.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def get(self, url: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Async GET request."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def post(self, url: str, json: Dict, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Async POST request."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def verify_token_with_auth_service(self, token: str) -> Optional[Dict]:
        """Verify JWT token with external auth service."""
        try:
            url = f"{self.settings.AUTH_SERVICE_URL}/verify"
            headers = {"Authorization": f"Bearer {token}"}
            return await self.get(url, headers=headers)
        except httpx.HTTPError:
            return None


http_client = AsyncHTTPClient()
