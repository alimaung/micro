"""
Roll manager service for microfilm processing.

This service handles the creation, management, and tracking of film rolls,
including capacity calculation and roll splitting.
"""

import logging
import math
from datetime import datetime
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.conf import settings

from microapp.models import (
    Project, Roll, TempRoll, Document, DocumentSegment,
    FilmAllocation, RollReferenceInfo, FilmType
)

# Constants for roll capacities
CAPACITY_16MM = 2940
CAPACITY_35MM = 690
PARTIAL_ROLL_THRESHOLD = 0.85  # 85% full is considered a partial roll

logger = logging.getLogger(__name__)

class RollManager:
    """
    Service for handling film roll operations.
    
    This service is responsible for creating, managing, and
    tracking film rolls throughout the microfilm process.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the roll manager.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    @transaction.atomic
    def create_rolls_for_project(self, project_id, document_data=None):
        """
        Create all necessary rolls for a project based on document data.
        
        Args:
            project_id: ID of the project
            document_data: Optional document data to use for roll creation
            
        Returns:
            Tuple of (list of created rolls, statistics dict)
        """
        try:
            project = Project.objects.get(pk=project_id)
            self.logger.info(f"Creating rolls for project {project.archive_id}")
            
            # Get or create film allocation for this project
            film_allocation, created = FilmAllocation.objects.get_or_create(
                project=project,
                defaults={
                    'total_rolls': 0,
                    'total_rolls_16mm': 0,
                    'total_rolls_35mm': 0
                }
            )
            
            if created:
                self.logger.info(f"Created new film allocation for project {project.archive_id}")
            
            # Process documents and create 16mm rolls
            created_rolls_16mm = self._create_16mm_rolls(project, document_data)
            
            # Process oversized documents and create 35mm rolls if needed
            created_rolls_35mm = []
            if project.has_oversized:
                created_rolls_35mm = self._create_35mm_rolls(project, document_data)
            
            # Update film allocation statistics
            film_allocation.total_rolls = Roll.objects.filter(project=project).count()
            film_allocation.total_rolls_16mm = Roll.objects.filter(project=project, film_type=FilmType.FILM_16MM).count()
            film_allocation.total_rolls_35mm = Roll.objects.filter(project=project, film_type=FilmType.FILM_35MM).count()
            film_allocation.save()
            
            # Compile statistics
            stats = {
                'total_rolls': film_allocation.total_rolls,
                'total_rolls_16mm': film_allocation.total_rolls_16mm,
                'total_rolls_35mm': film_allocation.total_rolls_35mm,
                'rolls_created': len(created_rolls_16mm) + len(created_rolls_35mm),
                'rolls_created_16mm': len(created_rolls_16mm),
                'rolls_created_35mm': len(created_rolls_35mm)
            }
            
            self.logger.info(f"Roll creation completed for project {project.archive_id}")
            self.logger.info(f"Created {stats['rolls_created']} rolls ({stats['rolls_created_16mm']} 16mm, {stats['rolls_created_35mm']} 35mm)")
            
            # Return all created rolls
            all_created_rolls = created_rolls_16mm + created_rolls_35mm
            return all_created_rolls, stats
            
        except Exception as e:
            self.logger.error(f"Error creating rolls: {str(e)}")
            # Transaction will be rolled back automatically
            raise
    
    def _create_16mm_rolls(self, project, document_data=None):
        """
        Create 16mm rolls for a project.
        
        Args:
            project: Project to create rolls for
            document_data: Optional document data to use
            
        Returns:
            List of created Roll objects
        """
        self.logger.info(f"Creating 16mm rolls for project {project.archive_id}")
        
        # If document_data is provided, use it to calculate page counts
        if document_data:
            return self._create_16mm_rolls_from_data(project, document_data)
        
        # Otherwise, use database documents
        return self._create_16mm_rolls_from_database(project)
    
    def _create_16mm_rolls_from_database(self, project):
        """
        Create 16mm rolls based on documents in the database.
        
        Args:
            project: Project to create rolls for
            
        Returns:
            List of created Roll objects
        """
        # Get regular documents (not oversized)
        documents = Document.objects.filter(
            project=project, 
            is_oversized=False
        ).order_by('doc_id')
        
        if not documents.exists():
            self.logger.info("No regular documents found for 16mm rolls")
            return []
        
        self.logger.info(f"Creating 16mm rolls for {documents.count()} regular documents")
        
        # Track created rolls
        created_rolls = []
        
        # Initialize current roll
        current_roll = None
        current_capacity = CAPACITY_16MM
        current_used = 0
        
        # Process documents in order
        for doc in documents:
            doc_pages = doc.pages
            
            # Skip documents with no pages
            if not doc_pages or doc_pages <= 0:
                self.logger.warning(f"Skipping document {doc.doc_id} with invalid page count: {doc_pages}")
                continue
                
            # Check if this document fits in the current roll
            if current_roll is None or current_used + doc_pages > current_capacity:
                # Create a new roll
                current_roll = self._create_roll(
                    project=project,
                    film_type=FilmType.FILM_16MM,
                    capacity=CAPACITY_16MM,
                    pages_used=0,
                    pages_remaining=CAPACITY_16MM,
                    is_full=False
                )
                created_rolls.append(current_roll)
                current_used = 0
                
                self.logger.debug(f"Created new 16mm roll: {current_roll.roll_id}")
            
            # Add document to the current roll
            current_used += doc_pages
            current_roll.pages_used = current_used
            current_roll.pages_remaining = current_capacity - current_used
            
            # Check if roll is now full
            is_full = current_used >= (current_capacity * PARTIAL_ROLL_THRESHOLD)
            if is_full:
                current_roll.is_full = True
                current_roll.status = "full"
            else:
                current_roll.is_partial = True
                current_roll.usable_capacity = current_capacity - current_used
            
            # Save roll state
            current_roll.save()
            
            # Create document segment for tracking
            document_index = DocumentSegment.objects.filter(roll=current_roll).count() + 1
            segment = DocumentSegment.objects.create(
                document=doc,
                roll=current_roll,
                pages=doc_pages,
                start_page=1,
                end_page=doc_pages,
                document_index=document_index,
                start_frame=None,  # Will be set during film number allocation
                end_frame=None,    # Will be set during film number allocation
                has_oversized=False
            )
            
            self.logger.debug(f"Added document {doc.doc_id} ({doc_pages} pages) to roll {current_roll.roll_id}")
            
            # If roll is full, reset for next roll
            if is_full:
                current_roll = None
        
        # Return created rolls
        return created_rolls
    
    def _create_16mm_rolls_from_data(self, project, document_data):
        """
        Create 16mm rolls based on provided document data.
        
        Args:
            project: Project to create rolls for
            document_data: Document data with page counts
            
        Returns:
            List of created Roll objects
        """
        if not document_data or "documents" not in document_data:
            self.logger.error("Invalid document data structure")
            return []
        
        # Extract regular (non-oversized) documents
        regular_docs = [doc for doc in document_data["documents"] 
                        if not doc.get("is_oversized", False)]
        
        if not regular_docs:
            self.logger.info("No regular documents found in data for 16mm rolls")
            return []
        
        self.logger.info(f"Creating 16mm rolls for {len(regular_docs)} regular documents from data")
        
        # Track created rolls
        created_rolls = []
        
        # Initialize current roll
        current_roll = None
        current_capacity = CAPACITY_16MM
        current_used = 0
        
        # Process documents in order
        for doc_data in regular_docs:
            doc_id = doc_data.get("doc_id")
            doc_pages = doc_data.get("pages", 0)
            doc_path = doc_data.get("path", "")
            
            # Skip documents with no pages
            if not doc_pages or doc_pages <= 0:
                self.logger.warning(f"Skipping document {doc_id} with invalid page count: {doc_pages}")
                continue
            
            # Try to find or create the document in the database
            doc, created = Document.objects.get_or_create(
                doc_id=doc_id,
                project=project,
                defaults={
                    "path": doc_path,
                    "pages": doc_pages,
                    "is_oversized": False
                }
            )
            
            if not created:
                # Update existing document
                doc.pages = doc_pages
                doc.path = doc_path
                doc.is_oversized = False
                doc.save()
                
            # Check if this document fits in the current roll
            if current_roll is None or current_used + doc_pages > current_capacity:
                # Create a new roll
                current_roll = self._create_roll(
                    project=project,
                    film_type=FilmType.FILM_16MM,
                    capacity=CAPACITY_16MM,
                    pages_used=0,
                    pages_remaining=CAPACITY_16MM,
                    is_full=False
                )
                created_rolls.append(current_roll)
                current_used = 0
                
                self.logger.debug(f"Created new 16mm roll: {current_roll.roll_id}")
            
            # Add document to the current roll
            current_used += doc_pages
            current_roll.pages_used = current_used
            current_roll.pages_remaining = current_capacity - current_used
            
            # Check if roll is now full
            is_full = current_used >= (current_capacity * PARTIAL_ROLL_THRESHOLD)
            if is_full:
                current_roll.is_full = True
                current_roll.status = "full"
            else:
                current_roll.is_partial = True
                current_roll.usable_capacity = current_capacity - current_used
            
            # Save roll state
            current_roll.save()
            
            # Create document segment for tracking
            document_index = DocumentSegment.objects.filter(roll=current_roll).count() + 1
            segment = DocumentSegment.objects.create(
                document=doc,
                roll=current_roll,
                pages=doc_pages,
                start_page=1,
                end_page=doc_pages,
                document_index=document_index,
                start_frame=None,  # Will be set during film number allocation
                end_frame=None,    # Will be set during film number allocation
                has_oversized=False
            )
            
            self.logger.debug(f"Added document {doc_id} ({doc_pages} pages) to roll {current_roll.roll_id}")
            
            # If roll is full, reset for next roll
            if is_full:
                current_roll = None
        
        # Return created rolls
        return created_rolls
    
    def _create_35mm_rolls(self, project, document_data=None):
        """
        Create allocation requests for 35mm rolls.
        Note: Actual 35mm rolls are created during film number allocation.
        
        Args:
            project: Project to create rolls for
            document_data: Optional document data to use
            
        Returns:
            Empty list (35mm rolls are created during allocation)
        """
        from microapp.models import DocumentAllocationRequest35mm
        
        self.logger.info(f"Creating 35mm allocation requests for project {project.archive_id}")
        
        # 35mm rolls are created during film number allocation
        # Here we just create the allocation requests
        
        # If document_data is provided, use it
        if document_data and "documents" in document_data:
            # Extract oversized documents
            oversized_docs = [doc for doc in document_data["documents"] 
                              if doc.get("is_oversized", False)]
            
            if not oversized_docs:
                self.logger.info("No oversized documents found in data for 35mm rolls")
                return []
            
            self.logger.info(f"Creating allocation requests for {len(oversized_docs)} oversized documents from data")
            
            # Process each oversized document
            for doc_data in oversized_docs:
                doc_id = doc_data.get("doc_id")
                doc_pages = doc_data.get("pages", 0)
                doc_path = doc_data.get("path", "")
                
                # Skip documents with no pages
                if not doc_pages or doc_pages <= 0:
                    self.logger.warning(f"Skipping oversized document {doc_id} with invalid page count: {doc_pages}")
                    continue
                
                # Try to find or create the document in the database
                doc, created = Document.objects.get_or_create(
                    doc_id=doc_id,
                    project=project,
                    defaults={
                        "path": doc_path,
                        "pages": doc_pages,
                        "is_oversized": True
                    }
                )
                
                if not created:
                    # Update existing document
                    doc.pages = doc_pages
                    doc.path = doc_path
                    doc.is_oversized = True
                    doc.save()
                
                # Create allocation request for this document
                request, created = DocumentAllocationRequest35mm.objects.get_or_create(
                    document=doc,
                    project=project,
                    defaults={
                        "start_page": 1,
                        "end_page": doc_pages,
                        "pages": doc_pages,
                        "processed": False
                    }
                )
                
                if not created:
                    # Update existing request
                    request.start_page = 1
                    request.end_page = doc_pages
                    request.pages = doc_pages
                    request.processed = False
                    request.save()
                
                self.logger.debug(f"Created 35mm allocation request for document {doc_id} ({doc_pages} pages)")
        else:
            # Use database documents
            # Get oversized documents
            oversized_docs = Document.objects.filter(
                project=project, 
                is_oversized=True
            ).order_by('doc_id')
            
            if not oversized_docs.exists():
                self.logger.info("No oversized documents found for 35mm rolls")
                return []
            
            self.logger.info(f"Creating allocation requests for {oversized_docs.count()} oversized documents")
            
            # Process each oversized document
            for doc in oversized_docs:
                # Create allocation request for this document
                request, created = DocumentAllocationRequest35mm.objects.get_or_create(
                    document=doc,
                    project=project,
                    defaults={
                        "start_page": 1,
                        "end_page": doc.pages,
                        "pages": doc.pages,
                        "processed": False
                    }
                )
                
                if not created:
                    # Update existing request
                    request.start_page = 1
                    request.end_page = doc.pages
                    request.pages = doc.pages
                    request.processed = False
                    request.save()
                
                self.logger.debug(f"Created 35mm allocation request for document {doc.doc_id} ({doc.pages} pages)")
        
        # No rolls are created yet - they will be created during film number allocation
        return []
    
    def _create_roll(self, project, film_type, capacity, pages_used=0, pages_remaining=None, is_full=False):
        """
        Create a new film roll.
        
        Args:
            project: Project the roll belongs to
            film_type: Type of film (16mm or 35mm)
            capacity: Total capacity of the roll
            pages_used: Number of pages already used
            pages_remaining: Number of pages remaining (calculated if None)
            is_full: Whether the roll is full
            
        Returns:
            Newly created Roll object
        """
        if pages_remaining is None:
            pages_remaining = capacity - pages_used
        
        # Calculate roll state
        is_partial = pages_used > 0 and pages_used < (capacity * PARTIAL_ROLL_THRESHOLD)
        usable_capacity = pages_remaining if is_partial else 0
        status = "full" if is_full else "active"
        
        # Create roll
        roll = Roll.objects.create(
            project=project,
            film_type=film_type,
            capacity=capacity,
            pages_used=pages_used,
            pages_remaining=pages_remaining,
            is_full=is_full,
            is_partial=is_partial,
            usable_capacity=usable_capacity,
            status=status,
            creation_date=datetime.now()
        )
        
        # Create reference info
        RollReferenceInfo.objects.create(
            roll=roll,
            is_new_roll=True,
            last_frame_position=1
        )
        
        return roll
    
    @transaction.atomic
    def mark_roll_as_scanned(self, roll_id, scanned_date=None, notes=None):
        """
        Mark a roll as scanned.
        
        Args:
            roll_id: ID of the roll
            scanned_date: Date the roll was scanned (defaults to now)
            notes: Optional notes about scanning
            
        Returns:
            Updated Roll object
        """
        try:
            roll = Roll.objects.get(pk=roll_id)
            
            if not scanned_date:
                scanned_date = datetime.now()
            
            roll.scan_date = scanned_date
            roll.scan_notes = notes or ""
            roll.status = "scanned"
            roll.save()
            
            self.logger.info(f"Marked roll {roll.roll_id} as scanned")
            
            return roll
            
        except Roll.DoesNotExist:
            self.logger.error(f"Roll with ID {roll_id} not found")
            raise ValueError(f"Roll with ID {roll_id} not found")
        except Exception as e:
            self.logger.error(f"Error marking roll as scanned: {str(e)}")
            raise
    
    @transaction.atomic
    def merge_rolls(self, source_roll_id, target_roll_id):
        """
        Merge two rolls together.
        
        Args:
            source_roll_id: ID of the source roll to merge from
            target_roll_id: ID of the target roll to merge into
            
        Returns:
            Updated target Roll object
        """
        try:
            source_roll = Roll.objects.get(pk=source_roll_id)
            target_roll = Roll.objects.get(pk=target_roll_id)
            
            # Check if rolls are of the same type
            if source_roll.film_type != target_roll.film_type:
                raise ValueError("Cannot merge rolls of different film types")
            
            # Check if target roll has capacity
            if target_roll.pages_remaining < source_roll.pages_used:
                raise ValueError("Target roll does not have enough capacity for merge")
            
            # Get segments from source roll
            segments = DocumentSegment.objects.filter(roll=source_roll)
            
            if not segments.exists():
                raise ValueError("Source roll has no document segments to merge")
            
            # Calculate target roll's highest document index
            target_highest_index = DocumentSegment.objects.filter(
                roll=target_roll
            ).aggregate(max_index=Max('document_index'))['max_index'] or 0
            
            # Move segments to target roll
            new_segments = []
            for segment in segments:
                # Create a new segment in the target roll
                new_index = target_highest_index + segment.document_index
                new_segment = DocumentSegment.objects.create(
                    document=segment.document,
                    roll=target_roll,
                    pages=segment.pages,
                    start_page=segment.start_page,
                    end_page=segment.end_page,
                    document_index=new_index,
                    start_frame=None,  # Will be recalculated in film number allocation
                    end_frame=None,    # Will be recalculated in film number allocation
                    has_oversized=segment.has_oversized,
                    blip=None,         # Will be regenerated in film number allocation
                    blipend=None       # Will be regenerated in film number allocation
                )
                new_segments.append(new_segment)
            
            # Update target roll statistics
            target_roll.pages_used += source_roll.pages_used
            target_roll.pages_remaining -= source_roll.pages_used
            target_roll.save()
            
            # Mark source roll as deprecated
            source_roll.status = "deprecated"
            source_roll.save()
            
            self.logger.info(f"Merged roll {source_roll.roll_id} into {target_roll.roll_id}")
            
            return target_roll
            
        except Roll.DoesNotExist:
            self.logger.error(f"One or both rolls not found")
            raise ValueError(f"One or both rolls not found")
        except Exception as e:
            self.logger.error(f"Error merging rolls: {str(e)}")
            raise 