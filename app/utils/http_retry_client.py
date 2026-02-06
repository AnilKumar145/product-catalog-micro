"""Reusable async HTTP client with timeout and retry logic."""

import httpx
import asyncio
import logging
from typing import Optional, Dict, Any
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class HTTPClientWithRetry:
    """HTTP client with automatic retry and timeout handling."""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def request(
        self,
        method: str,
        url: str,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> httpx.Response:
        """
        Make HTTP request with retry logic and timeout.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            json: JSON payload
            headers: Request headers
            timeout: Timeout in seconds (default: EXTERNAL_API_TIMEOUT)
            max_retries: Max retry attempts (default: EXTERNAL_API_MAX_RETRIES)
        
        Returns:
            httpx.Response object
        
        Raises:
            httpx.HTTPError: After all retries exhausted
        """
        timeout = timeout or self.settings.EXTERNAL_API_TIMEOUT
        max_retries = max_retries or self.settings.EXTERNAL_API_MAX_RETRIES
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        json=json,
                        headers=headers
                    )
                    return response
            
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 0.5 * (attempt + 1)
                    logger.warning(f"Request timeout to {url}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
            
            except httpx.RequestError as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 0.5 * (attempt + 1)
                    logger.warning(f"Request error to {url}: {e}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
        
        raise last_error
    
    async def get(self, url: str, headers: Optional[Dict] = None, **kwargs) -> httpx.Response:
        """GET request with retry."""
        return await self.request("GET", url, headers=headers, **kwargs)
    
    async def post(self, url: str, json: Dict, headers: Optional[Dict] = None, **kwargs) -> httpx.Response:
        """POST request with retry."""
        return await self.request("POST", url, json=json, headers=headers, **kwargs)
    
    async def put(self, url: str, json: Dict, headers: Optional[Dict] = None, **kwargs) -> httpx.Response:
        """PUT request with retry."""
        return await self.request("PUT", url, json=json, headers=headers, **kwargs)
    
    async def patch(self, url: str, json: Dict, headers: Optional[Dict] = None, **kwargs) -> httpx.Response:
        """PATCH request with retry."""
        return await self.request("PATCH", url, json=json, headers=headers, **kwargs)
    
    async def delete(self, url: str, headers: Optional[Dict] = None, **kwargs) -> httpx.Response:
        """DELETE request with retry."""
        return await self.request("DELETE", url, headers=headers, **kwargs)


http_client = HTTPClientWithRetry()
