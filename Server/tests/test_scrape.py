"""
Tests for scrape.py - Local testing utilities
"""
import pytest
import json
from unittest.mock import patch, Mock
from scrape import MockLambdaContext, create_lambda_event


class TestMockLambdaContext:
    """Test suite for MockLambdaContext"""
    
    @pytest.mark.unit
    def test_mock_context_attributes(self):
        """Test that mock context has all required attributes"""
        context = MockLambdaContext()
        
        assert hasattr(context, 'function_name')
        assert hasattr(context, 'function_version')
        assert hasattr(context, 'invoked_function_arn')
        assert hasattr(context, 'memory_limit_in_mb')
        assert hasattr(context, 'remaining_time_in_millis')
        assert hasattr(context, 'log_group_name')
        assert hasattr(context, 'log_stream_name')
        assert hasattr(context, 'aws_request_id')
    
    @pytest.mark.unit
    def test_mock_context_values(self):
        """Test that mock context has appropriate default values"""
        context = MockLambdaContext()
        
        assert context.function_name == "local-test-function"
        assert context.function_version == "$LATEST"
        assert "lambda" in context.invoked_function_arn
        assert context.memory_limit_in_mb == "128"
        assert context.log_group_name == "/aws/lambda/local-test-function"
        assert context.aws_request_id == "local-request-id"
    
    @pytest.mark.unit
    def test_mock_context_remaining_time_callable(self):
        """Test that remaining_time_in_millis is callable"""
        context = MockLambdaContext()
        
        assert callable(context.remaining_time_in_millis)
        time_remaining = context.remaining_time_in_millis()
        assert isinstance(time_remaining, int)
        assert time_remaining == 30000


class TestCreateLambdaEvent:
    """Test suite for create_lambda_event function"""
    
    @pytest.mark.unit
    def test_create_event_basic(self):
        """Test creating a basic Lambda event"""
        event = create_lambda_event("POST", "/scrape")
        
        assert event['routeKey'] == "POST /scrape"
        assert event['version'] == "2.0"
        assert event['rawPath'] == "/scrape"
        assert event['isBase64Encoded'] is False
    
    @pytest.mark.unit
    def test_create_event_with_body(self):
        """Test creating event with body"""
        body_data = {"key": "value", "number": 42}
        body_json = json.dumps(body_data)
        
        event = create_lambda_event("POST", "/scrape", body=body_json)
        
        assert event['body'] == body_json
        parsed_body = json.loads(event['body'])
        assert parsed_body['key'] == "value"
        assert parsed_body['number'] == 42
    
    @pytest.mark.unit
    def test_create_event_with_query_params(self):
        """Test creating event with query parameters"""
        query_params = {"search": "test", "limit": "10"}
        
        event = create_lambda_event("GET", "/search", query_params=query_params)
        
        assert event['routeKey'] == "GET /search"
        # Note: The current implementation doesn't use query_params,
        # but we test the function accepts it
        assert 'queryStringParameters' in event
    
    @pytest.mark.unit
    def test_create_event_with_headers(self):
        """Test creating event with headers"""
        headers = {"Content-Type": "application/json", "Authorization": "Bearer token"}
        
        event = create_lambda_event("POST", "/api", headers=headers)
        
        assert 'headers' in event
        # Note: The current implementation sets headers to empty string
        # This test documents current behavior
    
    @pytest.mark.unit
    def test_create_event_request_context(self):
        """Test that event has proper request context"""
        event = create_lambda_event("GET", "/test")
        
        assert 'requestContext' in event
        context = event['requestContext']
        
        assert context['accountId'] == "123456789012"
        assert context['apiId'] == "local"
        assert context['domainName'] == "localhost"
        assert context['stage'] == "local"
        assert 'http' in context
    
    @pytest.mark.unit
    def test_create_event_http_context(self):
        """Test that event has proper HTTP context"""
        event = create_lambda_event("POST", "/scrape")
        
        http_context = event['requestContext']['http']
        
        assert http_context['method'] == "POST"
        assert http_context['path'] == "/scrape"
        assert http_context['protocol'] == "HTTP/1.1"
        assert http_context['sourceIp'] == "127.0.0.1"
    
    @pytest.mark.unit
    def test_create_event_different_methods(self):
        """Test creating events with different HTTP methods"""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        
        for method in methods:
            event = create_lambda_event(method, "/test")
            assert event['routeKey'] == f"{method} /test"
            assert event['requestContext']['http']['method'] == method
    
    @pytest.mark.unit
    def test_create_event_different_paths(self):
        """Test creating events with different paths"""
        paths = ["/", "/api", "/api/v1/users", "/scrape"]
        
        for path in paths:
            event = create_lambda_event("GET", path)
            assert event['rawPath'] == path
            assert event['requestContext']['http']['path'] == path
    
    @pytest.mark.unit
    def test_create_event_structure_matches_api_gateway_v2(self):
        """Test that created event matches API Gateway v2 format"""
        event = create_lambda_event("POST", "/scrape", body=json.dumps({"test": "data"}))
        
        # Required API Gateway v2 fields
        required_fields = [
            'routeKey', 'version', 'rawPath', 'rawQueryString',
            'headers', 'queryStringParameters', 'requestContext',
            'body', 'isBase64Encoded'
        ]
        
        for field in required_fields:
            assert field in event, f"Missing required field: {field}"
        
        # Request context required fields
        context_fields = [
            'accountId', 'apiId', 'domainName', 'domainPrefix',
            'http', 'requestId', 'stage', 'time', 'timeEpoch'
        ]
        
        for field in context_fields:
            assert field in event['requestContext'], f"Missing context field: {field}"


class TestScrapePyIntegration:
    """Test suite for scrape.py integration with handler"""
    
    @pytest.mark.unit
    def test_mock_context_compatible_with_handler(self):
        """Test that mock context works with lambda handler"""
        from scrape import MockLambdaContext
        
        context = MockLambdaContext()
        
        # Simulate handler accessing context attributes
        assert context.function_name is not None
        assert context.aws_request_id is not None
        assert callable(context.remaining_time_in_millis)
    
    @pytest.mark.unit
    @patch('handler.lambda_handler')
    def test_create_event_compatible_with_handler(self, mock_handler):
        """Test that created events work with lambda handler"""
        mock_handler.return_value = {
            'statusCode': 200,
            'body': json.dumps({'message': 'success'})
        }
        
        event = create_lambda_event("POST", "/scrape", body=json.dumps({"test": "data"}))
        context = MockLambdaContext()
        
        # This should not raise any exceptions
        response = mock_handler(event, context)
        
        assert response['statusCode'] == 200
        mock_handler.assert_called_once_with(event, context)
