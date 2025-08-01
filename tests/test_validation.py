"""
Unit tests for validation logic.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from schema_validator import SchemaValidator
from version_tracker import VersionTracker


class TestSchemaValidator:
    """Test schema validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary schema file
        self.temp_dir = tempfile.mkdtemp()
        self.schema_file = Path(self.temp_dir) / "test_schema.json"
        
        schema = {
            "type": "object",
            "properties": {
                "supplier_name": {"type": "string"},
                "product_code": {"type": "string"},
                "description": {"type": "string"},
                "startup_voltage": {"type": "string"},
                "firmware_version": {"type": "string"},
                "valid_from": {"type": "string", "format": "date-time"},
                "valid_to": {"type": "string", "format": "date-time"}
            },
            "required": [
                "supplier_name", "product_code", "description",
                "startup_voltage", "firmware_version", "valid_from", "valid_to"
            ]
        }
        
        with open(self.schema_file, 'w') as f:
            json.dump(schema, f)
        
        self.validator = SchemaValidator(str(self.schema_file))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_validate_success(self):
        """Test successful validation."""
        extracted_data = {
            "data": {
                "supplier_name": "SolarTech Inc",
                "product_code": "INV-5000",
                "description": "5000W Inverter",
                "startup_voltage": "150V",
                "firmware_version": "v2.1.4",
                "valid_from": "2024-01-01T00:00:00Z",
                "valid_to": "2024-12-31T23:59:59Z"
            }
        }
        
        result = self.validator.validate(extracted_data)
        
        assert result["supplier_name"] == "SolarTech Inc"
        assert result["product_code"] == "INV-5000"
        assert result["startup_voltage"] == "150V"
    
    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields."""
        extracted_data = {
            "data": {
                "supplier_name": "SolarTech Inc",
                "product_code": "INV-5000"
                # Missing other required fields
            }
        }
        
        with pytest.raises(ValueError, match="Data doesn't match schema"):
            self.validator.validate(extracted_data)
    
    def test_clean_data(self):
        """Test data cleaning functionality."""
        raw_data = {
            "supplier_name": "  SolarTech Inc  ",
            "product_code": "INV-5000",
            "description": "",
            "startup_voltage": None,
            "firmware_version": "v2.1.4"
        }
        
        cleaned = self.validator._clean_data(raw_data)
        
        assert cleaned["supplier_name"] == "SolarTech Inc"
        assert "description" not in cleaned  # Empty string removed
        assert "startup_voltage" not in cleaned  # None value removed
        assert cleaned["firmware_version"] == "v2.1.4"
    
    def test_validate_date_format_valid(self):
        """Test valid date format validation."""
        valid_dates = [
            "2024-01-01T00:00:00Z",
            "2024-01-01T00:00:00+00:00",
            "2024-01-01"
        ]
        
        for date in valid_dates:
            assert self.validator.validate_date_format(date) is True
    
    def test_validate_date_format_invalid(self):
        """Test invalid date format validation."""
        invalid_dates = [
            "invalid-date",
            "2024-13-01",  # Invalid month
            "2024-01-32"   # Invalid day
        ]
        
        for date in invalid_dates:
            assert self.validator.validate_date_format(date) is False
    
    def test_get_missing_fields(self):
        """Test getting missing required fields."""
        data = {
            "supplier_name": "SolarTech Inc",
            "product_code": "INV-5000"
            # Missing other required fields
        }
        
        missing = self.validator.get_missing_fields(data)
        
        assert "description" in missing
        assert "startup_voltage" in missing
        assert "firmware_version" in missing
        assert "valid_from" in missing
        assert "valid_to" in missing
        assert "supplier_name" not in missing
        assert "product_code" not in missing
    
    def test_is_valid(self):
        """Test validity check."""
        valid_data = {
            "supplier_name": "SolarTech Inc",
            "product_code": "INV-5000",
            "description": "5000W Inverter",
            "startup_voltage": "150V",
            "firmware_version": "v2.1.4",
            "valid_from": "2024-01-01T00:00:00Z",
            "valid_to": "2024-12-31T23:59:59Z"
        }
        
        assert self.validator.is_valid(valid_data) is True
        
        invalid_data = {
            "supplier_name": "SolarTech Inc"
            # Missing required fields
        }
        
        assert self.validator.is_valid(invalid_data) is False


class TestVersionTracker:
    """Test version tracking functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = VersionTracker(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_extraction(self):
        """Test saving extraction with version tracking."""
        data = {
            "supplier_name": "SolarTech Inc",
            "product_code": "INV-5000",
            "description": "5000W Inverter",
            "startup_voltage": "150V",
            "firmware_version": "v2.1.4",
            "valid_from": "2024-01-01T00:00:00Z",
            "valid_to": "2024-12-31T23:59:59Z"
        }
        
        extraction_id = self.tracker.save_extraction(
            source_file="test.pdf",
            data=data,
            extras={"additional_info": "test"}
        )
        
        assert extraction_id is not None
        assert len(extraction_id) > 0
        
        # Check that extraction was saved
        extractions = self.tracker.get_all_extractions()
        assert len(extractions) == 1
        assert extractions[0]["source_file"] == "test.pdf"
        assert extractions[0]["data"] == data
    
    def test_version_tracking(self):
        """Test version tracking for multiple extractions."""
        data = {"supplier_name": "Test"}
        
        # First extraction
        self.tracker.save_extraction("test.pdf", data)
        
        # Second extraction (should be version 2)
        extraction_id = self.tracker.save_extraction("test.pdf", data)
        
        extraction = self.tracker.get_extraction_by_id(extraction_id)
        assert extraction["version"] == 2
    
    def test_get_extraction_history(self):
        """Test getting extraction history."""
        data = {"supplier_name": "Test"}
        
        # Create multiple extractions
        self.tracker.save_extraction("test1.pdf", data)
        self.tracker.save_extraction("test1.pdf", data)
        self.tracker.save_extraction("test2.pdf", data)
        
        history = self.tracker.get_extraction_history("test1.pdf")
        assert len(history) == 2
        assert history[0]["version"] == 1
        assert history[1]["version"] == 2
    
    def test_get_latest_extraction(self):
        """Test getting latest extraction."""
        data = {"supplier_name": "Test"}
        
        self.tracker.save_extraction("test.pdf", data)
        self.tracker.save_extraction("test.pdf", data)
        
        latest = self.tracker.get_latest_extraction("test.pdf")
        assert latest["version"] == 2
    
    def test_get_statistics(self):
        """Test getting processing statistics."""
        data = {"supplier_name": "Test"}
        
        # Create some extractions
        self.tracker.save_extraction("test1.pdf", data)
        self.tracker.save_extraction("test1.pdf", data)
        self.tracker.save_extraction("test2.pdf", data)
        
        stats = self.tracker.get_statistics()
        
        assert stats["total_extractions"] == 3
        assert stats["unique_files"] == 2
        assert stats["files_with_multiple_versions"] == 1


if __name__ == "__main__":
    pytest.main([__file__]) 