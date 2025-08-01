"""
Version Tracking Module

Handles versioning and audit trails for extracted data with change tracking.
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class VersionTracker:
    """Tracks versions of extracted data with audit trails."""
    
    def __init__(self, output_dir: str):
        """
        Initialize the version tracker.
        
        Args:
            output_dir: Directory to save versioned data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # File to store all extractions
        self.extractions_file = self.output_dir / "extractions.json"
        self.extractions = self._load_extractions()
    
    def _load_extractions(self) -> Dict[str, Any]:
        """
        Load existing extractions from file.
        
        Returns:
            Dictionary containing all extractions
        """
        if self.extractions_file.exists():
            try:
                with open(self.extractions_file, 'r') as f:
                    extractions = json.load(f)
                logger.info(f"Loaded {len(extractions.get('extractions', []))} existing extractions")
                return extractions
            except Exception as e:
                logger.warning(f"Failed to load existing extractions: {str(e)}")
        
        # Initialize new extractions structure
        return {
            "created_at": datetime.utcnow().isoformat(),
            "extractions": []
        }
    
    def save_extraction(
        self, 
        source_file: str, 
        data: Dict[str, Any], 
        extras: Dict[str, Any] = None
    ) -> str:
        """
        Save a new extraction with version tracking.
        
        Args:
            source_file: Name of the source PDF file
            data: Validated extracted data
            extras: Additional unmapped data
            
        Returns:
            Unique extraction ID
        """
        extraction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Create extraction record
        extraction = {
            "id": extraction_id,
            "source_file": source_file,
            "extracted_at": timestamp,
            "version": self._get_next_version(source_file),
            "data": data,
            "extras": extras or {},
            "metadata": {
                "file_size": 0,  # Could be enhanced to get actual file size
                "processing_time": 0,  # Could be enhanced to track processing time
                "llm_model": "claude-3-sonnet-20240229"  # Could be made configurable
            }
        }
        
        # Add to extractions list
        self.extractions["extractions"].append(extraction)
        
        # Save to file
        self._save_extractions()
        
        # Also save individual extraction file
        self._save_individual_extraction(extraction)
        
        logger.info(f"Saved extraction {extraction_id} for {source_file}")
        return extraction_id
    
    def _get_next_version(self, source_file: str) -> int:
        """
        Get the next version number for a source file.
        
        Args:
            source_file: Name of the source file
            
        Returns:
            Next version number
        """
        existing_versions = [
            ext["version"] for ext in self.extractions["extractions"]
            if ext["source_file"] == source_file
        ]
        
        return max(existing_versions, default=0) + 1
    
    def _save_extractions(self) -> None:
        """Save all extractions to file."""
        try:
            with open(self.extractions_file, 'w') as f:
                json.dump(self.extractions, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save extractions: {str(e)}")
            raise ValueError(f"Failed to save extractions: {str(e)}")
    
    def _save_individual_extraction(self, extraction: Dict[str, Any]) -> None:
        """
        Save individual extraction to separate file.
        
        Args:
            extraction: Extraction record to save
        """
        filename = f"{extraction['id']}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(extraction, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save individual extraction: {str(e)}")
    
    def get_extraction_history(self, source_file: str) -> List[Dict[str, Any]]:
        """
        Get version history for a source file.
        
        Args:
            source_file: Name of the source file
            
        Returns:
            List of extractions ordered by version
        """
        extractions = [
            ext for ext in self.extractions["extractions"]
            if ext["source_file"] == source_file
        ]
        
        return sorted(extractions, key=lambda x: x["version"])
    
    def get_latest_extraction(self, source_file: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest extraction for a source file.
        
        Args:
            source_file: Name of the source file
            
        Returns:
            Latest extraction or None if not found
        """
        extractions = self.get_extraction_history(source_file)
        return extractions[-1] if extractions else None
    
    def get_extraction_by_id(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get extraction by ID.
        
        Args:
            extraction_id: Unique extraction ID
            
        Returns:
            Extraction record or None if not found
        """
        for extraction in self.extractions["extractions"]:
            if extraction["id"] == extraction_id:
                return extraction
        return None
    
    def get_all_extractions(self) -> List[Dict[str, Any]]:
        """
        Get all extractions.
        
        Returns:
            List of all extractions
        """
        return self.extractions["extractions"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        extractions = self.extractions["extractions"]
        
        if not extractions:
            return {
                "total_extractions": 0,
                "unique_files": 0,
                "latest_extraction": None
            }
        
        unique_files = len(set(ext["source_file"] for ext in extractions))
        latest_extraction = max(extractions, key=lambda x: x["extracted_at"])
        
        return {
            "total_extractions": len(extractions),
            "unique_files": unique_files,
            "latest_extraction": latest_extraction["extracted_at"],
            "files_with_multiple_versions": len([
                source_file for source_file in set(ext["source_file"] for ext in extractions)
                if len(self.get_extraction_history(source_file)) > 1
            ])
        }
    
    def export_audit_trail(self, output_file: str) -> None:
        """
        Export complete audit trail to file.
        
        Args:
            output_file: Path to output file
        """
        audit_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "statistics": self.get_statistics(),
            "extractions": self.extractions["extractions"]
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(audit_data, f, indent=2)
            logger.info(f"Exported audit trail to {output_file}")
        except Exception as e:
            logger.error(f"Failed to export audit trail: {str(e)}")
            raise ValueError(f"Failed to export audit trail: {str(e)}") 