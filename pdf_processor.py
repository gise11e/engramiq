"""
PDF Processing Module

Handles PDF text extraction and preprocessing for solar maintenance documents.
"""

import logging
from pathlib import Path
from typing import Optional

import pdf_parse

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction and preprocessing."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        pass
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF is corrupted or unreadable
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                # Parse PDF and extract text
                pdf_data = pdf_parse(file)
                text = pdf_data['text']
                
                if not text or not text.strip():
                    raise ValueError(f"No text content found in PDF: {pdf_path}")
                
                # Clean and normalize text
                cleaned_text = self._clean_text(text)
                
                logger.info(f"Successfully extracted {len(cleaned_text)} characters from {pdf_path.name}")
                return cleaned_text
                
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {str(e)}")
            raise ValueError(f"Failed to process PDF {pdf_path}: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned and normalized text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        text = text.replace('\x00', '')  # Null characters
        text = text.replace('\r', '\n')  # Normalize line endings
        
        # Remove page numbers and headers/footers (simple heuristic)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip lines that are likely page numbers or headers
            if (len(line) < 3 or 
                line.isdigit() or 
                line.lower() in ['page', 'page of', 'confidential', 'internal use only']):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get metadata about the PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_data = pdf_parse(file)
                
                return {
                    'pages': pdf_data.get('numpages', 0),
                    'info': pdf_data.get('info', {}),
                    'file_size': pdf_path.stat().st_size,
                    'filename': pdf_path.name
                }
                
        except Exception as e:
            logger.error(f"Failed to get PDF info from {pdf_path}: {str(e)}")
            raise ValueError(f"Failed to get PDF info from {pdf_path}: {str(e)}")
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate that a PDF file is readable and contains text.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if PDF is valid, False otherwise
        """
        try:
            text = self.extract_text(pdf_path)
            return len(text.strip()) > 0
        except Exception:
            return False 