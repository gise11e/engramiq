"""
Data Extraction Module

Uses LLM to extract structured data from PDF text content.
"""

import json
import logging
from typing import Dict, Any, Optional

import anthropic

logger = logging.getLogger(__name__)


class DataExtractor:
    """Extracts structured data from PDF text using LLM."""
    
    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize the data extractor.
        
        Args:
            model: Claude model to use for extraction
        """
        self.model = model
        self.client = anthropic.Anthropic()
        
        # Schema for extraction
        self.schema = {
            "supplier_name": "string",
            "product_code": "string", 
            "description": "string",
            "startup_voltage": "string",
            "firmware_version": "string",
            "valid_from": "string (ISO date-time)",
            "valid_to": "string (ISO date-time)",
            "unit_price": "number (optional)",
            "currency": "string (optional)",
            "effective_date": "string (ISO date, optional)"
        }
    
    def extract_data(self, pdf_text: str) -> Dict[str, Any]:
        """
        Extract structured data from PDF text using LLM.
        
        Args:
            pdf_text: Text content extracted from PDF
            
        Returns:
            Dictionary containing extracted data and extras
        """
        try:
            # Create prompt for LLM
            prompt = self._create_extraction_prompt(pdf_text)
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            extracted_data = self._parse_llm_response(response.content[0].text)
            
            logger.info("Successfully extracted data using LLM")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Failed to extract data using LLM: {str(e)}")
            raise ValueError(f"LLM extraction failed: {str(e)}")
    
    def _create_extraction_prompt(self, pdf_text: str) -> str:
        """
        Create prompt for LLM data extraction.
        
        Args:
            pdf_text: Text content from PDF
            
        Returns:
            Formatted prompt for LLM
        """
        schema_description = """
        Please extract the following fields from the solar maintenance document:
        
        - supplier_name: Name of the supplier/manufacturer
        - product_code: Product code or model number of the inverter
        - description: Description of the inverter product
        - startup_voltage: Startup voltage setting in volts (e.g., "150V")
        - firmware_version: Firmware version number (e.g., "v2.1.4")
        - valid_from: Start date and time when settings were active (ISO format)
        - valid_to: End date and time when settings were active (ISO format)
        - unit_price: Price per unit (optional)
        - currency: Currency code for the price (optional)
        - effective_date: Date when pricing/configuration became effective (optional)
        
        Important context:
        - Inverters convert DC electricity from solar panels to AC electricity
        - Startup voltage determines when solar panels turn on in the morning
        - Firmware version controls inverter parameters/settings
        - Valid from/to dates are crucial for audit trails and root cause analysis
        """
        
        prompt = f"""
        {schema_description}
        
        Please analyze the following solar maintenance document and extract the required fields. 
        Return ONLY a valid JSON object with the extracted data. If a field is not found, 
        use null for that field. Include any additional relevant information in an "extras" field.
        
        Document text:
        {pdf_text}
        
        Return format:
        {{
            "supplier_name": "string or null",
            "product_code": "string or null", 
            "description": "string or null",
            "startup_voltage": "string or null",
            "firmware_version": "string or null",
            "valid_from": "ISO date-time string or null",
            "valid_to": "ISO date-time string or null",
            "unit_price": number or null,
            "currency": "string or null",
            "effective_date": "ISO date string or null",
            "extras": {{
                "additional_fields": "any other relevant information"
            }}
        }}
        """
        
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response and extract structured data.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Parsed data dictionary
        """
        try:
            # Clean response text (remove markdown formatting if present)
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            # Parse JSON
            data = json.loads(cleaned_text)
            
            # Separate main data from extras
            main_data = {}
            extras = data.get("extras", {})
            
            for key in self.schema.keys():
                if key in data and data[key] is not None:
                    main_data[key] = data[key]
            
            return {
                "data": main_data,
                "extras": extras
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            raise ValueError(f"Failed to parse LLM response: {str(e)}")
    
    def validate_extraction(self, extracted_data: Dict[str, Any]) -> bool:
        """
        Validate that required fields are present in extracted data.
        
        Args:
            extracted_data: Extracted data dictionary
            
        Returns:
            True if validation passes, False otherwise
        """
        required_fields = [
            "supplier_name", "product_code", "description", 
            "startup_voltage", "firmware_version", "valid_from", "valid_to"
        ]
        
        data = extracted_data.get("data", {})
        
        for field in required_fields:
            if field not in data or data[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True 