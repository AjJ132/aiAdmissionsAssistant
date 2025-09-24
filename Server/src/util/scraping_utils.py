import re
from lxml import html as lxml_html
from typing import Dict, List, Union, Optional
import json
import codecs


class ScrapingUtils:
    
    @staticmethod
    def _clean_unicode_escapes(text: str) -> str:
        """
        Clean Unicode characters and escape sequences in text, converting them to proper ASCII characters.
        Handles both literal Unicode characters and escape sequences like \u2019 (right single quotation mark) -> '
        Also handles newlines and other whitespace characters.
        """
        if not text:
            return text
        
        # Common Unicode character mappings (for literal Unicode characters)
        unicode_char_mappings = {
            '\u2019': "'",  # Right single quotation mark
            '\u2018': "'",  # Left single quotation mark
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2013': "-",  # En dash
            '\u2014': "—",  # Em dash
            '\u2026': "...", # Horizontal ellipsis
            '\u00a0': " ",  # Non-breaking space
        }
        
        # Common Unicode escape sequence mappings (for \uXXXX patterns)
        unicode_escape_mappings = {
            r'\u2019': "'",  # Right single quotation mark
            r'\u2018': "'",  # Left single quotation mark
            r'\u201c': '"',  # Left double quotation mark
            r'\u201d': '"',  # Right double quotation mark
            r'\u2013': "-",  # En dash
            r'\u2014': "—",  # Em dash
            r'\u2026': "...", # Horizontal ellipsis
            r'\u00a0': " ",  # Non-breaking space
        }
        
        # Apply literal Unicode character mappings first
        for unicode_char, replacement in unicode_char_mappings.items():
            text = text.replace(unicode_char, replacement)
        
        # Apply escape sequence mappings
        for unicode_seq, replacement in unicode_escape_mappings.items():
            text = text.replace(unicode_seq, replacement)
        
        # Handle any remaining Unicode escapes using codecs
        try:
            # This will decode any remaining \uXXXX sequences
            text = codecs.decode(text, 'unicode_escape')
        except (UnicodeDecodeError, UnicodeError):
            # If decoding fails, return the text as-is
            pass
        
        # Clean up newlines and excessive whitespace
        # Replace literal \n with spaces
        text = text.replace('\\n', ' ')
        # Replace actual newlines with spaces
        text = text.replace('\n', ' ')
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        # Replace carriage returns with spaces
        text = text.replace('\r', ' ')
        # Collapse multiple spaces into single spaces
        text = re.sub(r'\s+', ' ', text)
        # Strip leading and trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_main_content(html: str) -> Dict[str, Union[str, Dict, List]]:
        """
        Extract comprehensive content from a university degree page using multiple strategies
        """
        tree = lxml_html.fromstring(html)
        
        result = {
            'title': ScrapingUtils._extract_title(tree),
            'description': ScrapingUtils._extract_description(tree),
            'program_snapshot': ScrapingUtils._extract_program_snapshot(tree),
            'admission_requirements': ScrapingUtils._extract_admission_requirements(tree),
            'program_benefits': ScrapingUtils._extract_program_benefits(tree),
            'contact_info': ScrapingUtils._extract_contact_info(tree),
            'related_programs': ScrapingUtils._extract_related_programs(tree),
            'key_sections': ScrapingUtils._extract_key_sections(tree),
            'all_text': ScrapingUtils._extract_clean_text(tree)
        }
        
        return result
    
    @staticmethod
    def _extract_title(tree) -> str:
        """Extract page title using multiple fallback strategies"""
        selectors = [
            '//h1',
            '//title',
            '//*[@class="banner_message"]//h1',
            '//*[contains(@class, "heading")]//h1'
        ]
        
        for selector in selectors:
            elements = tree.xpath(selector)
            if elements:
                title = elements[0].text_content().strip()
                if title and len(title) > 10:  # Reasonable title length
                    return ScrapingUtils._clean_unicode_escapes(title)
        
        return "Title not found"
    
    @staticmethod
    def _extract_description(tree) -> str:
        """Extract main program description with fallbacks"""
        # Look for the first substantial paragraph after heading
        selectors = [
            '//div[contains(@class, "content")]//p[string-length(text()) > 100][1]',
            '//main//p[string-length(text()) > 100][1]',
            '//div[@role="main"]//p[string-length(text()) > 100][1]',
            '//p[contains(text(), "Master") or contains(text(), "program")][string-length(text()) > 100][1]'
        ]
        
        for selector in selectors:
            elements = tree.xpath(selector)
            if elements:
                desc = elements[0].text_content().strip()
                if len(desc) > 50:
                    return ScrapingUtils._clean_unicode_escapes(desc)
                    
        return "Description not found"
    
    @staticmethod
    def _extract_program_snapshot(tree) -> Dict[str, str]:
        """Extract structured program information"""
        snapshot = {}
        
        # Look for snapshot section by ID or heading
        snapshot_section = None
        for xpath in ['//h3[@id="snapshot"]', '//*[text()="Program Snapshot"]', '//*[contains(text(), "Snapshot")]']:
            elements = tree.xpath(xpath)
            if elements:
                snapshot_section = elements[0]
                break
        
        if snapshot_section is not None:
            # Find parent container and extract key-value pairs
            container = snapshot_section.getparent()
            if container is not None:
                # Look for paragraphs with colon-separated key-value pairs
                for p in container.xpath('.//p'):
                    text = p.text_content().strip()
                    if ':' in text and len(text) < 200:  # Avoid long paragraphs
                        key, value = text.split(':', 1)
                        snapshot[ScrapingUtils._clean_unicode_escapes(key.strip())] = ScrapingUtils._clean_unicode_escapes(value.strip())
        
        # Fallback: look for common program info patterns anywhere
        if not snapshot:
            all_paragraphs = tree.xpath('//p')
            for p in all_paragraphs:
                text = p.text_content().strip()
                if ':' in text and len(text) < 200:
                    # Check if it looks like program info
                    if any(keyword in text.lower() for keyword in ['credit', 'hour', 'term', 'format', 'time', 'degree']):
                        key, value = text.split(':', 1)
                        snapshot[ScrapingUtils._clean_unicode_escapes(key.strip())] = ScrapingUtils._clean_unicode_escapes(value.strip())
        
        return snapshot
    
    @staticmethod
    def _extract_admission_requirements(tree) -> List[str]:
        """Extract admission requirements"""
        requirements = []
        
        # Find requirements section - look for "Admission Requirements" heading
        req_headings = tree.xpath('//*[contains(text(), "Admission Requirements")]')
        
        for heading in req_headings:
            # Look for the parent container that holds the requirements
            container = heading.getparent()
            if container is not None:
                # Look for the next sibling that contains the two-column layout
                next_sibling = container.getnext()
                if next_sibling is not None:
                    # Find all ul elements within the two-column layout
                    lists = next_sibling.xpath('.//ul//li')
                    for li in lists:
                        # Get the text content from the div inside li
                        div = li.find('.//div')
                        if div is not None:
                            req_text = div.text_content().strip()
                        else:
                            req_text = li.text_content().strip()
                        
                        if len(req_text) > 10:  # Filter out empty or tiny items
                            requirements.append(ScrapingUtils._clean_unicode_escapes(req_text))
        
        # Fallback: if no requirements found with the specific heading, try broader search
        if not requirements:
            # Look for any heading containing "Admission" and then find nearby lists
            req_headings = tree.xpath('//*[contains(text(), "Admission")]')
            for heading in req_headings:
                container = heading.getparent()
                if container is not None:
                    # Find lists within reasonable distance
                    lists = container.xpath('.//ul//li | .//ol//li')
                    for li in lists:
                        req_text = li.text_content().strip()
                        if len(req_text) > 10:  # Filter out empty or tiny items
                            requirements.append(ScrapingUtils._clean_unicode_escapes(req_text))
        
        return requirements[:10]  # Limit to prevent noise
    
    @staticmethod
    def _extract_program_benefits(tree) -> List[str]:
        """Extract program benefits or learning outcomes"""
        benefits = []
        
        # Look for benefits sections
        benefit_headings = tree.xpath('//*[contains(text(), "Benefit") or contains(text(), "learn") or contains(text(), "skill")]')
        
        for heading in benefit_headings:
            container = heading.getparent()
            if container is not None:
                lists = container.xpath('.//ul//li | .//ol//li')
                for li in lists:
                    benefit = li.text_content().strip()
                    if len(benefit) > 15:
                        benefits.append(ScrapingUtils._clean_unicode_escapes(benefit))
        
        return benefits
    
    @staticmethod
    def _extract_contact_info(tree) -> Dict[str, str]:
        """Extract contact information"""
        contact = {}
        
        # Look for phone numbers
        phone_elements = tree.xpath('//a[starts-with(@href, "tel:")] | //*[contains(text(), "Phone")]')
        for elem in phone_elements:
            text = elem.text_content().strip()
            href = elem.get('href', '')
            if 'tel:' in href or re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text):
                contact['phone'] = ScrapingUtils._clean_unicode_escapes(text)
                break
        
        # Look for email
        email_elements = tree.xpath('//a[starts-with(@href, "mailto:")] | //*[contains(text(), "@")]')
        for elem in email_elements:
            text = elem.text_content().strip()
            href = elem.get('href', '')
            if '@' in text or 'mailto:' in href:
                if 'mailto:' in href:
                    contact['email'] = ScrapingUtils._clean_unicode_escapes(href.replace('mailto:', ''))
                elif '@' in text:
                    contact['email'] = ScrapingUtils._clean_unicode_escapes(text)
                break
        
        # Look for address
        address_indicators = ['Campus', 'Address', 'Location']
        for indicator in address_indicators:
            elements = tree.xpath(f'//*[contains(text(), "{indicator}")]')
            for elem in elements:
                parent = elem.getparent()
                if parent is not None:
                    text = parent.text_content()
                    # Look for patterns that might be addresses
                    if re.search(r'\d+.*(?:Road|Street|Drive|Ave|Pkwy).*\d{5}', text):
                        contact['address'] = ScrapingUtils._clean_unicode_escapes(text.strip())
                        break
        
        return contact
    
    @staticmethod
    def _extract_related_programs(tree) -> List[Dict[str, str]]:
        """Extract related programs/degrees"""
        programs = []
        
        # Look for related programs sections
        related_sections = tree.xpath('//*[contains(text(), "Related") and (contains(text(), "Program") or contains(text(), "Degree"))]')
        
        for section in related_sections:
            container = section.getparent()
            if container is not None:
                # Look for links that might be programs
                links = container.xpath('.//a[@href]')
                for link in links:
                    href = link.get('href')
                    text = link.text_content().strip()
                    if (href and text and 
                        len(text) > 5 and 
                        ('degree' in href.lower() or 'program' in href.lower())):
                        programs.append({
                            'name': ScrapingUtils._clean_unicode_escapes(text),
                            'url': href
                        })
        
        return programs[:5]  # Limit results
    
    @staticmethod
    def _extract_key_sections(tree) -> Dict[str, str]:
        """Extract major content sections by headings"""
        sections = {}
        
        # Find all headings (h2, h3, h4)
        headings = tree.xpath('//h2 | //h3 | //h4')
        
        for heading in headings:
            heading_text = ScrapingUtils._clean_unicode_escapes(heading.text_content().strip())
            if len(heading_text) > 3:
                # Get content following this heading
                content_parts = []
                current = heading.getnext()
                
                # Collect content until next heading or significant break
                for _ in range(5):  # Limit to prevent runaway
                    if current is None:
                        break
                    if current.tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break
                    
                    text = current.text_content().strip()
                    if text and len(text) > 10:
                        content_parts.append(ScrapingUtils._clean_unicode_escapes(text))
                    
                    current = current.getnext()
                
                if content_parts:
                    sections[heading_text] = ' '.join(content_parts)[:500]  # Truncate long content
        
        return sections
    
    @staticmethod
    def _extract_clean_text(tree) -> str:
        """Extract clean, readable text from main content area"""
        # Remove script, style, navigation elements
        for element in tree.xpath('//script | //style | //nav | //header | //footer'):
            element.getparent().remove(element)
        
        # Focus on main content areas
        main_content = tree.xpath('//main | //div[@role="main"] | //*[@id="main"]')
        
        if main_content:
            text = main_content[0].text_content()
        else:
            text = tree.text_content()
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return ScrapingUtils._clean_unicode_escapes(text)
    
    @staticmethod
    def extract_with_readability(html: str) -> str:
        """
        Alternative content extraction using readability approach
        (You'd need to install newspaper3k or readability-lxml for this)
        """
        try:
            from readability import Document
            doc = Document(html)
            return doc.summary()
        except ImportError:
            # Fallback to basic content extraction
            tree = lxml_html.fromstring(html)
            return ScrapingUtils._extract_clean_text(tree)


# Backward compatibility wrapper class
    # Simplified public methods (no fallbacks)
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
                    degrees.append({'name': ScrapingUtils._clean_unicode_escapes(degree_name), 'url': degree_url})

        print(f"Successfully parsed {len(degrees)} degrees")
        return degrees

    @staticmethod
    def get_all_text_content(html) -> str:
        if html is None:
            return ""
        tree = lxml_html.fromstring(html)
        return ScrapingUtils._extract_clean_text(tree)

    @staticmethod
    def parse_degree_page(html: str, description_xpath: Optional[str] = None, snapshot_xpath: Optional[str] = None) -> dict:
        data = ScrapingUtils.extract_main_content(html)
        # Provide backward compatible keys
        return {
            "description": data.get("description", "Description not found"),
            "snapshot": data.get("program_snapshot", {}),
            "paragraphs": [],
            "title": data.get("title"),
            "admission_requirements": data.get("admission_requirements", []),
            "program_benefits": data.get("program_benefits", []),
            "contact_info": data.get("contact_info", {}),
            "related_programs": data.get("related_programs", []),
            "key_sections": data.get("key_sections", {}),
            "all_text": data.get("all_text", "")
        }
