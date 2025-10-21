import aiohttp
import asyncio
from typing import Optional
from bs4 import BeautifulSoup

class WebRequestService:
    
    async def fetchPage(self, url: str, session: Optional[aiohttp.ClientSession] = None) -> str:
        """
        Asynchronously fetch a page from a URL.
        If a session is provided, use it. Otherwise, create a new session.
        """
        should_close = False
        if session is None:
            session = aiohttp.ClientSession()
            should_close = True
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"Failed to fetch page: {url} with status code {response.status}")
        finally:
            if should_close:
                await session.close()


        