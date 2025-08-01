"""
Unit tests for parsing logic.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from pdf_processor import PDFProcessor
from data_extractor import DataExtractor


class TestPDFProcessor:
    """Test PDF processing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = PDFProcessor()
    
    def test_extract_text_success(self):
        """Test successful text extraction."""
        # Mock PDF content
        mock_pdf_data = {
            'text': 'Sample PDF content with inverter information',
            'numpages': 1
        }
        
        with patch('pdf_parse') as mock_pdf_parse:
            mock_pdf_parse.return_value = mock_pdf_data
            
            # Mock file operations
            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                result = self.processor.extract_text('test.pdf')
                
                assert result == 'Sample PDF content with inverter information'
    
    def test_extract_text_no_content(self):
        """Test handling of PDF with no text content."""
        mock_pdf_data = {'text': '', 'numpages': 1}
        
        with patch('pdf_parse') as mock_pdf_parse:
            mock_pdf_parse.return_value = mock_pdf_data
            
            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                with pytest.raises(ValueError, match="No text content found"):
                    self.processor.extract_text('test.pdf')
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        raw_text = "  Sample   text  with  \n\n  extra  spaces  "
        cleaned = self.processor._clean_text(raw_text)
        
        assert cleaned == "Sample text with extra spaces"
    
    def test_clean_text_remove_artifacts(self):
        """Test removal of PDF artifacts."""
        raw_text = "Page 1\n\x00Sample\x00text\nPage 2"
        cleaned = self.processor._clean_text(raw_text)
        
        assert '\x00' not in cleaned
        assert 'Page 1' not in cleaned
        assert 'Page 2' not in cleaned


class TestDataExtractor:
    """Test data extraction functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = DataExtractor()
    
    def test_extract_data_success(self):
        """Test successful data extraction."""
        pdf_text = """
        SolarTech Inc
        Product: INV-5000
        Description: 5000W Inverter
        Startup Voltage: 150V
        Firmware Version: v2.1.4
        Valid From: 2024-01-01T00:00:00Z
        Valid To: 2024-12-31T23:59:59Z
        """
        
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''
        {
            "supplier_name": "SolarTech Inc",
            "product_code": "INV-5000",
            "description": "5000W Inverter",
            "startup_voltage": "150V",
            "firmware_version": "v2.1.4",
            "valid_from": "2024-01-01T00:00:00Z",
            "valid_to": "2024-12-31T23:59:59Z",
            "extras": {}
        }
        '''
        
        with patch.object(self.extractor.client.messages, 'create') as mock_create:
            mock_create.return_value = mock_response
            
            result = self.extractor.extract_data(pdf_text)
            
            assert result['data']['supplier_name'] == "SolarTech Inc"
            assert result['data']['product_code'] == "INV-5000"
            assert result['data']['startup_voltage'] == "150V"
    
    def test_parse_llm_response_with_markdown(self):
        """Test parsing LLM response with markdown formatting."""
        response_text = "```json\n{\"supplier_name\": \"Test\"}\n```"
        
        result = self.extractor._parse_llm_response(response_text)
        
        assert result['data']['supplier_name'] == "Test"
    
    def test_validate_extraction_success(self):
        """Test successful extraction validation."""
        extracted_data = {
            'data': {
                'supplier_name': 'Test',
                'product_code': 'TEST-001',
                'description': 'Test Description',
                'startup_voltage': '150V',
                'firmware_version': 'v1.0',
                'valid_from': '2024-01-01T00:00:00Z',
                'valid_to': '2024-12-31T23:59:59Z'
            }
        }
        
        assert self.extractor.validate_extraction(extracted_data) is True
    
    def test_validate_extraction_missing_fields(self):
        """Test validation with missing required fields."""
        extracted_data = {
            'data': {
                'supplier_name': 'Test',
                'product_code': 'TEST-001'
                # Missing other required fields
            }
        }
        
        assert self.extractor.validate_extraction(extracted_data) is False


if __name__ == "__main__":
    pytest.main([__file__]) 