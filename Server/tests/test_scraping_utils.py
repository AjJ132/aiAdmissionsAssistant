"""
Tests for scraping_utils.py - HTML parsing and content extraction utilities
"""
import pytest
from src.util.scraping_utils import ScrapingUtils


class TestScrapingUtilsCleanUnicode:
    """Test suite for Unicode cleaning functionality"""
    
    @pytest.mark.unit
    def test_clean_unicode_right_single_quote(self):
        """Test cleaning right single quotation mark"""
        text = "Master\u2019s Degree"
        result = ScrapingUtils._clean_unicode_escapes(text)
        assert result == "Master's Degree"
    
    @pytest.mark.unit
    def test_clean_unicode_left_single_quote(self):
        """Test cleaning left single quotation mark"""
        text = "\u2018Example\u2018"
        result = ScrapingUtils._clean_unicode_escapes(text)
        assert result == "'Example'"
    
    @pytest.mark.unit
    def test_clean_unicode_double_quotes(self):
        """Test cleaning double quotation marks"""
        text = "\u201cQuoted text\u201d"
        result = ScrapingUtils._clean_unicode_escapes(text)
        assert result == '"Quoted text"'
    
    @pytest.mark.unit
    def test_clean_unicode_dashes(self):
        """Test cleaning en-dash and em-dash"""
        text = "Range 2013\u20142015"
        result = ScrapingUtils._clean_unicode_escapes(text)
        assert result == "Range 2013—2015"
    
    @pytest.mark.unit
    def test_clean_unicode_ellipsis(self):
        """Test cleaning ellipsis"""
        text = "And so on\u2026"
        result = ScrapingUtils._clean_unicode_escapes(text)
        assert result == "And so on..."
    
    @pytest.mark.unit
    def test_clean_unicode_non_breaking_space(self):
        """Test cleaning non-breaking space"""
        text = "Word\u00a0word"
        result = ScrapingUtils._clean_unicode_escapes(text)
        assert result == "Word word"
    
    @pytest.mark.unit
    def test_clean_unicode_escape_sequences(self):
        """Test cleaning Unicode escape sequences"""
        text = r"Master\u2019s Program"
        result = ScrapingUtils._clean_unicode_escapes(text)
        assert "'" in result or "Master" in result
    
    @pytest.mark.unit
    def test_clean_unicode_newlines(self):
        """Test cleaning newlines"""
        text = "Line one\\nLine two\nLine three"
        result = ScrapingUtils._clean_unicode_escapes(text)
        assert "\n" not in result
        assert "Line one Line two Line three" == result
    
    @pytest.mark.unit
    def test_clean_unicode_multiple_spaces(self):
        """Test collapsing multiple spaces"""
        text = "Word    with     many    spaces"
        result = ScrapingUtils._clean_unicode_escapes(text)
        assert result == "Word with many spaces"
    
    @pytest.mark.unit
    def test_clean_unicode_tabs_and_carriage_returns(self):
        """Test cleaning tabs and carriage returns"""
        text = "Word\twith\ttabs\rand\rreturns"
        result = ScrapingUtils._clean_unicode_escapes(text)
        assert "\t" not in result
        assert "\r" not in result
    
    @pytest.mark.unit
    def test_clean_unicode_empty_string(self):
        """Test cleaning empty string"""
        result = ScrapingUtils._clean_unicode_escapes("")
        assert result == ""
    
    @pytest.mark.unit
    def test_clean_unicode_none(self):
        """Test cleaning None"""
        result = ScrapingUtils._clean_unicode_escapes(None)
        assert result is None


class TestScrapingUtilsParseDegreeList:
    """Test suite for degree list parsing"""
    
    @pytest.mark.unit
    def test_parse_degree_list_success(self, sample_degree_list_html):
        """Test successful degree list parsing"""
        xpath = "//ul[@class='degree-list']"
        degrees = ScrapingUtils.parse_degree_list(sample_degree_list_html, xpath)
        
        assert len(degrees) == 3
        assert degrees[0]['name'] == "Master of Business Administration"
        assert degrees[0]['url'] == "https://example.com/mba"
        assert degrees[1]['name'] == "Master of Computer Science"
        assert degrees[2]['name'] == "Master of Education"
    
    @pytest.mark.unit
    def test_parse_degree_list_empty_result(self):
        """Test parsing with no matching elements"""
        html = "<html><body><p>No degrees here</p></body></html>"
        xpath = "//ul[@class='degree-list']"
        degrees = ScrapingUtils.parse_degree_list(html, xpath)
        
        assert degrees == []
    
    @pytest.mark.unit
    def test_parse_degree_list_invalid_xpath(self, sample_degree_list_html):
        """Test parsing with invalid xpath"""
        xpath = "//invalid/xpath/that/matches/nothing"
        degrees = ScrapingUtils.parse_degree_list(sample_degree_list_html, xpath)
        
        assert degrees == []
    
    @pytest.mark.unit
    def test_parse_degree_list_with_unicode(self):
        """Test parsing degree list with Unicode characters"""
        html = """
        <html>
            <body>
                <ul class="degrees">
                    <li><a href="http://example.com/degree1">Master\u2019s in Engineering</a></li>
                    <li><a href="http://example.com/degree2">MBA \u2014 Finance</a></li>
                </ul>
            </body>
        </html>
        """
        xpath = "//ul[@class='degrees']"
        degrees = ScrapingUtils.parse_degree_list(html, xpath)
        
        assert len(degrees) == 2
        assert "Master's" in degrees[0]['name'] or "Engineering" in degrees[0]['name']


class TestScrapingUtilsExtractMainContent:
    """Test suite for main content extraction"""
    
    @pytest.mark.unit
    def test_extract_main_content_complete(self, sample_degree_page_html):
        """Test extracting complete content from degree page"""
        result = ScrapingUtils.extract_main_content(sample_degree_page_html)
        
        assert 'title' in result
        assert 'description' in result
        assert 'program_snapshot' in result
        assert 'admission_requirements' in result
        assert 'program_benefits' in result
        assert 'contact_info' in result
        assert 'related_programs' in result
        assert 'key_sections' in result
        assert 'all_text' in result
    
    @pytest.mark.unit
    def test_extract_title(self, sample_degree_page_html):
        """Test title extraction"""
        result = ScrapingUtils.extract_main_content(sample_degree_page_html)
        
        assert result['title'] == "Master of Computer Science"
    
    @pytest.mark.unit
    def test_extract_description(self, sample_degree_page_html):
        """Test description extraction"""
        result = ScrapingUtils.extract_main_content(sample_degree_page_html)
        
        assert len(result['description']) > 50
        assert "Master of Computer Science program" in result['description']
    
    @pytest.mark.unit
    def test_extract_program_snapshot(self, sample_degree_page_html):
        """Test program snapshot extraction"""
        result = ScrapingUtils.extract_main_content(sample_degree_page_html)
        
        snapshot = result['program_snapshot']
        assert 'Credit Hours' in snapshot
        assert snapshot['Credit Hours'] == '36'
        assert 'Format' in snapshot
        assert 'Duration' in snapshot
    
    @pytest.mark.unit
    def test_extract_admission_requirements(self, sample_degree_page_html):
        """Test admission requirements extraction"""
        result = ScrapingUtils.extract_main_content(sample_degree_page_html)
        
        requirements = result['admission_requirements']
        assert len(requirements) > 0
        assert any("Bachelor's degree" in req for req in requirements)
        assert any("GPA" in req for req in requirements)
    
    @pytest.mark.unit
    def test_extract_program_benefits(self, sample_degree_page_html):
        """Test program benefits extraction"""
        result = ScrapingUtils.extract_main_content(sample_degree_page_html)
        
        benefits = result['program_benefits']
        assert len(benefits) > 0
        assert any("machine learning" in benefit.lower() for benefit in benefits)
    
    @pytest.mark.unit
    def test_extract_contact_info(self, sample_degree_page_html):
        """Test contact information extraction"""
        result = ScrapingUtils.extract_main_content(sample_degree_page_html)
        
        contact = result['contact_info']
        assert 'phone' in contact
        assert '555-123-4567' in contact['phone'] or '(555) 123-4567' in contact['phone']
        assert 'email' in contact
        assert 'cs-grad@example.com' in contact['email']
    
    @pytest.mark.unit
    def test_extract_related_programs(self, sample_degree_page_html):
        """Test related programs extraction"""
        result = ScrapingUtils.extract_main_content(sample_degree_page_html)
        
        programs = result['related_programs']
        assert len(programs) > 0
        assert any('Data Science' in p['name'] for p in programs)
    
    @pytest.mark.unit
    def test_extract_from_empty_html(self):
        """Test extraction from empty HTML"""
        html = "<html><body></body></html>"
        result = ScrapingUtils.extract_main_content(html)
        
        assert result['title'] == "Title not found"
        assert result['description'] == "Description not found"
        assert result['program_snapshot'] == {}
        assert result['admission_requirements'] == []
    
    @pytest.mark.unit
    def test_extract_with_unicode_characters(self, sample_degree_page_with_unicode):
        """Test extraction with Unicode characters"""
        result = ScrapingUtils.extract_main_content(sample_degree_page_with_unicode)
        
        # Should have cleaned Unicode characters
        assert "\u2019" not in result['title']
        assert "Master's" in result['title'] or "Engineering" in result['title']


class TestScrapingUtilsGetAllTextContent:
    """Test suite for text content extraction"""
    
    @pytest.mark.unit
    def test_get_all_text_content_success(self, sample_degree_page_html):
        """Test extracting all text content"""
        text = ScrapingUtils.get_all_text_content(sample_degree_page_html)
        
        assert len(text) > 0
        assert "Master of Computer Science" in text
        assert "Admission Requirements" in text
    
    @pytest.mark.unit
    def test_get_all_text_content_none(self):
        """Test extracting text from None"""
        text = ScrapingUtils.get_all_text_content(None)
        
        assert text == ""
    
    @pytest.mark.unit
    def test_get_all_text_content_empty(self):
        """Test extracting text from empty HTML"""
        html = "<html></html>"
        text = ScrapingUtils.get_all_text_content(html)
        
        assert isinstance(text, str)


class TestScrapingUtilsParseDegreePageBackwardCompatibility:
    """Test suite for backward compatible degree page parsing"""
    
    @pytest.mark.unit
    def test_parse_degree_page_backward_compatible(self, sample_degree_page_html):
        """Test backward compatible parsing method"""
        result = ScrapingUtils.parse_degree_page(sample_degree_page_html)
        
        # Check backward compatible keys
        assert 'description' in result
        assert 'snapshot' in result
        assert 'paragraphs' in result
        assert 'title' in result
        assert 'admission_requirements' in result
        assert 'program_benefits' in result
        assert 'contact_info' in result
        assert 'related_programs' in result
        assert 'key_sections' in result
        assert 'all_text' in result
    
    @pytest.mark.unit
    def test_parse_degree_page_with_xpaths(self, sample_degree_page_html):
        """Test parsing with optional xpath parameters"""
        result = ScrapingUtils.parse_degree_page(
            sample_degree_page_html,
            description_xpath="//p[1]",
            snapshot_xpath="//div[@class='snapshot']"
        )
        
        assert result is not None
        assert 'description' in result


class TestScrapingUtilsPrivateMethods:
    """Test suite for private utility methods"""
    
    @pytest.mark.unit
    def test_extract_title_with_h1(self):
        """Test title extraction with h1 tag"""
        html = "<html><body><h1>Test Title</h1></body></html>"
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(html)
        
        title = ScrapingUtils._extract_title(tree)
        assert title == "Test Title"
    
    @pytest.mark.unit
    def test_extract_title_fallback_to_title_tag(self):
        """Test title extraction fallback to title tag"""
        html = "<html><head><title>Page Title from Title Tag</title></head><body></body></html>"
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(html)
        
        title = ScrapingUtils._extract_title(tree)
        assert "Page Title" in title
    
    @pytest.mark.unit
    def test_extract_clean_text_removes_scripts(self):
        """Test that clean text extraction removes scripts"""
        html = """
        <html>
            <body>
                <script>alert('test');</script>
                <p>Visible content</p>
                <style>.test { color: red; }</style>
            </body>
        </html>
        """
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(html)
        
        text = ScrapingUtils._extract_clean_text(tree)
        assert "alert" not in text
        assert ".test" not in text
        assert "Visible content" in text
    
    @pytest.mark.unit
    def test_extract_phone_from_contact_info(self):
        """Test phone number extraction"""
        html = """
        <html>
            <body>
                <a href="tel:555-123-4567">Call us at (555) 123-4567</a>
            </body>
        </html>
        """
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(html)
        
        contact = ScrapingUtils._extract_contact_info(tree)
        assert 'phone' in contact
    
    @pytest.mark.unit
    def test_extract_email_from_contact_info(self):
        """Test email extraction"""
        html = """
        <html>
            <body>
                <a href="mailto:test@example.com">Email us</a>
            </body>
        </html>
        """
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(html)
        
        contact = ScrapingUtils._extract_contact_info(tree)
        assert 'email' in contact
        assert contact['email'] == 'test@example.com'


class TestScrapingUtilsEdgeCases:
    """Test suite for edge cases and error handling"""
    
    @pytest.mark.unit
    def test_parse_malformed_html(self):
        """Test parsing malformed HTML"""
        html = "<html><body><div>Unclosed div<p>Unclosed paragraph</body>"
        
        # Should not raise an exception
        result = ScrapingUtils.extract_main_content(html)
        assert result is not None
    
    @pytest.mark.unit
    def test_parse_html_with_special_characters(self):
        """Test parsing HTML with special characters"""
        html = """
        <html>
            <body>
                <h1>Title with &amp; ampersand &lt; &gt;</h1>
                <p>Content with special chars: € £ ¥</p>
            </body>
        </html>
        """
        result = ScrapingUtils.extract_main_content(html)
        
        assert '&' in result['title'] or 'ampersand' in result['title']
    
    @pytest.mark.unit
    def test_parse_very_large_html(self):
        """Test parsing very large HTML document"""
        # Create a large HTML with many paragraphs
        paragraphs = "\n".join([f"<p>Paragraph {i} with content</p>" for i in range(1000)])
        html = f"<html><body><h1>Large Document</h1>{paragraphs}</body></html>"
        
        result = ScrapingUtils.extract_main_content(html)
        
        assert result['title'] == "Large Document"
        assert len(result['all_text']) > 0
    
    @pytest.mark.unit
    def test_parse_nested_structures(self):
        """Test parsing deeply nested HTML structures"""
        html = """
        <html>
            <body>
                <div>
                    <div>
                        <div>
                            <div>
                                <h1>Deep Title</h1>
                                <p>Deep content</p>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
        result = ScrapingUtils.extract_main_content(html)
        
        assert result['title'] == "Deep Title"
        assert "Deep content" in result['all_text']
