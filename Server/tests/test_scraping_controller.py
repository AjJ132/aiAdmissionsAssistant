"""
Tests for scraping_controller.py - Scraping operations controller
"""
import pytest
import json
import aiohttp
from unittest.mock import AsyncMock, patch, mock_open
from src.controllers.scraping_controller import ScrapingController, ScrapingControllerFactory


class TestScrapingControllerFactory:
    """Test suite for ScrapingControllerFactory"""
    
    @pytest.mark.unit
    def test_create_scraping_controller(self, sample_scraping_config):
        """Test factory creates controller with proper dependencies"""
        config_json = json.dumps(sample_scraping_config)
        
        with patch('builtins.open', mock_open(read_data=config_json)), \
             patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            controller = ScrapingControllerFactory.createScrapingController()
            
            assert controller is not None
            assert isinstance(controller, ScrapingController)
            assert controller.config == sample_scraping_config
            assert controller.webRequestService is not None
            assert controller.scraping_utils is not None
    @pytest.mark.unit
    def test_create_scraping_controller_loads_config(self):
        """Test factory loads config from file"""
        test_config = {
            "grad_admissions_list_url": "https://test.com",
            "grad_admissions_list_xpath": "//ul"
        }
        config_json = json.dumps(test_config)
        
        with patch('builtins.open', mock_open(read_data=config_json)), \
             patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            controller = ScrapingControllerFactory.createScrapingController()
            
            assert controller.config["grad_admissions_list_url"] == "https://test.com"
            assert controller.config["grad_admissions_list_url"] == "https://test.com"


class TestScrapingController:
    """Test suite for ScrapingController"""
    
    @pytest.mark.asyncio
    async def test_obtain_degree_list_success(
        self, mock_web_request_service, mock_scraping_utils, 
        sample_scraping_config, sample_degree_list_html, sample_degree_data
    ):
        """Test successful degree list retrieval"""
        mock_web_request_service.fetchPage.return_value = sample_degree_list_html
        mock_scraping_utils.parse_degree_list.return_value = sample_degree_data
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=sample_scraping_config
        )
        
        degrees = await controller.obtainDegreeList()
        
        assert degrees == sample_degree_data
        assert len(degrees) == 3
        mock_web_request_service.fetchPage.assert_called_once_with(
            sample_scraping_config["grad_admissions_list_url"]
        )
        mock_scraping_utils.parse_degree_list.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_obtain_degree_list_no_url_in_config(
        self, mock_web_request_service, mock_scraping_utils
    ):
        """Test degree list retrieval with missing URL in config"""
        config = {"grad_admissions_list_xpath": "//ul"}
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=config
        )
        
        with pytest.raises(ValueError, match="Graduate admissions list URL not found"):
            await controller.obtainDegreeList()
    
    @pytest.mark.asyncio
    async def test_obtain_degree_list_no_xpath_in_config(
        self, mock_web_request_service, mock_scraping_utils
    ):
        """Test degree list retrieval with missing XPath in config"""
        config = {"grad_admissions_list_url": "https://example.com"}
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=config
        )
        
        with pytest.raises(ValueError, match="Graduate admissions list XPath not found"):
            await controller.obtainDegreeList()
    
    @pytest.mark.asyncio
    async def test_obtain_degree_list_empty_result(
        self, mock_web_request_service, mock_scraping_utils, sample_scraping_config
    ):
        """Test degree list retrieval with empty result"""
        mock_web_request_service.fetchPage.return_value = "<html></html>"
        mock_scraping_utils.parse_degree_list.return_value = []
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=sample_scraping_config
        )
        
        with pytest.raises(ValueError, match="No graduate degrees found"):
            await controller.obtainDegreeList()
    
    @pytest.mark.asyncio
    async def test_obtain_degree_list_fetch_error(
        self, mock_web_request_service, mock_scraping_utils, sample_scraping_config
    ):
        """Test degree list retrieval with fetch error"""
        mock_web_request_service.fetchPage.side_effect = Exception("Network error")
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=sample_scraping_config
        )
        
        with pytest.raises(Exception, match="Network error"):
            await controller.obtainDegreeList()
    
    @pytest.mark.asyncio
    async def test_scrape_degree_page_success(
        self, mock_web_request_service, mock_scraping_utils, 
        sample_scraping_config, sample_extracted_content
    ):
        """Test successful degree page scraping"""
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_web_request_service.fetchPage.return_value = "<html>Test HTML</html>"
        mock_scraping_utils.extract_main_content.return_value = sample_extracted_content
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=sample_scraping_config
        )
        
        result = await controller.scrapeDegreePage(
            "Computer Science", 
            "https://example.com/cs",
            mock_session
        )
        
        assert result['scraped_url'] == "https://example.com/cs"
        assert result['scraped_degree_name'] == "Computer Science"
        assert result['title'] == sample_extracted_content['title']
        mock_web_request_service.fetchPage.assert_called_once_with(
            "https://example.com/cs", mock_session
        )
    
    @pytest.mark.asyncio
    async def test_scrape_degree_page_no_content(
        self, mock_web_request_service, mock_scraping_utils, sample_scraping_config
    ):
        """Test degree page scraping with no content extracted"""
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_web_request_service.fetchPage.return_value = "<html></html>"
        mock_scraping_utils.extract_main_content.return_value = None
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=sample_scraping_config
        )
        
        with pytest.raises(ValueError, match="No information parsed"):
            await controller.scrapeDegreePage(
                "Computer Science",
                "https://example.com/cs",
                mock_session
            )
    
    @pytest.mark.asyncio
    async def test_scrape_degree_page_fetch_error(
        self, mock_web_request_service, mock_scraping_utils, sample_scraping_config
    ):
        """Test degree page scraping with fetch error"""
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_web_request_service.fetchPage.side_effect = Exception("Page not found")
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=sample_scraping_config
        )
        
        with pytest.raises(Exception, match="Page not found"):
            await controller.scrapeDegreePage(
                "Computer Science",
                "https://example.com/cs",
                mock_session
            )
    
    @pytest.mark.asyncio
    async def test_begin_scraping_operation_success(
        self, mock_web_request_service, mock_scraping_utils,
        sample_scraping_config, sample_degree_data, sample_extracted_content
    ):
        """Test complete scraping operation"""
        # Mock degree list retrieval
        mock_web_request_service.fetchPage.return_value = "<html>Test</html>"
        mock_scraping_utils.parse_degree_list.return_value = sample_degree_data
        mock_scraping_utils.extract_main_content.return_value = sample_extracted_content
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=sample_scraping_config
        )
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await controller.beginScrapingOperation()
            
            # Should have attempted to scrape all degrees
            
            # Should have attempted to scrape all degrees
            assert mock_scraping_utils.extract_main_content.call_count == len(sample_degree_data)
    
    @pytest.mark.asyncio
    async def test_begin_scraping_operation_no_degrees(
        self, mock_web_request_service, mock_scraping_utils, sample_scraping_config
    ):
        """Test scraping operation when no degrees obtained"""
        mock_web_request_service.fetchPage.return_value = "<html></html>"
        mock_scraping_utils.parse_degree_list.return_value = []
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=sample_scraping_config
        )
        
        # Should raise ValueError from obtainDegreeList
        with pytest.raises(ValueError, match="No graduate degrees found"):
            await controller.beginScrapingOperation()
    
    @pytest.mark.asyncio
    async def test_begin_scraping_operation_partial_failures(
        self, mock_web_request_service, mock_scraping_utils,
        sample_scraping_config, sample_degree_data, sample_extracted_content
    ):
        """Test scraping operation with some pages failing"""
        mock_scraping_utils.parse_degree_list.return_value = sample_degree_data
        
        # First call succeeds, second fails, third succeeds
        mock_web_request_service.fetchPage.side_effect = [
            "<html>List</html>",  # For degree list
            "<html>Page 1</html>",  # First degree page
            Exception("Network error"),  # Second degree page fails
            "<html>Page 3</html>",  # Third degree page
        ]
        
        mock_scraping_utils.extract_main_content.return_value = sample_extracted_content
        
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=sample_scraping_config
        )
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Should complete without raising exception
            await controller.beginScrapingOperation()
            
            # Should have attempted all three
            
            # Should have attempted all three
            assert mock_web_request_service.fetchPage.call_count == 4  # 1 list + 3 pages
    
    @pytest.mark.asyncio
    async def test_controller_initializes_with_empty_degree_list(
        self, mock_web_request_service, mock_scraping_utils, sample_scraping_config
    ):
        """Test controller initializes with empty obtained_degrees list"""
        controller = ScrapingController(
            webRequestService=mock_web_request_service,
            scraping_utils=mock_scraping_utils,
            config=sample_scraping_config
        )
        
        assert controller.obtained_degrees == []
        assert controller.config == sample_scraping_config
