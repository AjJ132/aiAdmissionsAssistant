import json

def lambda_handler(event, context):
    """
    Basic Lambda handler for AI Admissions Assistant
    """
    
    # Handle API Gateway events
    if 'httpMethod' in event:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'message': 'AI Admissions Assistant API is running!',
                'method': event.get('httpMethod'),
                'path': event.get('path')
            })
        }
    
    # Handle direct invocation
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'AI Admissions Assistant Lambda is running!',
            'event': event
        })
    }
