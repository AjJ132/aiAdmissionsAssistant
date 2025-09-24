import json
import time

from typing import Dict, Any

from aws_lambda_powertools import Logger

logger = Logger()

@logger.inject_lambda_context
def lambda_handler(event: dict, context):
    handler_start_time = time.time()
    try:
        # logger custom key logic. Add keys as needed
        logger.append_keys(request_context="test_context")
        
        logger.info("Lambda handler started")

        # check route
        route = event.get("routeKey", "")
        if route == "POST /scrape":
            scrape_start_time = time.time()
            logger.info("Starting scraping operation...")
            
            from src.controllers.scraping_controller import ScrapingControllerFactory
            controller = ScrapingControllerFactory.createScrapingController()
            result = controller.beginScrapingOperation()
            
            scrape_end_time = time.time()
            scrape_duration = scrape_end_time - scrape_start_time
            logger.info(f"Scraping operation completed in {scrape_duration:.2f} seconds")
            
            return {
                'statusCode': 200,
                'body': json.dumps({'message': result, 'scrape_duration_seconds': round(scrape_duration, 2)})
            }
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
    finally:
        handler_end_time = time.time()
        handler_duration = handler_end_time - handler_start_time
        logger.info(f"Lambda handler completed in {handler_duration:.2f} seconds")