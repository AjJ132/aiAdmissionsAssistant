import json
from src.services.web_request_service import WebRequestService
from src.util.scraping_utils import ScrapingUtils


class ScrapingControllerFactory:
    @staticmethod
    def createScrapingController():
        #load config from json file
        with open('src/util/scraping_config.json') as f:
            config = json.load(f)

        return ScrapingController(webRequestService=WebRequestService(), scraping_utils=ScrapingUtils(), config=config)



class ScrapingController:
    def __init__(self, webRequestService: WebRequestService, scraping_utils: ScrapingUtils, config: dict):
        self.webRequestService = webRequestService
        self.scraping_utils = scraping_utils
        self.config = config
        self.obtained_degrees = []

    def beginScrapingOperation(self):
        print("Beginning scraping operation...")

        try:
            self.obtained_degrees = self.obtainDegreeList()

            if not self.obtained_degrees:
                print("No degrees obtained from scraping.")
                return None
            
            # foreach degree, scrape page 

        except Exception as e:
            print(f"Error during scraping operation: {e}")
            raise e

    def obtainDegreeList(self):
        url = self.config.get("grad_admissions_list_url")
        xpath = self.config.get("grad_admissions_list_xpath")
        if not url:
            raise ValueError("Graduate admissions list URL not found in config")
        if not xpath:
            raise ValueError("Graduate admissions list XPath not found in config")

        try:
            page_html = self.webRequestService.fetchPage(url)

            #save to file
            with open('debug_grad_degrees.html', 'w') as f:
                f.write(page_html)

            grad_degrees = self.scraping_utils.parse_degree_list(page_html, xpath)

            # check if grad_degrees is empty
            if not grad_degrees:
                raise ValueError("No graduate degrees found on the page")
            
            print(f"Obtained {len(grad_degrees)} graduate degrees.")

            return grad_degrees
        except Exception as e:
            print(f"Error fetching degree list: {e}")
            raise e
    