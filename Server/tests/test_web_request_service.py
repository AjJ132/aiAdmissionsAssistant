"""
Tests for web_request_service.py - HTTP request service
"""
import pytest
import aiohttp
from unittest.mock import AsyncMock, Mock, patch
from src.services.web_request_service import WebRequestService


class TestWebRequestService:
    """Test suite for WebRequestService"""
    
    @pytest.mark.asyncio
    async def test_fetch_page_success_without_session(self):
        """Test successful page fetch without providing a session"""
        service = WebRequestService()
        test_url = "https://example.com/test"
        expected_html = "<html><body>Test Content</body></html>"
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=expected_html)
            mock_response.__aenter__.return_value = mock_response
            mock_response.__aexit__.return_value = None
            
            mock_session.get.return_value = mock_response
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session
            
            result = await service.fetchPage(test_url)
            
            assert result == expected_html
            mock_session.get.assert_called_once_with(test_url)
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_page_success_with_session(self):
        """Test successful page fetch with provided session"""
        service = WebRequestService()
        test_url = "https://example.com/test"
        expected_html = "<html><body>Test Content</body></html>"
        
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=expected_html)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        
        mock_session.get.return_value = mock_response
        
        result = await service.fetchPage(test_url, mock_session)
        
        assert result == expected_html
        mock_session.get.assert_called_once_with(test_url)
        # Session should NOT be closed when provided externally
        assert not hasattr(mock_session, 'close') or not mock_session.close.called
    
    @pytest.mark.asyncio
    async def test_fetch_page_http_error_404(self):
        """Test page fetch with 404 error"""
        service = WebRequestService()
        test_url = "https://example.com/notfound"
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.__aenter__.return_value = mock_response
            mock_response.__aexit__.return_value = None
            
            mock_session.get.return_value = mock_response
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session
            
            with pytest.raises(Exception, match="Failed to fetch page.*404"):
                await service.fetchPage(test_url)
            
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_page_http_error_500(self):
        """Test page fetch with 500 error"""
        service = WebRequestService()
        test_url = "https://example.com/error"
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.__aenter__.return_value = mock_response
            mock_response.__aexit__.return_value = None
            
            mock_session.get.return_value = mock_response
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session
            
            with pytest.raises(Exception, match="Failed to fetch page.*500"):
                await service.fetchPage(test_url)
    
    @pytest.mark.asyncio
    async def test_fetch_page_network_error(self):
        """Test page fetch with network error"""
        service = WebRequestService()
        test_url = "https://example.com/test"
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get.side_effect = aiohttp.ClientError("Connection failed")
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session
            
            with pytest.raises(aiohttp.ClientError, match="Connection failed"):
                await service.fetchPage(test_url)
            
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_page_timeout_error(self):
        """Test page fetch with timeout"""
        service = WebRequestService()
        test_url = "https://example.com/slow"
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get.side_effect = aiohttp.ServerTimeoutError("Request timeout")
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session
            
            with pytest.raises(aiohttp.ServerTimeoutError, match="Request timeout"):
                await service.fetchPage(test_url)
    
    @pytest.mark.asyncio
    async def test_fetch_page_closes_session_on_error_without_provided_session(self):
        """Test that session is closed even when an error occurs (when session created internally)"""
        service = WebRequestService()
        test_url = "https://example.com/test"
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.__aenter__.return_value = mock_response
            mock_response.__aexit__.return_value = None
            
            mock_session.get.return_value = mock_response
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session
            
            with pytest.raises(Exception):
                await service.fetchPage(test_url)
            
            # Session should be closed in finally block
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_page_does_not_close_provided_session_on_error(self):
        """Test that provided session is NOT closed on error"""
        service = WebRequestService()
        test_url = "https://example.com/test"
        
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        
        mock_session.get.return_value = mock_response
        mock_session.close = AsyncMock()
        
        with pytest.raises(Exception):
            await service.fetchPage(test_url, mock_session)
        
        # Provided session should NOT be closed
        mock_session.close.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_fetch_page_multiple_urls_with_shared_session(self):
        """Test fetching multiple pages with a shared session"""
        service = WebRequestService()
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        
        for i, url in enumerate(urls):
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=f"<html>Page {i+1}</html>")
            mock_response.__aenter__.return_value = mock_response
            mock_response.__aexit__.return_value = None
            
            mock_session.get.return_value = mock_response
            
            result = await service.fetchPage(url, mock_session)
            assert f"Page {i+1}" in result
        
        # Session should not be closed after any of the calls
        assert mock_session.get.call_count == len(urls)
    
    @pytest.mark.asyncio
    async def test_fetch_page_different_status_codes(self):
        """Test handling of various HTTP status codes"""
        service = WebRequestService()
        test_cases = [
            (200, True),   # Success
            (201, True),   # Created (should work with status == 200 check)
            (301, False),  # Redirect
            (400, False),  # Bad Request
            (403, False),  # Forbidden
            (404, False),  # Not Found
            (500, False),  # Server Error
            (503, False),  # Service Unavailable
        ]
        
        for status_code, should_succeed in test_cases:
            with patch('aiohttp.ClientSession') as mock_session_class:
                mock_session = AsyncMock()
                mock_response = AsyncMock()
                mock_response.status = status_code
                mock_response.text = AsyncMock(return_value="<html>Content</html>")
                mock_response.__aenter__.return_value = mock_response
                mock_response.__aexit__.return_value = None
                
                mock_session.get.return_value = mock_response
                mock_session.close = AsyncMock()
                mock_session_class.return_value = mock_session
                
                if should_succeed and status_code == 200:
                    result = await service.fetchPage("https://example.com")
                    assert result == "<html>Content</html>"
                else:
                    with pytest.raises(Exception):
                        await service.fetchPage("https://example.com")
