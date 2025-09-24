from handler import lambda_handler
import json
import time

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
        "rawQueryString": "",
        "headers": "",
        "queryStringParameters": "",
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
                "userAgent": ""
            },
            "requestId": "local-request-id",
            "stage": "local",
            "time": "01/Jan/2023:00:00:00 +0000",
            "timeEpoch": 1672531200000
        },
        "body": body,
        "isBase64Encoded": False
    }



def main():
    # Start timing
    start_time = time.time()
    print("Starting scraping operation...")
    
    event = create_lambda_event(
        method="POST",
        path="/scrape",
        query_params={},
        body=json.dumps({"key": "value"}),
        headers={"Content-Type": "application/json"}
    )
    context = MockLambdaContext()

    result = lambda_handler(event, context)
    
    # Calculate and print total time
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Scraping operation completed in {total_time:.2f} seconds")
    
    print(f"Total execution time: {total_time:.2f} seconds")
    print(result)


if __name__ == "__main__":
    main()
