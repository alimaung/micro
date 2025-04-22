"""
Export service module for handling microfilm export operations.

This module provides a service layer for export-related operations,
including exporting project data, document information, film allocations,
film rolls, and index data to JSON files.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from models import Project, FilmAllocation

class ExportService:
    """
    Service for handling export operations.
    
    This service handles exporting project data, document information,
    film allocations, and other relevant data to JSON files.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the export service.
        
        Args:
            logger: Optional logger instance.
        """
        self.logger = logger
    
    def export_results(self, project: Project, index_data: Optional[Dict[str, Any]] = None) -> Dict[str, Path]:
        """
        Export project results to JSON files.
        
        Args:
            project: Project with processed documents and film allocation
            index_data: Optional index data dictionary
            
        Returns:
            Dictionary with paths to exported files
        """
        if self.logger:
            self.logger.section("Exporting Results")
            self.logger.film_info("Starting export of project results")
        
        result_paths = {}
        
        try:
            # Create a data directory in the project path
            data_dir = project.project_path / ".data"
            data_dir.mkdir(exist_ok=True)
            
            if self.logger:
                self.logger.film_info(f"Creating data directory at {data_dir}")
            
            # Export project data
            project_data = {
                "archive_id": project.archive_id,
                "location": project.location,
                "location_code": project.location_code,
                "doc_type": project.doc_type,
                "project_path": str(project.project_path),
                "project_folder_name": project.project_folder_name,
                "document_folder_path": str(project.document_folder_path) if project.document_folder_path else None,
                "document_folder_name": project.document_folder_name,
                "has_oversized": project.has_oversized,
                "total_pages": project.total_pages,
                "total_pages_with_refs": project.total_pages_with_refs,
                "total_oversized": project.total_oversized,
                "documents_with_oversized": project.documents_with_oversized,
                "comlist_path": str(project.comlist_path) if project.comlist_path else None,
            }
            
            project_info_path = data_dir / f"{project.archive_id}_project_info.json"
            with open(project_info_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=4)
                
            result_paths["project_info"] = project_info_path
            if self.logger:
                self.logger.film_info(f"Exported project info to {project_info_path}")
            
            # Export document data
            documents_data = []
            for doc in project.documents:
                doc_data = {
                    "doc_id": doc.doc_id,
                    "path": str(doc.path),
                    "pages": doc.pages,
                    "has_oversized": doc.has_oversized,
                    "total_oversized": doc.total_oversized,
                    "dimensions": doc.dimensions,
                    "ranges": doc.ranges,
                    "reference_pages": doc.reference_pages,
                    "total_references": doc.total_references,
                    "is_split": doc.is_split,
                    "roll_count": doc.roll_count,
                    "com_id": doc.com_id,
                    "total_pages_with_refs": doc.total_pages_with_refs
                }
                documents_data.append(doc_data)
            
            documents_path = data_dir / f"{project.archive_id}_documents.json"
            with open(documents_path, "w", encoding="utf-8") as f:
                json.dump(documents_data, f, indent=4)
                
            result_paths["documents"] = documents_path
            if self.logger:
                self.logger.film_info(f"Exported document data to {documents_path}")
            
            # Export film allocation if available
            if project.film_allocation:
                film_allocation_data = self._serialize_film_allocation(project.film_allocation)
                
                film_allocation_path = data_dir / f"{project.archive_id}_film_allocation.json"
                with open(film_allocation_path, "w", encoding="utf-8") as f:
                    json.dump(film_allocation_data, f, indent=4)
                    
                result_paths["film_allocation"] = film_allocation_path
                if self.logger:
                    self.logger.film_info(f"Exported film allocation to {film_allocation_path}")
                
                # Export film rolls data
                film_rolls_16mm = []
                for roll in project.film_allocation.rolls_16mm:
                    roll_data = {
                        "roll_id": roll.roll_id,
                        "film_type": roll.film_type.value,
                        "capacity": roll.capacity,
                        "pages_used": roll.pages_used,
                        "pages_remaining": roll.pages_remaining,
                        "has_split_documents": roll.has_split_documents,
                        "is_partial": roll.is_partial,
                        "remaining_capacity": roll.remaining_capacity,
                        "usable_capacity": roll.usable_capacity,
                        "creation_date": roll.creation_date,
                        "document_segments": [
                            {
                                "doc_id": segment.doc_id,
                                "path": str(segment.path),
                                "pages": segment.pages,
                                "page_range": segment.page_range,
                                "frame_range": segment.frame_range,
                                "document_index": segment.document_index,
                                "has_oversized": segment.has_oversized
                            }
                            for segment in roll.document_segments
                        ],
                        "document_ids": roll.document_ids,
                        "utilization": roll.utilization
                    }
                    film_rolls_16mm.append(roll_data)
                
                film_rolls_35mm = []
                for roll in project.film_allocation.rolls_35mm:
                    roll_data = {
                        "roll_id": roll.roll_id,
                        "film_type": roll.film_type.value,
                        "capacity": roll.capacity,
                        "pages_used": roll.pages_used,
                        "pages_remaining": roll.pages_remaining,
                        "has_split_documents": roll.has_split_documents,
                        "is_partial": roll.is_partial,
                        "remaining_capacity": roll.remaining_capacity,
                        "usable_capacity": roll.usable_capacity,
                        "creation_date": roll.creation_date,
                        "document_segments": [
                            {
                                "doc_id": segment.doc_id,
                                "path": str(segment.path),
                                "pages": segment.pages,
                                "page_range": segment.page_range,
                                "frame_range": segment.frame_range,
                                "document_index": segment.document_index,
                                "has_oversized": segment.has_oversized
                            }
                            for segment in roll.document_segments
                        ],
                        "document_ids": roll.document_ids,
                        "utilization": roll.utilization
                    }
                    film_rolls_35mm.append(roll_data)
                
                film_rolls_data = {
                    "rolls_16mm": film_rolls_16mm,
                    "rolls_35mm": film_rolls_35mm,
                    "statistics": {
                        "total_rolls_16mm": project.film_allocation.total_rolls_16mm,
                        "total_pages_16mm": project.film_allocation.total_pages_16mm,
                        "total_partial_rolls_16mm": project.film_allocation.total_partial_rolls_16mm,
                        "total_split_documents_16mm": project.film_allocation.total_split_documents_16mm,
                        "total_rolls_35mm": project.film_allocation.total_rolls_35mm,
                        "total_pages_35mm": project.film_allocation.total_pages_35mm,
                        "total_partial_rolls_35mm": project.film_allocation.total_partial_rolls_35mm,
                        "total_split_documents_35mm": project.film_allocation.total_split_documents_35mm
                    }
                }
                
                film_rolls_path = data_dir / f"{project.archive_id}_film_rolls.json"
                with open(film_rolls_path, "w", encoding="utf-8") as f:
                    json.dump(film_rolls_data, f, indent=4)
                    
                result_paths["film_rolls"] = film_rolls_path
                if self.logger:
                    self.logger.film_info(f"Exported film rolls to {film_rolls_path}")
            
            # Export index data if provided
            if index_data:
                index_path = data_dir / f"{project.archive_id}_index.json"
                with open(index_path, "w", encoding="utf-8") as f:
                    json.dump(index_data, f, indent=4)
                    
                result_paths["index"] = index_path
                if self.logger:
                    self.logger.film_info(f"Exported index data to {index_path}")
            
            if self.logger:
                self.logger.film_success(f"Successfully exported all results to {data_dir}")
                
        except Exception as e:
            if self.logger:
                self.logger.film_error(f"Error exporting results: {str(e)}")
            
        return result_paths
    
    def _serialize_film_allocation(self, film_allocation: FilmAllocation) -> Dict[str, Any]:
        """
        Serialize FilmAllocation object to a dictionary.
        
        Args:
            film_allocation: FilmAllocation object
            
        Returns:
            Serialized dictionary
        """
        return {
            "archive_id": film_allocation.archive_id,
            "project_name": film_allocation.project_name,
            "split_documents_16mm": film_allocation.split_documents_16mm,
            "split_documents_35mm": film_allocation.split_documents_35mm,
            "partial_rolls_16mm": film_allocation.partial_rolls_16mm,
            "partial_rolls_35mm": film_allocation.partial_rolls_35mm,
            "total_rolls_16mm": film_allocation.total_rolls_16mm,
            "total_pages_16mm": film_allocation.total_pages_16mm,
            "total_partial_rolls_16mm": film_allocation.total_partial_rolls_16mm,
            "total_split_documents_16mm": film_allocation.total_split_documents_16mm,
            "total_rolls_35mm": film_allocation.total_rolls_35mm,
            "total_pages_35mm": film_allocation.total_pages_35mm,
            "total_partial_rolls_35mm": film_allocation.total_partial_rolls_35mm,
            "total_split_documents_35mm": film_allocation.total_split_documents_35mm,
            "creation_date": film_allocation.creation_date,
            "version": film_allocation.version
        } 