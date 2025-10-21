"""
Tests for handler.py - Lambda function handler
"""
import pytest
import json
from unittest.mock import patch, Mock, AsyncMock
from handler import lambda_handler


class TestLambdaHandler:
    """Test suite for the Lambda handler function"""
    
    @pytest.mark.unit
    def test_handler_scrape_route_success(self, sample_lambda_event, mock_lambda_context):
        """Test successful scraping route handling"""
        with patch('handler.ScrapingControllerFactory') as mock_factory, \
             patch('handler.asyncio.run') as mock_asyncio_run:
            
            # Setup mocks
            mock_controller = Mock()
            mock_controller.beginScrapingOperation = AsyncMock(return_value="Scraping completed successfully")
            mock_factory.createScrapingController.return_value = mock_controller
            mock_asyncio_run.return_value = "Scraping completed successfully"
            
            # Execute
            response = lambda_handler(sample_lambda_event, mock_lambda_context)
            
            # Assert
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['message'] == "Scraping completed successfully"
            mock_factory.createScrapingController.assert_called_once()
    
    @pytest.mark.unit
    def test_handler_invalid_route(self, mock_lambda_context):
        """Test handler with invalid route"""
        event = {
            "routeKey": "GET /invalid",
            "version": "2.0",
            "rawPath": "/invalid"
        }
        
        response = lambda_handler(event, mock_lambda_context)
        
        assert response['statusCode'] == 404
        assert 'Route not found' in response['body']
    
    @pytest.mark.unit
    def test_handler_missing_route_key(self, mock_lambda_context):
        """Test handler with missing routeKey"""
        event = {
            "version": "2.0",
            "rawPath": "/scrape"
        }
        
        response = lambda_handler(event, mock_lambda_context)
        
        assert response['statusCode'] == 404
    
    @pytest.mark.unit
    def test_handler_exception_handling(self, sample_lambda_event, mock_lambda_context):
        """Test handler exception handling"""
        with patch('handler.ScrapingControllerFactory') as mock_factory:
            mock_factory.createScrapingController.side_effect = Exception("Test error")
            
            response = lambda_handler(sample_lambda_event, mock_lambda_context)
            
            assert response['statusCode'] == 500
            assert 'Internal Server Error' in response['body']
    
    @pytest.mark.unit
    def test_handler_scraping_controller_exception(self, sample_lambda_event, mock_lambda_context):
        """Test handler when scraping controller raises exception"""
        with patch('handler.ScrapingControllerFactory') as mock_factory, \
             patch('handler.asyncio.run') as mock_asyncio_run:
            
            mock_controller = Mock()
            mock_factory.createScrapingController.return_value = mock_controller
            mock_asyncio_run.side_effect = ValueError("Scraping failed")
            
            response = lambda_handler(sample_lambda_event, mock_lambda_context)
            
            assert response['statusCode'] == 500
    
    @pytest.mark.unit
    def test_handler_empty_event(self, mock_lambda_context):
        """Test handler with empty event"""
        event = {}
        
        response = lambda_handler(event, mock_lambda_context)
        
        assert response['statusCode'] == 404
    
    @pytest.mark.unit
    def test_handler_different_http_methods(self, mock_lambda_context):
        """Test handler with different HTTP methods on scrape endpoint"""
        methods = ["GET", "PUT", "DELETE", "PATCH"]
        
        for method in methods:
            event = {
                "routeKey": f"{method} /scrape",
                "version": "2.0"
            }
            
            response = lambda_handler(event, mock_lambda_context)
            
            # Should return 404 as only POST /scrape is valid
            assert response['statusCode'] == 404


class TestLambdaEventStructure:
    """Test suite for Lambda event structure validation"""
    
    @pytest.mark.unit
    def test_valid_event_structure(self, sample_lambda_event):
        """Test that sample event has required structure"""
        assert "routeKey" in sample_lambda_event
        assert "version" in sample_lambda_event
        assert "requestContext" in sample_lambda_event
        assert sample_lambda_event["version"] == "2.0"
    
    @pytest.mark.unit
    def test_event_with_body(self, sample_lambda_event):
        """Test event body parsing"""
        assert "body" in sample_lambda_event
        body = json.loads(sample_lambda_event["body"])
        assert isinstance(body, dict)
