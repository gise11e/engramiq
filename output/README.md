# Output Directory

This directory contains processed data from solar maintenance PDFs.

## File Structure

### `extractions.json`
Main file containing all extractions with metadata:
```json
{
  "created_at": "2024-01-15T10:30:00Z",
  "extractions": [
    {
      "id": "unique_extraction_id",
      "source_file": "maintenance_report_2024.pdf",
      "extracted_at": "2024-01-15T10:30:00Z",
      "version": 1,
      "data": {
        "supplier_name": "SolarTech Inc",
        "product_code": "INV-5000",
        "description": "5000W Inverter",
        "startup_voltage": "150V",
        "firmware_version": "v2.1.4",
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_to": "2024-12-31T23:59:59Z"
      },
      "extras": {
        "additional_fields": "any_unmapped_data"
      },
      "metadata": {
        "file_size": 0,
        "processing_time": 0,
        "llm_model": "claude-3-sonnet-20240229"
      }
    }
  ]
}
```

### Individual Extraction Files
Each extraction is also saved as a separate JSON file:
- `{extraction_id}.json` - Individual extraction records

## Data Fields

### Required Fields
- **supplier_name**: Name of the supplier/manufacturer
- **product_code**: Product code or model number
- **description**: Description of the inverter product
- **startup_voltage**: Startup voltage setting in volts
- **firmware_version**: Firmware version number
- **valid_from**: Start date and time when settings were active
- **valid_to**: End date and time when settings were active

### Optional Fields
- **unit_price**: Price per unit
- **currency**: Currency code for the price
- **effective_date**: Date when pricing/configuration became effective

### Metadata
- **id**: Unique extraction identifier
- **source_file**: Original PDF filename
- **extracted_at**: Timestamp of extraction
- **version**: Version number for this source file
- **extras**: Additional unmapped data from PDF
- **metadata**: Processing information

## Version Tracking

The system maintains complete version history:
- Each PDF can have multiple extractions (versions)
- Versions are numbered sequentially (1, 2, 3, etc.)
- All versions are retained for audit purposes
- Latest version is the most recent extraction

## Audit Trail

Complete audit trail includes:
- **Source Tracking**: Links each piece of data to source document
- **Timestamp Tracking**: When each extraction occurred
- **Version History**: All previous versions retained
- **Processing Metadata**: LLM model, processing time, etc.

## Compliance Features

- **Data Integrity**: Schema validation ensures data quality
- **Audit Trail**: Complete history for regulatory review
- **Source Preservation**: Original file information maintained
- **Version Control**: Change tracking over time 