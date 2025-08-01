# Sample PDFs Directory

Place your solar maintenance PDF files in this directory for processing.

## Expected PDF Types

This system is designed to process solar maintenance PDFs that contain information about:

- **Inverters**: Components that convert DC electricity from solar panels to AC electricity
- **Startup Voltage**: Inverter settings that determine when solar panels turn on in the morning
- **Firmware Versions**: Software versions that control inverter parameters/settings
- **Valid Date Ranges**: Date and time ranges when settings were active
- **Supplier Information**: Manufacturer and product details

## File Requirements

- **Format**: PDF files only
- **Content**: Text-based PDFs (not scanned images)
- **Size**: Reasonable file sizes (under 10MB recommended)
- **Naming**: Use descriptive names (e.g., `maintenance_report_2024.pdf`)

## Processing

The system will:
1. Extract text content from each PDF
2. Use LLM to understand context and relationships
3. Extract structured data according to the schema
4. Validate data against `inverter_schema.json`
5. Save versioned records with audit trails

## Example Usage

```bash
# Place your PDFs in this directory
cp your_maintenance_report.pdf samples/

# Run the processor
python main.py --input-dir ./samples --output-dir ./output
```

## Output

Processed data will be saved to the `output/` directory with:
- Individual extraction files (JSON format)
- Complete audit trail (`extractions.json`)
- Version tracking for each source file 