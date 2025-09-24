import aiohttp
import asyncio
from typing import Optional

class WebRequestService:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Max connections per host
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
        )
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def _ensure_session(self):
        """Ensure session is created"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; scraper)',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            )
    
    async def fetchPage(self, url: str) -> str:
        """Fetch a single page asynchronously"""
        await self._ensure_session()
        
        try:
            if self.session is None:
                raise Exception("Session not initialized")
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"Failed to fetch page: {url} with status code {response.status}")
        except asyncio.TimeoutError:
            raise Exception(f"Timeout while fetching page: {url}")
        except aiohttp.ClientError as e:
            raise Exception(f"Client error while fetching page {url}: {e}")
    
    async def close(self):
        """Manually close the session"""
        if self.session:
            await self.session.close()