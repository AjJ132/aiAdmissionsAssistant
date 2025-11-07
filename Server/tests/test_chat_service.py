"""
Tests for the chat service, including citation annotation cleaning.
"""

import pytest
from src.services.chat_service import clean_citation_annotations


class TestCitationCleaning:
    """Tests for cleaning citation annotations from OpenAI responses"""
    
    def test_clean_single_citation(self):
        """Test cleaning a single citation annotation"""
        text = "This is a test【8:0†source】 with citation."
        expected = "This is a test with citation."
        assert clean_citation_annotations(text) == expected
    
    def test_clean_multiple_citations(self):
        """Test cleaning multiple citation annotations"""
        text = "First citation【1:0†source】 and second【2:1†source】 here."
        expected = "First citation and second here."
        assert clean_citation_annotations(text) == expected
    
    def test_clean_citation_at_end(self):
        """Test cleaning citation at the end of text"""
        text = "The Master of Science in Software Engineering at Kennesaw State University is designed to prepare students for successful careers【8:0†source】."
        expected = "The Master of Science in Software Engineering at Kennesaw State University is designed to prepare students for successful careers."
        assert clean_citation_annotations(text) == expected
    
    def test_no_citations(self):
        """Test text without citations remains unchanged"""
        text = "This text has no citations."
        expected = "This text has no citations."
        assert clean_citation_annotations(text) == expected
    
    def test_empty_string(self):
        """Test empty string"""
        text = ""
        expected = ""
        assert clean_citation_annotations(text) == expected
    
    def test_only_citation(self):
        """Test string with only citation"""
        text = "【8:0†source】"
        expected = ""
        assert clean_citation_annotations(text) == expected
    
    def test_consecutive_citations(self):
        """Test consecutive citations"""
        text = "Text here【1:0†source】【2:0†source】【3:1†source】 continues."
        expected = "Text here continues."
        assert clean_citation_annotations(text) == expected
    
    def test_multiline_with_citations(self):
        """Test multiline text with citations"""
        text = """The program focuses on cutting-edge tools【1:0†source】.
        
        For more information【2:1†source】, visit the website."""
        # Note: The cleaning function normalizes whitespace, so newlines are preserved
        # but extra spaces are cleaned up
        result = clean_citation_annotations(text)
        assert "cutting-edge tools" in result
        assert "visit the website" in result
        assert "【" not in result
        assert "†source" not in result
    
    def test_preserves_other_brackets(self):
        """Test that other bracket types are preserved"""
        text = "This [is normal] and (this too) but【8:0†source】 this is removed."
        expected = "This [is normal] and (this too) but this is removed."
        assert clean_citation_annotations(text) == expected
    
    def test_citation_at_sentence_end(self):
        """Test citation at the end of a sentence with period"""
        text = "This is a sentence【4:1†source】."
        expected = "This is a sentence."
        assert clean_citation_annotations(text) == expected
    
    def test_real_world_example(self):
        """Test the exact pattern reported by user"""
        text = "Some text here【4:1†source】."
        expected = "Some text here."
        assert clean_citation_annotations(text) == expected
