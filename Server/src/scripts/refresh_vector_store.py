"""
Standalone script to delete all files from the vector store and re-upload fresh data.

Usage:
    python -m src.scripts.refresh_vector_store
    
Or from Server directory:
    python src/scripts/refresh_vector_store.py
"""
import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from aws_lambda_powertools import Logger
from src.util.vector_store_cleanup import delete_all_vector_store_files, get_vector_store_info
from src.controllers.scraping_controller import ScrapingControllerFactory

# Load environment variables
load_dotenv()

logger = Logger()


async def main():
    """Delete all files from vector store and re-upload fresh data"""
    
    # Get vector store ID from environment
    vector_store_id = os.environ.get('OPENAI_VECTOR_STORE_ID')
    
    if not vector_store_id:
        logger.error("OPENAI_VECTOR_STORE_ID environment variable not set")
        print("Error: OPENAI_VECTOR_STORE_ID environment variable not set")
        return 1
    
    print(f"Starting deletion and re-upload process for vector store: {vector_store_id}\n")
    
    # Step 1: Get current vector store info
    print("Getting current vector store info...")
    try:
        info = get_vector_store_info(vector_store_id)
        print(f"  Vector Store Name: {info['name']}")
        print(f"  Status: {info['status']}")
        print(f"  File Counts: {info['file_counts']}")
        print()
    except Exception as e:
        logger.error(f"Error getting vector store info: {e}")
        print(f"Error getting vector store info: {e}\n")
    
    # Step 2: Delete all existing files
    print("Deleting all files from vector store...")
    try:
        deletion_result = delete_all_vector_store_files(vector_store_id)
        print(f"  Deleted {deletion_result['deleted_count']} file(s)")
        if deletion_result.get('failed_count', 0) > 0:
            print(f"  Failed to delete {deletion_result['failed_count']} file(s)")
        print()
    except Exception as e:
        logger.error(f"Error deleting files: {e}")
        print(f"Error deleting files: {e}")
        return 1
    
    # Step 3: Scrape fresh data
    print("Scraping fresh degree data from website...")
    try:
        controller = ScrapingControllerFactory.createScrapingController()
        scrape_result = await controller.beginScrapingOperation()
        print(f"  Scraping complete")
        print(f"  Result: {scrape_result}")
        print()
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        print(f"Error during scraping: {e}")
        return 1
    
    # Step 4: Get final vector store info
    print("Getting updated vector store info...")
    try:
        final_info = get_vector_store_info(vector_store_id)
        print(f"  Vector Store Name: {final_info['name']}")
        print(f"  Status: {final_info['status']}")
        print(f"  File Counts: {final_info['file_counts']}")
        print()
    except Exception as e:
        logger.error(f"Error getting final vector store info: {e}")
        print(f"Error getting final vector store info: {e}\n")
    
    print("Delete and re-upload process complete!")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
