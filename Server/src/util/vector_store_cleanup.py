"""
Utility module for managing vector store cleanup operations.
This module provides functions to delete files from the vector store
as part of the scraping and upload process.
"""
import os
from typing import Dict, Any, Optional
from aws_lambda_powertools import Logger

from src.services.vector_store_service import VectorStoreService

logger = Logger(child=True)


def delete_all_vector_store_files(vector_store_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete all files from the vector store.
    
    Args:
        vector_store_id: Optional vector store ID. If not provided,
                        will use OPENAI_VECTOR_STORE_ID from environment
    
    Returns:
        Dictionary with deletion results including deleted_count and failed_count
        
    Raises:
        ValueError: If no vector store ID is provided or found in environment
    """
    # Get vector store ID from parameter or environment
    vs_id = vector_store_id or os.environ.get('OPENAI_VECTOR_STORE_ID')
    
    if not vs_id:
        raise ValueError("No vector store ID provided and OPENAI_VECTOR_STORE_ID environment variable not set")
    
    logger.info(f"Starting vector store cleanup for: {vs_id}")
    
    # Create vector store service
    vector_service = VectorStoreService(vector_store_id=vs_id)
    
    try:
        # Get current file count before deletion
        try:
            info = vector_service.get_vector_store_info()
            logger.info(f"Vector store status before cleanup: {info.get('file_counts', {})}")
        except Exception as e:
            logger.warning(f"Could not retrieve vector store info before cleanup: {e}")
        
        # Delete all files
        result = vector_service.delete_all_files()
        logger.info(f"Cleanup complete: deleted {result['deleted_count']} files, failed {result.get('failed_count', 0)}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during vector store cleanup: {e}")
        raise


def get_vector_store_info(vector_store_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about the vector store.
    
    Args:
        vector_store_id: Optional vector store ID. If not provided,
                        will use OPENAI_VECTOR_STORE_ID from environment
    
    Returns:
        Dictionary with vector store information
        
    Raises:
        ValueError: If no vector store ID is provided or found in environment
    """
    # Get vector store ID from parameter or environment
    vs_id = vector_store_id or os.environ.get('OPENAI_VECTOR_STORE_ID')
    
    if not vs_id:
        raise ValueError("No vector store ID provided and OPENAI_VECTOR_STORE_ID environment variable not set")
    
    vector_service = VectorStoreService(vector_store_id=vs_id)
    return vector_service.get_vector_store_info()
