"""
Schema Validation Module

Validates extracted data against JSON schema and handles data type conversions.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validates extracted data against JSON schema."""
    
    def __init__(self, schema_path: str):
        """
        Initialize the schema validator.
        
        Args:
            schema_path: Path to JSON schema file
        """
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """
        Load JSON schema from file.
        
        Returns:
            Loaded schema dictionary
            
        Raises:
            FileNotFoundError: If schema file doesn't exist
            ValueError: If schema file is invalid JSON
        """
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        
        try:
            with open(self.schema_path, 'r') as f:
                schema = json.load(f)
            
            logger.info(f"Successfully loaded schema from {self.schema_path}")
            return schema
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file: {str(e)}")
            raise ValueError(f"Invalid JSON in schema file: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to load schema: {str(e)}")
            raise ValueError(f"Failed to load schema: {str(e)}")
    
    def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted data against schema.
        
        Args:
            extracted_data: Data extracted from PDF
            
        Returns:
            Validated and cleaned data
            
        Raises:
            ValueError: If data doesn't match schema
        """
        try:
            # Get main data from extraction
            data = extracted_data.get("data", {})
            
            # Clean and validate data
            cleaned_data = self._clean_data(data)
            
            # Validate against schema
            validate(instance=cleaned_data, schema=self.schema)
            
            logger.info("Data validation successful")
            return cleaned_data
            
        except ValidationError as e:
            logger.error(f"Schema validation failed: {str(e)}")
            raise ValueError(f"Data doesn't match schema: {str(e)}")
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            raise ValueError(f"Validation failed: {str(e)}")
    
    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize data before validation.
        
        Args:
            data: Raw extracted data
            
        Returns:
            Cleaned data
        """
        cleaned_data = {}
        
        for key, value in data.items():
            if value is None or value == "":
                continue
            
            # Clean string values
            if isinstance(value, str):
                cleaned_value = value.strip()
                if cleaned_value:
                    cleaned_data[key] = cleaned_value
            
            # Keep numeric values as-is
            elif isinstance(value, (int, float)):
                cleaned_data[key] = value
            
            # Skip other types
            else:
                logger.warning(f"Skipping field {key} with unexpected type: {type(value)}")
        
        return cleaned_data
    
    def validate_date_format(self, date_string: str) -> bool:
        """
        Validate date string format.
        
        Args:
            date_string: Date string to validate
            
        Returns:
            True if valid date format, False otherwise
        """
        try:
            # Try parsing as ISO format
            datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return True
        except ValueError:
            try:
                # Try common date formats
                datetime.strptime(date_string, '%Y-%m-%d')
                return True
            except ValueError:
                return False
    
    def get_validation_errors(self, data: Dict[str, Any]) -> List[str]:
        """
        Get detailed validation errors for data.
        
        Args:
            data: Data to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        try:
            validate(instance=data, schema=self.schema)
        except ValidationError as e:
            for error in e.context:
                errors.append(f"{error.path}: {error.message}")
        
        return errors
    
    def get_missing_fields(self, data: Dict[str, Any]) -> List[str]:
        """
        Get list of missing required fields.
        
        Args:
            data: Data to check
            
        Returns:
            List of missing required field names
        """
        required_fields = self.schema.get("required", [])
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        return missing_fields
    
    def is_valid(self, data: Dict[str, Any]) -> bool:
        """
        Check if data is valid according to schema.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            validate(instance=data, schema=self.schema)
            return True
        except ValidationError:
            return False 