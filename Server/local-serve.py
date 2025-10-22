import json
import os
import asyncio
from flask import Flask, request, jsonify
from handler import lambda_handler

app = Flask(__name__)

class MockLambdaContext:
    """Mock Lambda context for local testing"""
    def __init__(self):
        self.function_name = "local-test-function"
        self.function_version = "$LATEST"
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:local-test-function"
        self.memory_limit_in_mb = "128"
        self.remaining_time_in_millis = lambda: 30000
        self.log_group_name = "/aws/lambda/local-test-function"
        self.log_stream_name = "2023/01/01/[$LATEST]abcdefg"
        self.aws_request_id = "local-request-id"

def create_lambda_event(method, path, query_params=None, body=None, headers=None):
    """Create a Lambda event from Flask request"""
    return {
        "routeKey": f"{method} {path}",
        "version": "2.0",
        "rawPath": path,
        "rawQueryString": request.query_string.decode() if request.query_string else "",
        "headers": dict(request.headers) if headers is None else headers,
        "queryStringParameters": query_params or dict(request.args),
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "local",
            "domainName": "localhost",
            "domainPrefix": "local",
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": request.headers.get("User-Agent", "")
            },
            "requestId": "local-request-id",
            "stage": "local",
            "time": "01/Jan/2023:00:00:00 +0000",
            "timeEpoch": 1672531200000
        },
        "body": body,
        "isBase64Encoded": False
    }


@app.route('/scrape', methods=['POST'])
def scrape():
    """Handle scrape endpoint"""
    try:
        # Get request body
        body = None
        if request.is_json:
            body = json.dumps(request.get_json())
        elif request.data:
            body = request.data.decode('utf-8')
        
        # Create Lambda event
        event = create_lambda_event(
            method="POST",
            path="/scrape",
            query_params=dict(request.args),
            body=body,
            headers=dict(request.headers)
        )
        
        # Create mock context
        context = MockLambdaContext()
        
        # Call the Lambda handler (async)
        response = asyncio.run(lambda_handler(event, context))
        
        # Extract status code and body
        status_code = response.get('statusCode', 200)
        response_body = response.get('body', '{}')
        
        # Parse response body if it's a JSON string
        try:
            parsed_body = json.loads(response_body)
            return jsonify(parsed_body), status_code
        except (json.JSONDecodeError, TypeError):
            return response_body, status_code
            
    except Exception as e:
        print(f"Error in scrape endpoint: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat/LLM endpoint"""
    try:
        # Get request body
        body = None
        if request.is_json:
            body = json.dumps(request.get_json())
        elif request.data:
            body = request.data.decode('utf-8')
        
        # Create Lambda event
        event = create_lambda_event(
            method="POST",
            path="/chat",
            query_params=dict(request.args),
            body=body,
            headers=dict(request.headers)
        )
        
        # Create mock context
        context = MockLambdaContext()
        
        # Call the Lambda handler (async)
        response = asyncio.run(lambda_handler(event, context))
        
        # Extract status code and body
        status_code = response.get('statusCode', 200)
        response_body = response.get('body', '{}')
        
        # Parse response body if it's a JSON string
        try:
            parsed_body = json.loads(response_body)
            return jsonify(parsed_body), status_code
        except (json.JSONDecodeError, TypeError):
            return response_body, status_code
            
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
