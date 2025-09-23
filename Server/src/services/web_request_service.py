import requests
from bs4 import BeautifulSoup

class WebRequestService:
    

    def fetchPage(self, url: str) :
        response = requests.get(url)

        # return html
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to fetch page: {url} with status code {response.status_code}")


        