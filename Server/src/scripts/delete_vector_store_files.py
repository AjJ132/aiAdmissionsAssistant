"""
Standalone script to delete all files from the OpenAI vector store.

Usage:
    python -m src.scripts.delete_vector_store_files
    
Or from Server directory:
    python src/scripts/delete_vector_store_files.py
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from aws_lambda_powertools import Logger
from src.util.vector_store_cleanup import delete_all_vector_store_files, get_vector_store_info

# Load environment variables
load_dotenv()

logger = Logger()


def main():
    """Delete all files from the vector store with user confirmation"""
    
    # Get vector store ID from environment
    vector_store_id = os.environ.get('OPENAI_VECTOR_STORE_ID')
    
    if not vector_store_id:
        logger.error("OPENAI_VECTOR_STORE_ID environment variable not set")
        print("Error: OPENAI_VECTOR_STORE_ID environment variable not set")
        print("Please set OPENAI_VECTOR_STORE_ID in your .env file or environment variables")
        return 1
    
    print(f"Deleting all files from vector store: {vector_store_id}\n")
    
    # Get current vector store info before deletion
    try:
        print("Getting current vector store info...")
        info = get_vector_store_info(vector_store_id)
        print(f"  Vector Store Name: {info['name']}")
        print(f"  Status: {info['status']}")
        print(f"  Current File Counts: {info['file_counts']}")
        print()
    except Exception as e:
        logger.error(f"Error getting vector store info: {e}")
        print(f"Warning: Could not retrieve vector store info: {e}\n")
    
    # Ask for confirmation
    response = input("Are you sure you want to delete ALL files? This cannot be undone. (yes/no): ")
    
    if response.lower() != 'yes':
        print("Deletion cancelled.")
        return 0
    
    print("\nDeleting files...")
    
    try:
        # Delete all files
        result = delete_all_vector_store_files(vector_store_id)
        print(f"\nSuccessfully deleted {result['deleted_count']} file(s) from vector store")
        
        if result.get('failed_count', 0) > 0:
            print(f"Failed to delete {result['failed_count']} file(s)")
        
        # Get updated info
        try:
            final_info = get_vector_store_info(vector_store_id)
            print(f"\nUpdated vector store info:")
            print(f"  Status: {final_info['status']}")
            print(f"  File Counts: {final_info['file_counts']}")
        except Exception as e:
            logger.warning(f"Could not retrieve final vector store info: {e}")
        
        return 0
            
    except Exception as e:
        logger.error(f"Error deleting files: {e}")
        print(f"\nError deleting files: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
