import re
from bs4 import BeautifulSoup
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
        
        # Apply escape sequence mappings (for strings containing literal \uXXXX patterns)
        for unicode_seq, replacement in unicode_escape_mappings.items():
            text = text.replace(unicode_seq, replacement)
        
        # Only attempt to decode escape sequences if the string contains them
        # This prevents mangling of already-decoded UTF-8 characters
        if r'\u' in text or r'\x' in text:
            try:
                # This will decode any remaining \uXXXX or \xXX sequences
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
    def _convert_tables_to_markdown(element) -> str:
        """
        Convert HTML tables within an element to markdown format.
        Also includes any paragraph text found.
        """
        from bs4 import Tag
        
        result_parts = []
        
        # Find all tables in the element
        tables = element.find_all('table')
        
        for table in tables:
            markdown_table = []
            
            # Process thead
            thead = table.find('thead')
            if thead:
                header_rows = thead.find_all('tr')
                for row in header_rows:
                    cells = row.find_all(['th', 'td'])
                    if cells:
                        # Extract header text
                        headers = [cell.get_text(strip=True) for cell in cells]
                        headers = [ScrapingUtils._clean_unicode_escapes(h) for h in headers]
                        
                        # Create markdown header row
                        markdown_table.append('| ' + ' | '.join(headers) + ' |')
                        # Create separator row
                        markdown_table.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
            
            # Process tbody
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        # Extract cell text
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        cell_texts = [ScrapingUtils._clean_unicode_escapes(c) for c in cell_texts]
                        
                        # Create markdown data row
                        markdown_table.append('| ' + ' | '.join(cell_texts) + ' |')
            
            if markdown_table:
                result_parts.append('\n'.join(markdown_table))
        
        # Also extract any paragraph text
        paragraphs = element.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                text = ScrapingUtils._clean_unicode_escapes(text)
                result_parts.append('\n' + text)
        
        return '\n\n'.join(result_parts)
    
    @staticmethod
    def extract_main_content(html: str) -> Dict[str, Union[str, Dict, List]]:
        """
        Extract comprehensive content from a university degree page using multiple strategies
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            'title': ScrapingUtils._extract_title(soup),
            'description': ScrapingUtils._extract_description(soup),
            'program_snapshot': ScrapingUtils._extract_program_snapshot(soup),
            'admission_requirements': ScrapingUtils._extract_admission_requirements(soup),
            'program_benefits': ScrapingUtils._extract_program_benefits(soup),
            'contact_info': ScrapingUtils._extract_contact_info(soup),
            'related_programs': ScrapingUtils._extract_related_programs(soup),
            'catalog_links': ScrapingUtils._extract_catalog_links(soup),
            'key_sections': ScrapingUtils._extract_key_sections(soup),
            'all_text': ScrapingUtils._extract_clean_text(soup)
        }
        
        return result
    
    @staticmethod
    def _extract_title(soup) -> str:
        """Extract page title using multiple fallback strategies"""
        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text().strip()
            if title and len(title) >= 3:
                return ScrapingUtils._clean_unicode_escapes(title)
        
        # Try title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            if title and len(title) >= 3:
                return ScrapingUtils._clean_unicode_escapes(title)
        
        # Try banner message
        banner = soup.find(class_=lambda x: x and 'banner_message' in x)
        if banner:
            h1 = banner.find('h1')
            if h1:
                title = h1.get_text().strip()
                if title and len(title) >= 3:
                    return ScrapingUtils._clean_unicode_escapes(title)
        
        return "Title not found"
    
    @staticmethod
    def _extract_description(soup) -> str:
        """Extract main program description with fallbacks"""
        # Look for substantial paragraphs
        for selector in [
            soup.find('div', class_=lambda x: x and 'content' in x),
            soup.find('main'),
            soup.find('div', role='main')
        ]:
            if selector:
                paragraphs = selector.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 100:
                        return ScrapingUtils._clean_unicode_escapes(text)
        
        # Fallback: look for any substantial paragraph
        all_paragraphs = soup.find_all('p')
        for p in all_paragraphs:
            text = p.get_text().strip()
            if len(text) > 100 and ('master' in text.lower() or 'program' in text.lower()):
                return ScrapingUtils._clean_unicode_escapes(text)
                    
        return "Description not found"
    
    @staticmethod
    def _extract_program_snapshot(soup) -> Dict[str, str]:
        """Extract structured program information"""
        snapshot = {}
        
        # Look for snapshot section
        snapshot_section = soup.find('h3', id='snapshot')
        if not snapshot_section:
            snapshot_section = soup.find(string=re.compile(r'Program Snapshot|Snapshot', re.I))
            if snapshot_section:
                snapshot_section = snapshot_section.parent
        
        if snapshot_section:
            # Find parent container and extract key-value pairs
            container = snapshot_section.parent
            if container:
                paragraphs = container.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if ':' in text and len(text) < 200:
                        key, value = text.split(':', 1)
                        snapshot[ScrapingUtils._clean_unicode_escapes(key.strip())] = ScrapingUtils._clean_unicode_escapes(value.strip())
        
        # Fallback: look for common program info patterns anywhere
        if not snapshot:
            all_paragraphs = soup.find_all('p')
            for p in all_paragraphs:
                text = p.get_text().strip()
                if ':' in text and len(text) < 200:
                    if any(keyword in text.lower() for keyword in ['credit', 'hour', 'term', 'format', 'time', 'degree']):
                        key, value = text.split(':', 1)
                        snapshot[ScrapingUtils._clean_unicode_escapes(key.strip())] = ScrapingUtils._clean_unicode_escapes(value.strip())
        
        return snapshot
    
    @staticmethod
    def _extract_admission_requirements(soup) -> List[str]:
        """Extract admission requirements"""
        requirements = []
        
        # Find requirements section
        req_heading = soup.find(string=re.compile(r'Admission Requirements', re.I))
        
        if req_heading:
            heading_parent = req_heading.parent
            # Look for the container
            container = heading_parent.parent if heading_parent else None
            if container:
                # Find lists
                lists = container.find_all(['ul', 'ol'])
                for ul in lists:
                    items = ul.find_all('li')
                    for li in items:
                        req_text = li.get_text().strip()
                        if len(req_text) > 10:
                            requirements.append(ScrapingUtils._clean_unicode_escapes(req_text))
        
        # Fallback: broader search
        if not requirements:
            admission_text = soup.find(string=re.compile(r'Admission', re.I))
            if admission_text:
                parent = admission_text.parent
                if parent:
                    container = parent.parent
                    if container:
                        lists = container.find_all(['ul', 'ol'])
                        for ul in lists:
                            items = ul.find_all('li')
                            for li in items:
                                req_text = li.get_text().strip()
                                if len(req_text) > 10:
                                    requirements.append(ScrapingUtils._clean_unicode_escapes(req_text))
        
        return requirements[:10]
    
    @staticmethod
    def _extract_program_benefits(soup) -> List[str]:
        """Extract program benefits or learning outcomes"""
        benefits = []
        
        # Look for benefits sections
        benefit_heading = soup.find(string=re.compile(r'Benefit|learn|skill', re.I))
        
        if benefit_heading:
            parent = benefit_heading.parent
            if parent:
                container = parent.parent
                if container:
                    lists = container.find_all(['ul', 'ol'])
                    for ul in lists:
                        items = ul.find_all('li')
                        for li in items:
                            benefit = li.get_text().strip()
                            if len(benefit) > 15:
                                benefits.append(ScrapingUtils._clean_unicode_escapes(benefit))
        
        return benefits
    
    @staticmethod
    def _extract_contact_info(soup) -> Dict[str, str]:
        """Extract contact information"""
        contact = {}
        
        # Look for phone numbers
        phone_links = soup.find_all('a', href=re.compile(r'^tel:'))
        if phone_links:
            contact['phone'] = ScrapingUtils._clean_unicode_escapes(phone_links[0].get_text().strip())
        else:
            # Look for phone text
            phone_text = soup.find(string=re.compile(r'Phone', re.I))
            if phone_text:
                parent_text = phone_text.parent.get_text() if phone_text.parent else str(phone_text)
                phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', parent_text)
                if phone_match:
                    contact['phone'] = ScrapingUtils._clean_unicode_escapes(phone_match.group())
        
        # Look for email
        email_links = soup.find_all('a', href=re.compile(r'^mailto:'))
        if email_links:
            contact['email'] = ScrapingUtils._clean_unicode_escapes(email_links[0]['href'].replace('mailto:', ''))
        else:
            # Look for email in text
            email_text = soup.find(string=re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'))
            if email_text:
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', str(email_text))
                if email_match:
                    contact['email'] = ScrapingUtils._clean_unicode_escapes(email_match.group())
        
        # Look for address
        for indicator in ['Campus', 'Address', 'Location']:
            address_text = soup.find(string=re.compile(indicator, re.I))
            if address_text and address_text.parent:
                text = address_text.parent.get_text()
                if re.search(r'\d+.*(?:Road|Street|Drive|Ave|Pkwy).*\d{5}', text):
                    contact['address'] = ScrapingUtils._clean_unicode_escapes(text.strip())
                    break
        
        return contact
    
    @staticmethod
    def _extract_related_programs(soup) -> List[Dict[str, str]]:
        """Extract related programs/degrees"""
        programs = []
        
        # Look for related programs sections
        related_text = soup.find(string=re.compile(r'Related.*(Program|Degree)', re.I))
        
        if related_text:
            parent = related_text.parent
            if parent:
                container = parent.parent
                if container:
                    links = container.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text().strip()
                        if (href and text and 
                            len(text) > 5 and 
                            ('degree' in href.lower() or 'program' in href.lower())):
                            programs.append({
                                'name': ScrapingUtils._clean_unicode_escapes(text),
                                'url': href
                            })
        
        return programs[:5]
    
    @staticmethod
    def _extract_catalog_links(soup) -> List[str]:
        """Extract catalog links (e.g., catalog.kennesaw.edu)"""
        catalog_links = []
        
        # Find all links in the page
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            # Check if the link contains 'catalog.kennesaw.edu'
            if 'catalog.kennesaw.edu' in href:
                # Avoid duplicates
                if href not in catalog_links:
                    catalog_links.append(href)
        
        return catalog_links
    
    @staticmethod
    def _extract_key_sections(soup) -> Dict[str, str]:
        """Extract major content sections by headings"""
        sections = {}
        
        # Find all headings
        headings = soup.find_all(['h2', 'h3', 'h4'])
        
        for heading in headings:
            heading_text = ScrapingUtils._clean_unicode_escapes(heading.get_text().strip())
            if len(heading_text) > 3:
                # Get content following this heading
                content_parts = []
                current = heading.find_next_sibling()
                
                # Collect content until next heading
                count = 0
                while current and count < 5:
                    if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break
                    
                    text = current.get_text().strip()
                    if text and len(text) > 10:
                        content_parts.append(ScrapingUtils._clean_unicode_escapes(text))
                    
                    current = current.find_next_sibling()
                    count += 1
                
                if content_parts:
                    sections[heading_text] = ' '.join(content_parts)[:500]
        
        return sections
    
    @staticmethod
    def _extract_clean_text(soup) -> str:
        """Extract clean, readable text from main content area"""
        # Remove script, style, navigation elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Focus on main content areas
        main_content = soup.find('main') or soup.find('div', role='main') or soup.find(id='main')
        
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return ScrapingUtils._clean_unicode_escapes(text)


    # Simplified public methods (no fallbacks)
    @staticmethod
    def parse_degree_list(html: str, list_xpath: str) -> list:
        print("Parsing degree list from HTML: XPATH =", list_xpath)

        soup = BeautifulSoup(html, 'html.parser')

        # Look for the specific degree list with the 'searchable_list' class
        # This is more specific than searching all ul elements
        degree_list = soup.find('ul', class_='searchable_list')
        
        if not degree_list:
            print("No degree list with class 'searchable_list' found.")
            # Fallback: try to find a ul with 'link_list' class
            degree_list = soup.find('ul', class_='link_list')
        
        if not degree_list:
            print("No degree list with class 'link_list' found.")
            # Fallback: try to find any ul with 'degree' in the class name
            degree_list = soup.find('ul', class_=lambda x: x and 'degree' in x)
        
        if not degree_list:
            print("No degree list with 'degree' in class found.")
            # Final fallback: find all ul elements and use the first one with links
            all_uls = soup.find_all('ul')
            for ul in all_uls:
                if ul.find('a'):
                    degree_list = ul
                    break
            
        if not degree_list:
            print("No degree list found with expected classes.")
            return []

        print("Found degree list element")

        degrees = []
        li_elements = degree_list.find_all('li')
        print(f"Found {len(li_elements)} li elements in the degree list")
        
        for li in li_elements:
            a = li.find('a')
            if a and a.get('href'):
                degree_name = a.get_text().strip()
                degree_url = a.get('href')
                if degree_name:  # Only add if there's actual text
                    degrees.append({'name': ScrapingUtils._clean_unicode_escapes(degree_name), 'url': degree_url})

        print(f"Successfully parsed {len(degrees)} degrees")
        return degrees

    @staticmethod
    def get_all_text_content(html) -> str:
        if html is None:
            return ""
        soup = BeautifulSoup(html, 'html.parser')
        return ScrapingUtils._extract_clean_text(soup)

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
            "catalog_links": data.get("catalog_links", []),
            "key_sections": data.get("key_sections", {}),
            "all_text": data.get("all_text", "")
        }

    @staticmethod
    def extract_general_admissions_requirements(html: str) -> Dict[str, str]:
        """
        Extract general admissions requirements from catalog page.
        Targets the main content area containing headings and paragraphs about admissions.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the main content area - look for td with class 'block_content'
        content_td = soup.find('td', class_='block_content')
        
        if not content_td:
            return {
                "error": "Main content area (td.block_content) not found",
                "raw_text": ""
            }
        
        # Extract all the text content, preserving structure
        # We want headings and paragraphs
        text_parts = []
        
        # Find all relevant elements (h1, h2, h3, h4, p, ol, ul)
        for element in content_td.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ol', 'ul']):
            # Skip the jump navigation table content
            if element.find_parent('table', class_='acalog-export-remove'):
                continue
            
            text = element.get_text(separator=' ', strip=True)
            if text:  # Only add non-empty text
                # Add heading markers for better structure
                if element.name in ['h1', 'h2', 'h3', 'h4']:
                    text = f"\n## {text}\n"
                text_parts.append(ScrapingUtils._clean_unicode_escapes(text))
        
        if not text_parts:
            return {
                "error": "No content found in main content area",
                "raw_text": ""
            }
        
        # Join all text parts
        text_content = '\n\n'.join(text_parts)
        
        return {
            "source_url": "https://catalog.kennesaw.edu/content.php?catoid=61&navoid=4606",
            "raw_text": text_content,
            "extracted_at": "general_admissions_requirements",
            "element_count": len(text_parts)
        }
    
    @staticmethod
    def extract_cost_of_attendance(html: str) -> Dict[str, str]:
        """
        Extract cost of attendance information from tabbed interface.
        Specifically extracts Graduate and Online program costs.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            "source_url": "https://campus.kennesaw.edu/current-students/financial-aid/student-resources/cost-of-attendance.php",
            "extracted_at": "cost_of_attendance",
        }
        
        # Find all tab labels
        tab_labels = soup.find_all('label', {'role': 'tab'})
        
        for label in tab_labels:
            label_text = label.get_text(strip=True)
            
            # We're interested in Graduate and Online tabs
            if label_text in ['Graduate', 'Online']:
                # Get the label's id
                label_id = label.get('id')
                
                if label_id:
                    # Find the corresponding tab panel using aria-labelledby
                    tab_panel = soup.find('div', {
                        'role': 'tabpanel',
                        'aria-labelledby': label_id
                    })
                    
                    if tab_panel:
                        # Convert HTML tables to markdown format
                        markdown_content = ScrapingUtils._convert_tables_to_markdown(tab_panel)
                        
                        # Store markdown version
                        key_name = label_text.lower().replace(' ', '_')
                        result[f"{key_name}_text"] = markdown_content
        
        return result
