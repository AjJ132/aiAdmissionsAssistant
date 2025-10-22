import json
import asyncio
from typing import List, Dict, Optional
from src.services.web_request_service import WebRequestService
from src.util.scraping_utils import ScrapingUtils

class ScrapingControllerFactory:
    @staticmethod
    def createScrapingController():
        # Load config from json file
        with open('src/util/scraping_config.json') as f:
            config = json.load(f)
        return ScrapingController(
            webRequestService=WebRequestService(), 
            scraping_utils=ScrapingUtils(), 
            config=config
        )

class ScrapingController:
    def __init__(self, webRequestService: WebRequestService, scraping_utils: ScrapingUtils, config: dict):
        self.webRequestService = webRequestService
        self.scraping_utils = scraping_utils
        self.config = config
        self.obtained_degrees = []
        
        # Concurrency control
        self.max_concurrent_requests = config.get('max_concurrent_requests', 20)
        self.semaphore = None  # Will be initialized in async context

    async def beginScrapingOperation(self):
        """Begin the complete scraping operation asynchronously"""
        print("Beginning scraping operation...")
        
        # Initialize semaphore in async context
        self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        async with self.webRequestService:  # Use context manager
            try:
                self.obtained_degrees = await self.obtainDegreeList()

                if not self.obtained_degrees:
                    print("No degrees obtained from scraping.")
                    return None

                print(f"Starting concurrent scraping of {len(self.obtained_degrees)} degrees...")
                
                # Create semaphore-controlled tasks for all degrees
                tasks = [
                    self._scrape_degree_with_semaphore(degree['name'], degree['url'])
                    for degree in self.obtained_degrees
                ]
                
                # Process all degrees concurrently
                degree_information = []
                completed = 0
                
                # Use as_completed to get results as they finish
                for coro in asyncio.as_completed(tasks):
                    try:
                        result = await coro
                        if result:
                            degree_information.append(result)
                        completed += 1
                        
                        # Progress update
                        if completed % 10 == 0:
                            print(f"Completed {completed}/{len(tasks)} degrees")
                            
                    except Exception as e:
                        print(f"Error processing degree: {e}")
                        completed += 1

                print(f"Scraping complete! Successfully processed {len(degree_information)} degrees")

                # sort by name in ABC order
                degree_information.sort(key=lambda x: x['name'])

                # Save to file
                with open('scraped_degrees_output.json', 'w') as f:
                    json.dump(degree_information, f, indent=4)

                return degree_information

            except Exception as e:
                print(f"Error during scraping operation: {e}")
                raise e

    async def _scrape_degree_with_semaphore(self, degree_name: str, degree_url: str) -> Optional[Dict]:
        """Scrape a single degree page with semaphore control"""
        if self.semaphore is None:
            self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        async with self.semaphore:  # Limit concurrent requests
            try:
                scraped_info = await self.scrapeDegreePage(degree_name, degree_url)
                return {
                    'name': degree_name,
                    'url': degree_url,
                    **scraped_info
                }
            except Exception as e:
                print(f"Failed to scrape {degree_name}: {e}")
                return None

    async def obtainDegreeList(self) -> List[Dict]:
        """Obtain the list of degrees asynchronously"""
        url = self.config.get("grad_admissions_list_url")
        xpath = self.config.get("grad_admissions_list_xpath")
        
        if not url:
            raise ValueError("Graduate admissions list URL not found in config")
        if not xpath:
            raise ValueError("Graduate admissions list XPath not found in config")

        try:
            print(f"Fetching degree list from: {url}")
            page_html = await self.webRequestService.fetchPage(url)

            # Save to file for debugging
            with open('debug_grad_degrees.html', 'w') as f:
                f.write(page_html)

            grad_degrees = self.scraping_utils.parse_degree_list(page_html, xpath)

            # Check if grad_degrees is empty
            if not grad_degrees:
                raise ValueError("No graduate degrees found on the page")
            
            print(f"Obtained {len(grad_degrees)} graduate degrees.")
            return grad_degrees
            
        except Exception as e:
            print(f"Error fetching degree list: {e}")
            raise e
        
    async def scrapeDegreePage(self, degree_name: str, degree_url: str) -> Dict:
        """Scrape a single degree page asynchronously"""
        try:
            page_html = await self.webRequestService.fetchPage(degree_url)

            # write to file for debugging
            debug_filename = f"debug_html.html"
            with open(debug_filename, 'w') as f:
                f.write(page_html)

            print(f"Extracting degree page for: {degree_name}")
            degree_information = self.scraping_utils.extract_main_content(page_html)

            if not degree_information:
                raise ValueError(f"No information parsed for degree: {degree_name}")

            degree_information['scraped_url'] = degree_url
            degree_information['scraped_degree_name'] = degree_name

            return degree_information
            
        except Exception as e:
            print(f"Error scraping degree page for {degree_name}: {e}")
            raise e

    async def scrape_batch(self, degrees: List[Dict], batch_size: int = 50) -> List[Dict]:
        """
        Alternative method: Scrape degrees in batches with delays between batches
        Useful for being more respectful to the target server
        """
        all_results = []
        
        async with self.webRequestService:
            for i in range(0, len(degrees), batch_size):
                batch = degrees[i:i + batch_size]
                print(f"Processing batch {i//batch_size + 1}/{(len(degrees)-1)//batch_size + 1} ({len(batch)} degrees)")
                
                # Process batch concurrently
                tasks = [
                    self._scrape_degree_with_semaphore(degree['name'], degree['url'])
                    for degree in batch
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter out exceptions and None results
                valid_results = [r for r in batch_results if r is not None and not isinstance(r, Exception)]
                all_results.extend(valid_results)
                
                print(f"Batch complete: {len(valid_results)}/{len(batch)} successful")
                
                # Brief delay between batches to be respectful
                if i + batch_size < len(degrees):
                    await asyncio.sleep(1)
        
        return all_results