import json

from typing import Dict, Any

from aws_lambda_powertools import Logger

logger = Logger()

@logger.inject_lambda_context
def lambda_handler(event: dict, context):
    try:
        # logger custom key logic. Add keys as needed
        logger.append_keys(request_context="test_context")
        

        # check route
        route = event.get("routeKey", "")
        if route == "POST /scrape":
            from src.controllers.ScrapingController import ScrapingControllerFactory
            controller = ScrapingControllerFactory.create()
            result = controller.test()
            return {
                'statusCode': 200,
                'body': json.dumps({'message': result})
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