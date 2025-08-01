#!/usr/bin/env python3
"""
Solar Maintenance PDF Processor

Main script for processing solar maintenance PDFs and extracting structured data.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
import click

from pdf_processor import PDFProcessor
from data_extractor import DataExtractor
from schema_validator import SchemaValidator
from version_tracker import VersionTracker

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_directories(output_dir: str) -> None:
    """Create output directory if it doesn't exist."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)


def get_pdf_files(input_dir: str) -> List[Path]:
    """Get all PDF files from input directory."""
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory {input_dir} does not exist")
    
    pdf_files = list(input_path.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
    
    return pdf_files


def process_pdfs(
    input_dir: str,
    output_dir: str,
    schema_path: str,
    model: str
) -> Dict[str, Any]:
    """Process all PDFs in the input directory."""
    
    # Initialize components
    pdf_processor = PDFProcessor()
    data_extractor = DataExtractor(model=model)
    schema_validator = SchemaValidator(schema_path)
    version_tracker = VersionTracker(output_dir)
    
    # Get PDF files
    pdf_files = get_pdf_files(input_dir)
    
    results = {
        "processed_files": 0,
        "successful_extractions": 0,
        "failed_extractions": 0,
        "extractions": []
    }
    
    for pdf_file in pdf_files:
        logger.info(f"Processing {pdf_file.name}")
        
        try:
            # Extract text from PDF
            pdf_text = pdf_processor.extract_text(str(pdf_file))
            
            # Extract structured data using LLM
            extracted_data = data_extractor.extract_data(pdf_text)
            
            # Validate against schema
            validated_data = schema_validator.validate(extracted_data)
            
            # Track version and save
            extraction_id = version_tracker.save_extraction(
                source_file=pdf_file.name,
                data=validated_data,
                extras=extracted_data.get("extras", {})
            )
            
            results["successful_extractions"] += 1
            results["extractions"].append({
                "file": pdf_file.name,
                "extraction_id": extraction_id,
                "status": "success"
            })
            
            logger.info(f"Successfully processed {pdf_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {str(e)}")
            results["failed_extractions"] += 1
            results["extractions"].append({
                "file": pdf_file.name,
                "status": "failed",
                "error": str(e)
            })
        
        results["processed_files"] += 1
    
    return results


@click.command()
@click.option('--input-dir', required=True, help='Directory containing PDF files to process')
@click.option('--output-dir', required=True, help='Directory to save structured JSON files')
@click.option('--schema', default='inverter_schema.json', help='Path to JSON schema file')
@click.option('--model', default='claude-3-sonnet-20240229', help='Claude model to use')
def main(input_dir: str, output_dir: str, schema: str, model: str):
    """
    Process solar maintenance PDFs and extract structured data.
    
    This script processes PDF files containing solar maintenance information,
    extracts key fields using LLM, validates against schema, and maintains
    versioned records for compliance and audit purposes.
    """
    
    # Validate API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        logger.error("ANTHROPIC_API_KEY environment variable is required")
        sys.exit(1)
    
    # Validate schema file
    if not Path(schema).exists():
        logger.error(f"Schema file {schema} does not exist")
        sys.exit(1)
    
    try:
        # Setup output directory
        setup_directories(output_dir)
        
        # Process PDFs
        results = process_pdfs(input_dir, output_dir, schema, model)
        
        # Print summary
        logger.info("=" * 50)
        logger.info("PROCESSING SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total files processed: {results['processed_files']}")
        logger.info(f"Successful extractions: {results['successful_extractions']}")
        logger.info(f"Failed extractions: {results['failed_extractions']}")
        logger.info(f"Output directory: {output_dir}")
        
        if results['failed_extractions'] > 0:
            logger.warning("Some files failed to process. Check logs for details.")
            sys.exit(1)
        else:
            logger.info("All files processed successfully!")
            
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 