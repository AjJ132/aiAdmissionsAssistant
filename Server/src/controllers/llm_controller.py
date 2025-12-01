"""
Controller for handling chat/LLM-related operations.

This controller implements a stateless chat architecture using OpenAI Assistants API.
"""

import json
from typing import Dict, Any, Optional
from aws_lambda_powertools import Logger

from src.services.chat_service import ChatService

logger = Logger(child=True)


class ChatController:
    """Controller for handling chat requests"""
    
    def __init__(self):
        """Initialize the chat controller"""
        self.chat_service = ChatService()
        logger.info("ChatController initialized")
    
    def handle_chat_request(self, event: dict) -> Dict[str, Any]:
        """
        Handle a chat request from the client.
        
        Expected request body:
        {
            "message": "User's message",
            "thread_id": "optional_thread_id"  // Omit for new conversation
        }
        
        Args:
            event: The Lambda event containing the request
            
        Returns:
            Dict containing:
                - statusCode: HTTP status code
                - body: JSON string with response data
        """
        try:
            # Parse request body
            body = json.loads(event.get('body', '{}'))
            message = body.get('message')
            thread_id = body.get('thread_id')
            
            # Validate message
            if not message or not isinstance(message, str):
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Message is required and must be a string'
                    })
                }
            
            # Validate thread_id if provided
            if thread_id is not None and not isinstance(thread_id, str):
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'thread_id must be a string'
                    })
                }
            
            logger.info(f"Processing chat request - message: '{message[:50]}...', thread_id: {thread_id}")
            
            # Call chat service
            result = self.chat_service.chat(message=message, thread_id=thread_id)
            
            # Check if chat was successful
            if result.get('status') == 'completed':
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'response': result.get('response'),
                        'thread_id': result.get('thread_id'),
                        'sources': result.get('sources', []),
                        'status': 'completed'
                    })
                }
            else:
                # Chat failed or had an error
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': result.get('error', 'Failed to process message'),
                        'thread_id': result.get('thread_id'),
                        'status': result.get('status', 'failed')
                    })
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {e}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid JSON in request body'
                })
            }
        except Exception as e:
            logger.error(f"Error handling chat request: {e}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Internal server error',
                    'details': str(e)
                })
            }


class ChatControllerFactory:
    """Factory for creating ChatController instances"""
    
    @staticmethod
    def create_chat_controller() -> ChatController:
        """
        Create and return a ChatController instance.
        
        Returns:
            ChatController instance
        """
        return ChatController()
