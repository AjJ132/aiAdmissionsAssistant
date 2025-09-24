import re
from lxml import html as lxml_html
from typing import Dict, List, Union, Optional
import json
import codecs
import html


class ScrapingUtils:
    
    @staticmethod
    def _clean_unicode_escapes(text: str) -> str:
        """
        Clean Unicode characters and escape sequences in text, converting them to proper ASCII characters.
        Handles both literal Unicode characters and escape sequences like \u2019 (right single quotation mark) -> '
        Also handles newlines, HTML entities, and other whitespace characters.
        """
        if not text:
            return text
        
        # First decode HTML entities like &amp; -> &, &quot; -> ", etc.
        text = html.unescape(text)
        
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
        """Extract admission requirements with enhanced logic for KSU pages"""
        requirements = []
        
        # First check if there's a link to admissions requirements section
        req_link = tree.xpath('//a[@href="#admissions_requirements" or contains(@href, "admissions_requirements")]')
        
        if req_link:
            # Enhanced logic for KSU pages with admissions_requirements anchor
            req_section = tree.xpath('//*[@id="admissions_requirements"]')
            
            if req_section:

                # Find the parent section containing the admissions requirements
                section_parent = None
                current = req_section[0]
                
                # Traverse up to find the section container
                for _ in range(5):  # Limit traversal depth
                    current = current.getparent()
                    if current is not None and 'section' in current.get('class', ''):
                        section_parent = current
                        break
                
                if section_parent is not None:
                    # Look for all ul elements in the section
                    lists = section_parent.xpath('.//ul//li')
                    for li in lists:
                        req_text = li.text_content().strip()
                        if len(req_text) > 10:  # Filter out empty or tiny items
                            requirements.append(ScrapingUtils._clean_unicode_escapes(req_text))
                    
                    # Also look for any paragraphs with admission criteria
                    criteria_paragraphs = section_parent.xpath('.//p[contains(text(), "Admission Criteria") or contains(text(), "Additional Program Requirements")]')
                    for p in criteria_paragraphs:
                        # Get the parent container and look for nearby lists
                        p_container = p.getparent()
                        if p_container is not None:
                            nearby_lists = p_container.xpath('.//ul//li | .//ol//li')
                            for li in nearby_lists:
                                req_text = li.text_content().strip()
                                if len(req_text) > 10 and req_text not in [req.split(' - ')[0] for req in requirements]:
                                    requirements.append(ScrapingUtils._clean_unicode_escapes(req_text))
                    
                    # Look for text content in two-column divs that might contain requirements
                    two_col_divs = section_parent.xpath('.//div[contains(@class, "two_col")]//div')
                    for div in two_col_divs:
                        text_content = div.text_content().strip()
                        # Check if this looks like requirement text (contains key phrases)
                        if (len(text_content) > 50 and 
                            any(keyword in text_content.lower() for keyword in 
                                ['must', 'required', 'should', 'complete', 'prior to', 'accounting', 'gpa', 'hours'])):
                            # Split into sentences and add relevant ones
                            sentences = [s.strip() for s in text_content.split('.') if len(s.strip()) > 20]
                            for sentence in sentences[:3]:  # Limit to first 3 sentences
                                if sentence not in requirements:
                                    requirements.append(ScrapingUtils._clean_unicode_escapes(sentence))
        
        return requirements[:15]  # Increased limit for more comprehensive extraction
    
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
        phone_elements = tree.xpath('//a[starts-with(@href, "tel:")] | //*[contains(text(), "Phone") and not(self::style) and not(self::script)]')
        for elem in phone_elements:
            text = elem.text_content().strip()
            href = elem.get('href', '')
            if 'tel:' in href:
                # Extract phone from tel: link
                phone = href.replace('tel:', '').replace('+1', '').strip()
                contact['phone'] = ScrapingUtils._clean_unicode_escapes(phone)
                break
            elif re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text):
                # Extract phone number from text using regex
                phone_match = re.search(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text)
                if phone_match:
                    contact['phone'] = ScrapingUtils._clean_unicode_escapes(phone_match.group(1))
                    break
        
        # Look for email
        email_elements = tree.xpath('//a[starts-with(@href, "mailto:")] | //*[contains(text(), "@") and not(self::style) and not(self::script)]')
        for elem in email_elements:
            text = elem.text_content().strip()
            href = elem.get('href', '')
            if '@' in text or 'mailto:' in href:
                if 'mailto:' in href:
                    # Clean up mailto href, remove query parameters
                    email = href.replace('mailto:', '').split('?')[0]
                    contact['email'] = ScrapingUtils._clean_unicode_escapes(email)
                elif '@' in text:
                    # Validate that this looks like an email and not CSS code
                    if (re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text) and
                        not text.startswith('.') and  # Not CSS class
                        not '@media' in text and      # Not CSS @media rule
                        not text.count('{') > 0):     # Not CSS code block
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
        
        # Strategy 1: Look for "Related Degrees & Programs" section with cards
        related_headings = tree.xpath('//*[contains(text(), "Related Degrees") or contains(text(), "Related Programs")]')
        
        for heading in related_headings:
            # Find the parent section and look for cards structure
            current = heading
            for _ in range(8):  # Look up to 8 levels up to find the section
                current = current.getparent()
                if current is not None:
                    # Look for cards div with ul/li structure
                    cards_divs = current.xpath('.//div[contains(@class, "cards")]//ul//li//a[@href]')
                    for link in cards_divs:
                        href = link.get('href')
                        # Skip navigation links and non-program links
                        if not href or href.startswith('#') or 'navigation' in href.lower():
                            continue
                            
                        # Look for title text in p tag with class "title" or just get text content
                        title_elem = link.xpath('.//p[contains(@class, "title")]')
                        if title_elem:
                            text = title_elem[0].text_content().strip()
                        else:
                            text = link.text_content().strip()
                        
                        # Clean up text and validate
                        if text and len(text) > 3 and text not in ['Sign Up', 'Learn More', 'Apply Now']:
                            # Clean up the URL
                            clean_url = href
                            if href.startswith('http'):
                                clean_url = href
                            elif href.startswith('/'):
                                clean_url = f"https://www.kennesaw.edu{href}"
                            else:
                                clean_url = f"https://www.kennesaw.edu/{href}"
                            
                            programs.append({
                                'name': ScrapingUtils._clean_unicode_escapes(text),
                                'url': clean_url
                            })
                    
                    # If we found programs in this section, break out of parent traversal
                    if programs:
                        break
        
        # Strategy 2: Look for cards sections anywhere on the page that contain degree/program links
        if not programs:
            cards_sections = tree.xpath('//div[contains(@class, "cards")]//ul//li//a[@href]')
            for link in cards_sections:
                href = link.get('href')
                # Skip navigation links and non-program links
                if not href or href.startswith('#') or 'navigation' in href.lower():
                    continue
                
                # Look for degree/program indicators in URL or skip catalog links
                if ('degree' not in href.lower() and 'program' not in href.lower() and 
                    'master' not in href.lower() and 'mba' not in href.lower() and
                    'catalog.kennesaw.edu' not in href.lower()):
                    continue
                    
                # Look for title text in p tag with class "title" or just get text content
                title_elem = link.xpath('.//p[contains(@class, "title")]')
                if title_elem:
                    text = title_elem[0].text_content().strip()
                else:
                    text = link.text_content().strip()
                
                # Clean up text and validate
                if text and len(text) > 3 and text not in ['Sign Up', 'Learn More', 'Apply Now']:
                    # Clean up the URL
                    clean_url = href
                    if href.startswith('http'):
                        clean_url = href
                    elif href.startswith('/'):
                        clean_url = f"https://www.kennesaw.edu{href}"
                    else:
                        clean_url = f"https://www.kennesaw.edu/{href}"
                    
                    programs.append({
                        'name': ScrapingUtils._clean_unicode_escapes(text),
                        'url': clean_url
                    })
        
        # Strategy 3: Fallback - Look for any section with "Related" in text
        if not programs:
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
                            ('degree' in href.lower() or 'program' in href.lower() or 'master' in href.lower())):
                            programs.append({
                                'name': ScrapingUtils._clean_unicode_escapes(text),
                                'url': href if href.startswith('http') else f"https://www.kennesaw.edu{href}"
                            })
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_programs = []
        for program in programs:
            if program['url'] not in seen_urls:
                seen_urls.add(program['url'])
                unique_programs.append(program)
        
        return unique_programs[:6]  # Limit results to 6
    
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
