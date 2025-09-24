import json
import time
import asyncio

from typing import Dict, Any

from aws_lambda_powertools import Logger

logger = Logger()

@logger.inject_lambda_context
def lambda_handler(event: dict, context):
    # For async operations, we'll run them in an event loop
    return asyncio.run(async_lambda_handler(event, context))

async def async_lambda_handler(event: dict, context):
    handler_start_time = time.time()
    try:
        # logger custom key logic. Add keys as needed
        logger.append_keys(request_context="test_context")
        
        logger.info("Lambda handler started")
        logger.info(f"Event: {json.dumps(event)}")

        # check route - handle both API Gateway v1 and v2 formats
        # v2 format uses routeKey, v1 format uses httpMethod + resource/path
        route = event.get("routeKey", "")
        if not route:
            # API Gateway v1 format
            method = event.get("httpMethod", "")
            path = event.get("resource", event.get("path", ""))
            route = f"{method} {path}"
        
        if route == "POST /scrape" or (event.get("httpMethod") == "POST" and "/scrape" in event.get("path", "")):
            scrape_start_time = time.time()
            logger.info("Starting scraping operation...")
            
            from src.controllers.scraping_controller import ScrapingControllerFactory
            controller = ScrapingControllerFactory.createScrapingController()
            result = await controller.beginScrapingOperation()
            
            scrape_end_time = time.time()
            scrape_duration = scrape_end_time - scrape_start_time
            logger.info(f"Scraping operation completed in {scrape_duration:.2f} seconds")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': result, 'scrape_duration_seconds': round(scrape_duration, 2)})
            }
        elif route == "POST /chat" or (event.get("httpMethod") == "POST" and "/chat" in event.get("path", "")):
            chat_start_time = time.time()
            logger.info("Starting chat/LLM operation...")
            
            # For now, return a placeholder response since LLM controller is empty
            # TODO: Implement LLM controller functionality
            # from src.controllers.llm_controller import LLMController
            
            chat_end_time = time.time()
            chat_duration = chat_end_time - chat_start_time
            logger.info(f"Chat operation completed in {chat_duration:.2f} seconds")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Chat endpoint is available but not yet implemented', 
                    'chat_duration_seconds': round(chat_duration, 2)
                })
            }
        else:
            # Default route - health check
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'AI Admissions Assistant API is running!',
                    'available_routes': ['/scrape', '/chat'],
                    'method': event.get('httpMethod', 'Unknown'),
                    'path': event.get('path', event.get('resource', 'Unknown'))
                })
            }
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps('Internal Server Error')
        }
    finally:
        handler_end_time = time.time()
        handler_duration = handler_end_time - handler_start_time
        logger.info(f"Lambda handler completed in {handler_duration:.2f} seconds")