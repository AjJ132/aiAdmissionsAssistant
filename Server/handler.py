import json
import asyncio

from typing import Dict, Any

from aws_lambda_powertools import Logger
from src.util.rate_limiter import chat_rate_limiter, scrape_rate_limiter

logger = Logger()

def get_client_identifier(event: dict) -> str:
    """
    Extract a unique identifier for the client from the event.
    Uses IP address as the primary identifier.
    
    Args:
        event: Lambda event dict
        
    Returns:
        Client identifier string
    """
    # Try to get the real IP from headers (in case of proxy)
    request_context = event.get('requestContext', {})
    http_context = request_context.get('http', {})
    
    # Get source IP from request context
    source_ip = http_context.get('sourceIp', 'unknown')
    
    # Fallback to X-Forwarded-For header if available
    headers = event.get('headers', {})
    forwarded_for = headers.get('x-forwarded-for', headers.get('X-Forwarded-For'))
    
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, use the first one
        source_ip = forwarded_for.split(',')[0].strip()
    
    return source_ip


@logger.inject_lambda_context
def lambda_handler(event: dict, context):
    try:
        # logger custom key logic. Add keys as needed
        logger.append_keys(request_context="test_context")
        
        # Get client identifier for rate limiting
        client_id = get_client_identifier(event)
        logger.append_keys(client_id=client_id)

        # check route
        route = event.get("routeKey", "")
        
        if route == "POST /scrape":
            # Check rate limit for scraping endpoint
            is_allowed, rate_info = scrape_rate_limiter.is_allowed(client_id)
            
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for scrape endpoint. Client: {client_id}")
                return {
                    'statusCode': 429,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Retry-After': str(rate_info['retry_after']),
                        'X-RateLimit-Limit': str(rate_info['limit']),
                        'X-RateLimit-Window': str(rate_info['window_seconds']),
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Rate limit exceeded',
                        'message': f"Too many requests. Please try again in {rate_info['retry_after']} seconds.",
                        'retry_after': rate_info['retry_after']
                    })
                }
            
            from src.controllers.scraping_controller import ScrapingControllerFactory
            controller = ScrapingControllerFactory.createScrapingController()
            
            # Run the async operation in the event loop
            result = asyncio.run(controller.beginScrapingOperation())
            
            return {
                'statusCode': 200,
                'headers': {
                    'X-RateLimit-Limit': str(rate_info['limit']),
                    'X-RateLimit-Remaining': str(rate_info.get('remaining', 0)),
                    'X-RateLimit-Window': str(rate_info['window_seconds']),
                },
                'body': json.dumps({'message': result})
            }
        
        elif route == "POST /chat":
            # Check rate limit for chat endpoint
            is_allowed, rate_info = chat_rate_limiter.is_allowed(client_id)
            
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for chat endpoint. Client: {client_id}")
                return {
                    'statusCode': 429,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Retry-After': str(rate_info['retry_after']),
                        'X-RateLimit-Limit': str(rate_info['limit']),
                        'X-RateLimit-Window': str(rate_info['window_seconds']),
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Rate limit exceeded',
                        'message': f"Too many requests. Please try again in {rate_info['retry_after']} seconds.",
                        'retry_after': rate_info['retry_after']
                    })
                }
            
            from src.controllers.llm_controller import ChatControllerFactory
            controller = ChatControllerFactory.create_chat_controller()
            
            # Handle chat request (stateless)
            response = controller.handle_chat_request(event)
            
            # Add rate limit headers to response
            if 'headers' not in response:
                response['headers'] = {}
            
            response['headers'].update({
                'X-RateLimit-Limit': str(rate_info['limit']),
                'X-RateLimit-Remaining': str(rate_info.get('remaining', 0)),
                'X-RateLimit-Window': str(rate_info['window_seconds']),
            })
            
            return response
        
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Route not found')
            }
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }