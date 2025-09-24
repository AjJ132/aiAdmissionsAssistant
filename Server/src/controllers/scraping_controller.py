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
            degree_information = []
            # foreach degree, scrape page 
            # LIMIT to 1 for demo purposes
            for degree in self.obtained_degrees[:1]:
            # for degree in self.obtained_degrees:
                print(f"Scraping degree page: {degree['name']} - {degree['url']}")
                scraped_info = self.scrapeDegreePage(degree['name'], degree['url'])

                degree_info = {
                    'name': degree['name'],
                    'url': degree['url'],
                    **scraped_info
                }
                degree_information.append(degree_info)

            #save to file
            with open('debug_all_degrees.json', 'w') as f:
                json.dump(degree_information, f, indent=4)

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
        
    def scrapeDegreePage(self, degree_name, degree_url):
        try:
            page_html = self.webRequestService.fetchPage(degree_url)

            #save to file
            with open('debug_degree_page.html', 'w') as f:
                f.write(page_html)

            # for demo purposes
            text_content = self.scraping_utils.get_all_text_content(page_html)

            description_xpath = self.config.get("degree", {}).get("description_xpath", "")
            if not description_xpath:    
                raise ValueError("Degree description XPath not found in config")
            
            snapshot_xpath = self.config.get("degree", {}).get("snapshot_xpath", "")
            if not snapshot_xpath:    
                raise ValueError("Degree snapshot XPath not found in config")

            # parse page
            degree_information = self.scraping_utils.parse_degree_page(
                html=page_html,
                description_xpath=description_xpath,
                snapshot_xpath=snapshot_xpath
            )

            if not degree_information:
                raise ValueError(f"No information parsed for degree: {degree_name}")
            
            return degree_information

        except Exception as e:
            print(f"Error fetching degree page for {degree_name}: {e}")
            raise e
    