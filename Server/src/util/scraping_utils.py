from lxml import html as lxml_html

class ScrapingUtils:
    @staticmethod
    def parse_degree_list(html: str, list_xpath: str) -> list:
        print("Parsing degree list from HTML: XPATH =", list_xpath)

        # example xpath: "/html/body/div[1]/div[3]/div/div/div/ul"

        tree = lxml_html.fromstring(html)
        degree_elements = tree.xpath(list_xpath)

        if not degree_elements:
            print("No elements found matching the XPath.")
            return []

        print(f"Found {len(degree_elements)} elements matching the XPath.")

        # xpath should get you to the ul element containing the degree list
        # each li child contains an 'a' element with the degree name and URL
        """
        EXAMPLE: <li class=""><a
            href="https://www.kennesaw.edu/degrees-programs/master-degrees/business-administration-conflict-management.php">Business
            Administration/Conflict Management Dual Master's Degree (MBA/MSCM)</a></li>
        """
        degrees = []
        
        # The XPath should return the ul element(s) containing the degree list
        for ul_elem in degree_elements:
            # Find all li elements within this ul
            li_elements = ul_elem.findall('li')
            print(f"Found {len(li_elements)} li elements in the ul")
            
            for li in li_elements:
                a = li.find('a')
                if a is not None:
                    degree_name = a.text_content().strip()
                    degree_url = a.get('href')
                    degrees.append({'name': degree_name, 'url': degree_url})

        print(f"Successfully parsed {len(degrees)} degrees")
        return degrees
                    
    @staticmethod
    def get_all_text_content(html) -> str:
        if html is None:
            return ""
        
        # Get all text from the html page
        tree = lxml_html.fromstring(html)
        text_content = tree.text_content()
        return text_content
        
    @staticmethod
    def parse_degree_page(html: str, description_xpath: str) -> dict:
        tree = lxml_html.fromstring(html)
        description_element = tree.xpath(description_xpath)
        description = description_element[0].text_content().strip() if description_element else "No description found"

        print(f"Extracted description: {description[:100]}...")  # Print first 100 characters

        return {
            "description": description
        }
