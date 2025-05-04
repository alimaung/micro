"""
Project manager service for microfilm processing.

This service handles the creation and management of microfilm projects,
coordinating between roll management and film number allocation.
"""

import logging
import json
from datetime import datetime
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.conf import settings

from microapp.models import Project, FilmAllocation
from microapp.services.roll_manager import RollManager
from microapp.services.film_number_manager import FilmNumberManager

logger = logging.getLogger(__name__)

class ProjectManager:
    """
    Service for managing microfilm projects.
    
    This service is responsible for creating and managing projects,
    and coordinating between the roll manager and film number manager.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the project manager.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.roll_manager = RollManager(logger=self.logger)
        self.film_number_manager = FilmNumberManager(logger=self.logger)
    
    @transaction.atomic
    def create_project(self, archive_id, location, name=None, notes=None, has_oversized=False):
        """
        Create a new microfilm project.
        
        Args:
            archive_id: Archive ID of the project
            location: Location code of the project
            name: Optional name of the project
            notes: Optional notes about the project
            has_oversized: Whether the project has oversized documents
            
        Returns:
            Newly created Project object
        """
        try:
            # Check if project with this archive ID already exists
            if Project.objects.filter(archive_id=archive_id).exists():
                raise ValueError(f"Project with archive ID {archive_id} already exists")
            
            # Create project
            project = Project.objects.create(
                archive_id=archive_id,
                location=location,
                location_code=location[:3].upper(),
                name=name or f"Project {archive_id}",
                notes=notes or "",
                has_oversized=has_oversized,
                status="new",
                creation_date=datetime.now()
            )
            
            # Create film allocation for this project
            FilmAllocation.objects.create(
                project=project,
                total_rolls=0,
                total_rolls_16mm=0,
                total_rolls_35mm=0
            )
            
            self.logger.info(f"Created new project {archive_id} at location {location}")
            
            return project
            
        except Exception as e:
            self.logger.error(f"Error creating project: {str(e)}")
            # Transaction will be rolled back automatically
            raise
    
    @transaction.atomic
    def process_project(self, project_id, document_data=None, allocate_film_numbers=True):
        """
        Process a project by creating rolls and optionally allocating film numbers.
        
        Args:
            project_id: ID of the project
            document_data: Optional document data to use for roll creation
            allocate_film_numbers: Whether to allocate film numbers
            
        Returns:
            Tuple of (Project, statistics dict)
        """
        try:
            project = Project.objects.get(pk=project_id)
            self.logger.info(f"Processing project {project.archive_id}")
            
            # Check if project is in the right state
            if project.status not in ["new", "in_progress"]:
                raise ValueError(f"Project is in {project.status} state, can only process new or in_progress projects")
            
            # Create rolls for this project
            rolls, roll_stats = self.roll_manager.create_rolls_for_project(project_id, document_data)
            
            # Update project status
            project.status = "in_progress"
            project.last_updated = datetime.now()
            project.save()
            
            # If allocate_film_numbers is True, allocate film numbers
            if allocate_film_numbers:
                # Allocate film numbers
                project, index_data = self.film_number_manager.allocate_film_numbers(project_id)
                
                # Update project status
                project.status = "film_numbers_allocated"
                project.last_updated = datetime.now()
                project.save()
            
            # Compile statistics
            stats = roll_stats.copy()
            stats["project_id"] = project.pk
            stats["archive_id"] = project.archive_id
            stats["status"] = project.status
            
            self.logger.info(f"Project {project.archive_id} processed successfully")
            
            return project, stats
            
        except Project.DoesNotExist:
            self.logger.error(f"Project with ID {project_id} not found")
            raise ValueError(f"Project with ID {project_id} not found")
        except Exception as e:
            self.logger.error(f"Error processing project: {str(e)}")
            # Transaction will be rolled back automatically
            raise
    
    @transaction.atomic
    def import_document_data(self, project_id, data_file_path=None, data_json=None):
        """
        Import document data for a project.
        
        Args:
            project_id: ID of the project
            data_file_path: Path to the JSON file with document data
            data_json: JSON document data as a string
            
        Returns:
            Tuple of (Project, imported document data)
        """
        if data_file_path is None and data_json is None:
            raise ValueError("Either data_file_path or data_json must be provided")
        
        try:
            project = Project.objects.get(pk=project_id)
            self.logger.info(f"Importing document data for project {project.archive_id}")
            
            # Load document data
            if data_file_path:
                with open(data_file_path, 'r') as f:
                    document_data = json.load(f)
            else:
                document_data = json.loads(data_json)
            
            # Validate document data
            if not isinstance(document_data, dict) or "documents" not in document_data:
                raise ValueError("Invalid document data format")
            
            # Update project attributes from document data if available
            if "project" in document_data:
                project_data = document_data["project"]
                
                if "name" in project_data:
                    project.name = project_data["name"]
                
                if "notes" in project_data:
                    project.notes = project_data["notes"]
                
                if "has_oversized" in project_data:
                    project.has_oversized = project_data["has_oversized"]
                
                # Save project changes
                project.save()
            
            # Count document statistics
            doc_count = len(document_data["documents"])
            regular_count = sum(1 for doc in document_data["documents"] 
                               if not doc.get("is_oversized", False))
            oversized_count = sum(1 for doc in document_data["documents"] 
                                if doc.get("is_oversized", False))
            
            total_pages = sum(doc.get("pages", 0) for doc in document_data["documents"])
            
            self.logger.info(f"Imported {doc_count} documents ({regular_count} regular, {oversized_count} oversized)")
            self.logger.info(f"Total pages: {total_pages}")
            
            return project, document_data
            
        except Project.DoesNotExist:
            self.logger.error(f"Project with ID {project_id} not found")
            raise ValueError(f"Project with ID {project_id} not found")
        except Exception as e:
            self.logger.error(f"Error importing document data: {str(e)}")
            # Transaction will be rolled back automatically
            raise
    
    @transaction.atomic
    def mark_project_as_completed(self, project_id, notes=None):
        """
        Mark a project as completed.
        
        Args:
            project_id: ID of the project
            notes: Optional completion notes
            
        Returns:
            Updated Project object
        """
        try:
            project = Project.objects.get(pk=project_id)
            
            # Check if project is in the right state
            if project.status not in ["film_numbers_allocated", "in_progress"]:
                raise ValueError(f"Project is in {project.status} state, cannot mark as completed")
            
            # Update project status
            project.status = "completed"
            project.completion_date = datetime.now()
            project.last_updated = datetime.now()
            project.completion_notes = notes or ""
            project.save()
            
            self.logger.info(f"Marked project {project.archive_id} as completed")
            
            return project
            
        except Project.DoesNotExist:
            self.logger.error(f"Project with ID {project_id} not found")
            raise ValueError(f"Project with ID {project_id} not found")
        except Exception as e:
            self.logger.error(f"Error marking project as completed: {str(e)}")
            # Transaction will be rolled back automatically
            raise
    
    def get_project_stats(self, project_id):
        """
        Get statistics for a project.
        
        Args:
            project_id: ID of the project
            
        Returns:
            Dictionary of project statistics
        """
        try:
            project = Project.objects.get(pk=project_id)
            
            # Get film allocation info
            try:
                film_allocation = project.film_allocation_info
            except FilmAllocation.DoesNotExist:
                film_allocation = None
            
            # Get roll statistics
            roll_stats = {
                "total_rolls": 0,
                "total_rolls_16mm": 0,
                "total_rolls_35mm": 0,
                "pages_used": 0,
                "pages_remaining": 0,
                "film_numbers_allocated": 0
            }
            
            if film_allocation:
                roll_stats["total_rolls"] = film_allocation.total_rolls
                roll_stats["total_rolls_16mm"] = film_allocation.total_rolls_16mm
                roll_stats["total_rolls_35mm"] = film_allocation.total_rolls_35mm
            
            # Get document statistics
            from microapp.models import Document, DocumentSegment
            
            doc_stats = {
                "total_documents": Document.objects.filter(project=project).count(),
                "regular_documents": Document.objects.filter(project=project, is_oversized=False).count(),
                "oversized_documents": Document.objects.filter(project=project, is_oversized=True).count(),
                "total_pages": Document.objects.filter(project=project).aggregate(Sum('pages'))['pages__sum'] or 0,
                "segments_allocated": DocumentSegment.objects.filter(
                    roll__project=project,
                    blip__isnull=False
                ).count()
            }
            
            # Compile all statistics
            stats = {
                "project_id": project.pk,
                "archive_id": project.archive_id,
                "name": project.name,
                "location": project.location,
                "status": project.status,
                "creation_date": project.creation_date.isoformat() if project.creation_date else None,
                "completion_date": project.completion_date.isoformat() if project.completion_date else None,
                "has_oversized": project.has_oversized,
                "film_allocation_complete": project.film_allocation_complete,
                "rolls": roll_stats,
                "documents": doc_stats
            }
            
            return stats
            
        except Project.DoesNotExist:
            self.logger.error(f"Project with ID {project_id} not found")
            raise ValueError(f"Project with ID {project_id} not found")
        except Exception as e:
            self.logger.error(f"Error getting project stats: {str(e)}")
            raise
    
    def export_allocation_data(self, project_id, include_documents=True):
        """
        Export film allocation data for a project.
        
        Args:
            project_id: ID of the project
            include_documents: Whether to include document data
            
        Returns:
            Dictionary of allocation data
        """
        try:
            project = Project.objects.get(pk=project_id)
            
            # Basic project data
            data = {
                "project": {
                    "id": project.pk,
                    "archive_id": project.archive_id,
                    "name": project.name,
                    "location": project.location,
                    "status": project.status,
                    "has_oversized": project.has_oversized,
                    "film_allocation_complete": project.film_allocation_complete
                },
                "rolls": [],
                "allocation_info": {}
            }
            
            # Get film allocation info
            try:
                film_allocation = project.film_allocation_info
                data["allocation_info"] = {
                    "total_rolls": film_allocation.total_rolls,
                    "total_rolls_16mm": film_allocation.total_rolls_16mm,
                    "total_rolls_35mm": film_allocation.total_rolls_35mm
                }
            except FilmAllocation.DoesNotExist:
                pass
            
            # Get roll data
            from microapp.models import Roll, DocumentSegment
            
            for roll in Roll.objects.filter(project=project).order_by('film_type', 'film_number'):
                roll_data = {
                    "id": roll.pk,
                    "roll_id": roll.roll_id,
                    "film_number": roll.film_number,
                    "film_type": roll.film_type,
                    "capacity": roll.capacity,
                    "pages_used": roll.pages_used,
                    "pages_remaining": roll.pages_remaining,
                    "status": roll.status,
                    "is_full": roll.is_full,
                    "is_partial": roll.is_partial
                }
                
                # Include document segments if requested
                if include_documents:
                    roll_data["documents"] = []
                    for segment in DocumentSegment.objects.filter(roll=roll).order_by('document_index'):
                        segment_data = {
                            "doc_id": segment.document.doc_id,
                            "pages": segment.pages,
                            "start_page": segment.start_page,
                            "end_page": segment.end_page,
                            "document_index": segment.document_index,
                            "start_frame": segment.start_frame,
                            "end_frame": segment.end_frame,
                            "blip": segment.blip,
                            "blipend": segment.blipend,
                            "has_oversized": segment.has_oversized
                        }
                        roll_data["documents"].append(segment_data)
                
                data["rolls"].append(roll_data)
            
            return data
            
        except Project.DoesNotExist:
            self.logger.error(f"Project with ID {project_id} not found")
            raise ValueError(f"Project with ID {project_id} not found")
        except Exception as e:
            self.logger.error(f"Error exporting allocation data: {str(e)}")
            raise 