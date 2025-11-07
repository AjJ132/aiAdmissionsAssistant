import json
import asyncio
import aiohttp
from src.services.web_request_service import WebRequestService
from src.services.vector_store_service import VectorStoreService
from src.util.scraping_utils import ScrapingUtils
from aws_lambda_powertools import Logger

logger = Logger(child=True)


class ScrapingControllerFactory:
    @staticmethod
    def createScrapingController():
        #load config from json file
        with open('src/util/scraping_config.json') as f:
            config = json.load(f)
        
        # Initialize vector store service
        vector_store_service = VectorStoreService()
        
        return ScrapingController(
            webRequestService=WebRequestService(), 
            scraping_utils=ScrapingUtils(), 
            config=config,
            vector_store_service=vector_store_service
        )



class ScrapingController:
    def __init__(self, webRequestService: WebRequestService, scraping_utils: ScrapingUtils, config: dict, vector_store_service: VectorStoreService | None = None):
        self.webRequestService = webRequestService
        self.scraping_utils = scraping_utils
        self.config = config
        self.obtained_degrees = []
        self.vector_store_service = vector_store_service

    async def beginScrapingOperation(self):
        import time
        start_time = time.time()
        print("Beginning scraping operation...")

        try:
            self.obtained_degrees = await self.obtainDegreeList()

            if not self.obtained_degrees:
                print("No degrees obtained from scraping.")
                return None
            
            # Create a shared session for all requests
            async with aiohttp.ClientSession() as session:
                degrees_to_scrape = self.obtained_degrees[:]  # Scrape all degrees
                
                tasks = []
                for degree in degrees_to_scrape:
                    print(f"Queuing degree page for scraping: {degree['name']} - {degree['url']}")
                    tasks.append(self.scrapeDegreePage(degree['name'], degree['url'], session))
                
                print(f"Scraping {len(tasks)} degree pages concurrently...")
                # Execute all scraping tasks concurrently
                scraped_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results and filter out errors
                degree_information = []
                for degree, result in zip(degrees_to_scrape, scraped_results):
                    if isinstance(result, Exception):
                        print(f"Error scraping {degree['name']}: {result}")
                        continue
                    
                    if isinstance(result, dict):
                        degree_info = {
                            'name': degree['name'],
                            'url': degree['url'],
                            **result
                        }
                        degree_information.append(degree_info)
            
            elapsed_time = time.time() - start_time
            print(f"✓ Scraping operation completed in {elapsed_time:.2f} seconds")
            print(f"✓ Successfully scraped {len(degree_information)} out of {len(degrees_to_scrape)} degrees")

            # save to file
            with open('scraped_degrees.json', 'w') as f:
                json.dump(degree_information, f, indent=2)

            exit()
            
            # Upload to OpenAI Vector Store
            if self.vector_store_service and degree_information:
                print("\nPreparing vector store for upload...")
                
                # Delete all existing files before uploading fresh data
                try:
                    from src.util.vector_store_cleanup import delete_all_vector_store_files
                    print("Deleting existing files from vector store...")
                    deletion_result = delete_all_vector_store_files()
                    print(f"Deleted {deletion_result['deleted_count']} existing file(s)")
                except Exception as e:
                    logger.error(f"Error deleting existing files: {e}")
                    print(f"Warning: Failed to delete existing files: {e}")
                    # Continue with upload even if deletion fails
                
                print("Uploading degree data to OpenAI Vector Store...")
                upload_start = time.time()
                
                try:
                    upload_result = self.vector_store_service.upload_degree_data(degree_information)
                    upload_elapsed = time.time() - upload_start
                    
                    print(f"Vector store upload completed in {upload_elapsed:.2f} seconds")
                    print(f"New uploads: {upload_result['new_uploads']}, Updated: {upload_result['updated_files']}, Failed: {upload_result['failed_uploads']}")
                    
                    if upload_result['updated_files'] > 0:
                        logger.info(f"Updated {upload_result['updated_files']} existing degree files")
                    
                    if upload_result['failed_uploads'] > 0:
                        logger.warning(f"Failed to upload {upload_result['failed_uploads']} degrees")
                        for failure in upload_result['failures']:
                            logger.warning(f"  - {failure['degree']}: {failure['error']}")
                    
                    # Return comprehensive results
                    return {
                        'scraping': {
                            'total_degrees': len(degrees_to_scrape),
                            'successful_scrapes': len(degree_information),
                            'duration_seconds': elapsed_time
                        },
                        'vector_store_upload': upload_result
                    }
                    
                except Exception as e:
                    logger.error(f"Error uploading to vector store: {e}")
                    print(f"Warning: Failed to upload to vector store: {e}")
                    # Return scraping results even if upload fails
                    return {
                        'scraping': {
                            'total_degrees': len(degrees_to_scrape),
                            'successful_scrapes': len(degree_information),
                            'duration_seconds': elapsed_time
                        },
                        'vector_store_upload': {
                            'error': str(e)
                        }
                    }
            else:
                if not self.vector_store_service:
                    print("ℹ️  Vector store service not configured, skipping upload")
                
                return {
                    'scraping': {
                        'total_degrees': len(degrees_to_scrape),
                        'successful_scrapes': len(degree_information),
                        'duration_seconds': elapsed_time
                    }
                }

        except Exception as e:
            print(f"Error during scraping operation: {e}")
            raise e

    async def obtainDegreeList(self):
        url = self.config.get("grad_admissions_list_url")
        xpath = self.config.get("grad_admissions_list_xpath")
        if not url:
            raise ValueError("Graduate admissions list URL not found in config")
        if not xpath:
            raise ValueError("Graduate admissions list XPath not found in config")

        try:
            page_html = await self.webRequestService.fetchPage(url)

            grad_degrees = self.scraping_utils.parse_degree_list(page_html, xpath)

            # check if grad_degrees is empty
            if not grad_degrees:
                raise ValueError("No graduate degrees found on the page")
            
            print(f"Obtained {len(grad_degrees)} graduate degrees.")

            # take 3
            # grad_degrees = grad_degrees[:3]

            return grad_degrees
        except Exception as e:
            print(f"Error fetching degree list: {e}")
            raise e
        
    async def scrapeDegreePage(self, degree_name: str, degree_url: str, session: aiohttp.ClientSession) -> dict:
        try:
            page_html = await self.webRequestService.fetchPage(degree_url, session)

            print(f"Extracting degree page (no fallback) for: {degree_name}")
            degree_information = self.scraping_utils.extract_main_content(page_html)

            if not degree_information:
                raise ValueError(f"No information parsed for degree: {degree_name}")

            degree_information['scraped_url'] = degree_url
            degree_information['scraped_degree_name'] = degree_name

            return degree_information
        except Exception as e:
            print(f"Error scraping degree page for {degree_name}: {e}")
            raise e
    