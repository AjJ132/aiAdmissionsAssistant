"""
Service for managing OpenAI Assistants API chat operations.

This service implements a stateless chat architecture where:
- One assistant is reused for all users (configured via environment variable)
- One vector store contains all degree program data
- Threads are created per conversation and managed by the client
- Server is stateless - no session storage required
"""

import os
import re
from typing import Dict, Any, Optional, List
from openai import OpenAI
from aws_lambda_powertools import Logger

from src.util.secrets_manager import get_openai_api_key

logger = Logger(child=True)


def clean_citation_annotations(text: str) -> str:
    """
    Remove OpenAI citation annotations from text.
    
    These annotations appear as 【number:number†source】 in the response text
    and should be removed before displaying to users.
    
    Args:
        text: The text containing citation annotations
        
    Returns:
        Cleaned text without citation annotations
    """
    # Pattern matches 【number:number†source】 or similar variations
    # Using Unicode ranges for the special brackets: \u3010 (【) and \u3011 (】)
    # Made more flexible to catch various formats
    pattern = r'[\u3010\[][\d]+:[\d]+[†\u2020]source[\u3011\]]'
    cleaned_text = re.sub(pattern, '', text)
    
    # Also remove any standalone citation patterns that might be left
    # This catches cases like 【4:1†source】 even with extra spaces or at line ends
    pattern2 = r'\s*[\u3010][\d]+:[\d]+[†\u2020]source[\u3011]\s*'
    cleaned_text = re.sub(pattern2, ' ', cleaned_text)
    
    # Clean up any double spaces created by removal
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


class ChatService:
    """Service for handling chat interactions using OpenAI Assistants API"""
    
    def __init__(self, assistant_id: Optional[str] = None):
        """
        Initialize the chat service.
        
        Args:
            assistant_id: Optional assistant ID. If not provided, will look for
                         OPENAI_ASSISTANT_ID environment variable.
        """
        api_key = get_openai_api_key()
        self.client = OpenAI(api_key=api_key)
        
        # Get assistant ID from parameter or environment
        assistant_id_value = assistant_id or os.environ.get('OPENAI_ASSISTANT_ID')
        
        if not assistant_id_value:
            raise ValueError(
                "Assistant ID not configured. Set OPENAI_ASSISTANT_ID environment variable."
            )
        
        # Ensure assistant_id is a string (satisfy type checker)
        self.assistant_id: str = assistant_id_value
        
        logger.info(f"ChatService initialized with assistant_id: {self.assistant_id}")
    
    def create_thread(self) -> str:
        """
        Create a new conversation thread.
        
        Returns:
            str: The thread ID
        """
        try:
            thread = self.client.beta.threads.create()
            logger.info(f"Created new thread: {thread.id}")
            return thread.id
        except Exception as e:
            logger.error(f"Error creating thread: {e}")
            raise
    
    def add_message_to_thread(self, thread_id: str, message: str) -> None:
        """
        Add a user message to an existing thread.
        
        Args:
            thread_id: The thread ID to add the message to
            message: The user's message text
        """
        try:
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            logger.info(f"Added message to thread {thread_id}")
        except Exception as e:
            logger.error(f"Error adding message to thread {thread_id}: {e}")
            raise
    
    def run_assistant(self, thread_id: str) -> Dict[str, Any]:
        """
        Run the assistant on a thread and wait for completion.
        
        Args:
            thread_id: The thread ID to run the assistant on
            
        Returns:
            Dict containing the response and status
        """
        try:
            # Create and poll the run
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            
            logger.info(f"Run completed with status: {run.status}")
            
            if run.status == 'completed':
                # Get the latest message (assistant's response)
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id,
                    limit=1,
                    order="desc"
                )
                
                if messages.data:
                    message = messages.data[0]
                    # Extract text content
                    response_text = ""
                    sources = []
                    
                    for content_block in message.content:
                        if content_block.type == 'text':
                            response_text += content_block.text.value
                            
                            # Extract citations if present
                            if hasattr(content_block.text, 'annotations'):
                                for annotation in content_block.text.annotations:
                                    if hasattr(annotation, 'file_citation') and annotation.type == 'file_citation':
                                        citation = annotation.file_citation  # type: ignore
                                        if hasattr(citation, 'file_id'):
                                            sources.append(citation.file_id)
                    
                    # Clean citation annotations from the response text
                    response_text = clean_citation_annotations(response_text)
                    
                    return {
                        "response": response_text,
                        "sources": sources,
                        "status": "completed"
                    }
                else:
                    return {
                        "error": "No response from assistant",
                        "status": "failed"
                    }
            else:
                # Handle other statuses (failed, cancelled, etc.)
                return {
                    "error": f"Assistant run failed with status: {run.status}",
                    "status": run.status
                }
                
        except Exception as e:
            logger.error(f"Error running assistant on thread {thread_id}: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def chat(self, message: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main stateless chat method.
        
        If no thread_id is provided, creates a new thread.
        Adds the user message to the thread and runs the assistant.
        
        Args:
            message: The user's message
            thread_id: Optional thread ID from previous conversation
            
        Returns:
            Dict containing:
                - response: The assistant's response text
                - thread_id: The thread ID (new or existing)
                - status: The completion status
                - sources: List of source file IDs (if any)
        """
        try:
            # If no thread_id provided, create new thread
            if thread_id is None:
                thread_id = self.create_thread()
                logger.info(f"Created new conversation with thread_id: {thread_id}")
            else:
                logger.info(f"Continuing conversation with thread_id: {thread_id}")
            
            # Add user message to thread
            self.add_message_to_thread(thread_id, message)
            
            # Run assistant and get response
            result = self.run_assistant(thread_id)
            
            # Add thread_id to result
            result["thread_id"] = thread_id
            
            return result
            
        except Exception as e:
            logger.error(f"Error in chat method: {e}")
            return {
                "error": str(e),
                "status": "error",
                "thread_id": thread_id
            }
    
    def get_thread_messages(self, thread_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve messages from a thread (useful for loading conversation history).
        
        Args:
            thread_id: The thread ID to retrieve messages from
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=limit,
                order="asc"
            )
            
            formatted_messages = []
            for message in messages.data:
                content = ""
                for content_block in message.content:
                    if content_block.type == 'text':
                        content += content_block.text.value
                
                formatted_messages.append({
                    "role": message.role,
                    "content": content,
                    "created_at": message.created_at
                })
            
            return formatted_messages
            
        except Exception as e:
            logger.error(f"Error retrieving messages from thread {thread_id}: {e}")
            raise
    
    def delete_thread(self, thread_id: str) -> bool:
        """
        Delete a thread (optional cleanup operation).
        
        Args:
            thread_id: The thread ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            self.client.beta.threads.delete(thread_id)
            logger.info(f"Deleted thread: {thread_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting thread {thread_id}: {e}")
            return False
