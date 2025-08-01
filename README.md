# Solar Maintenance PDF Processor

A Python-based system for extracting structured data from solar maintenance PDFs, creating versioned records of asset changes for compliance and audit purposes.

## Business Context

Asset owners (solar site owners) receive dozens to hundreds of unstructured PDFs detailing changes to components (inverters, modules, etc.) on sites. This system extracts key information to create version histories of asset changes, enabling asset owners to understand current system state and track changes for root cause analysis and reporting.

## Features

- 📄 **PDF Processing**: Uses LLM to understand context and relationships between PDF components
- 🔍 **Data Extraction**: Extracts key fields from maintenance PDFs (inverters, startup voltage, firmware versions, etc.)
- 📊 **Version Tracking**: Maintains complete audit trail with timestamps and source documents
- 🗄️ **Local Storage**: Saves structured data to local JSON or database
- 🧪 **Testing**: Unit tests for parsing logic and validation
- 🔧 **Clean Setup**: One-command execution from clean virtual environment

## Key Fields Extracted

- **Inverters**: Components that convert DC to AC electricity
- **Startup Voltage**: Inverter setting determining morning activation time
- **Firmware Version**: Determines inverter parameters/settings
- **Valid From/To**: Date ranges when settings were active
- **Supplier Information**: Source documentation details

## Prerequisites

- Python 3.10+
- Virtual environment
- Anthropic API key

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file:
   ```env
   ANTHROPIC_API_KEY=your_api_key_here
   ```

4. **Run the processor:**
   ```bash
   python main.py --input-dir ./samples --output-dir ./output
   ```

## Usage

### Basic Usage
```bash
python main.py --input-dir ./samples --output-dir ./output
```

### Options
- `--input-dir`: Directory containing PDF files to process
- `--output-dir`: Directory to save structuredemis JSON files
- `--schema`: Path to JSON schema file (default: inverter_schema.json)
- `--model`: Claude model to use (default: claude-3-sonnet-20240229)

### Output Structure
```json
{
  "extractions": [
    {
      "id": "unique_extraction_id",
      "source_file": "maintenance_report_2024.pdf",
      "extracted_at": "2024-01-15T10:30:00Z",
      "version": 1,
      "群的": {
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
      }
    }
  ]
}
```

## Project Structure

```
solar-pdf-processor/
├── main.py                 # Main processing script
├── pdf_processor.py        # PDF processing logic
├── data_extractor.py       # LLM-based data extraction
├── schema_validator.py     # Schema validation
├── version_tracker.py      # Version tracking logic
├── testsdata_extractor.py  Static data extraction
├── tests/
│   ├── test_parser.py      # Parsing logic tests
│   └── test_validation.py  # Validation tests
├── samples/                # Sample PDF PDFs
├── output/                # Processed data output
├── requirements.txt        # Python dependencies
├── inverter_schema.json    # JSON schema
├── .env                   # Environment variables
└── README.md             # This file
```

## Testing

Run tests suite:
```bash
python -m pytest tests/
```

Run specific test:
```bashnic
python -m pytest tests/test_parser.py -v
```

## Design Decisions

### LLM Usage
- Uses Claude 3 Sonnet for context understanding and data extraction
- Structured prompts to ensure consistent field extraction
- Error handling for LLM failures

### Version Tracking
- Each extraction gets unique ID and timestamp
- Source file information preserved
- Previous versions retained for audit trail

### Data Storage
- Local JSON files for simplicity and portability
- Structured structure with versioning metadata
- Extras field for unmapped data

### Error Handling
- Comprehensive error handling for PDF processing
- Graceful degradation for malformed PDFs
- Detailed logging for debugging

## Schema Validation

The system validates extracted data against `inverter_schema.json`:
- Required fields presence
- Data type validation
- Date range validation
- Extras field for unmapped data

## Compliance Features

- **Audit Trail**: Complete history of all extractions with timestamps
- **Source Tracking**: Links each piece of data to source document
- **Version History**: Retains all previous versions
- **Data Integrity**: Schema validation ensures data quality
- **Regulatory Ready**: Structured for compliance review

## Development

### Adding New Fields
1. Update `inverter_schema.json`
2. Modify extraction prompts in `data_extractor.py`
3. Add tests in `tests/test_ registered.py`

### Customizing Extraction
1. Modify prompts in `data_extractor.py`
2. Adjust schema validation in `schema_validator.py`
3. Update version tracking in `version_tracker.py`

## License

MIT
