"""
Document manager service for microfilm processing.

This service handles operations related to documents in the microfilm system,
such as document lookup, document splitting, and document status tracking.
"""

import logging
import os
import json
from datetime import datetime
from django.db import transaction
from django.db.models import Sum, Count, Q, Max
from django.conf import settings

from microapp.models import (
    Project, Document, DocumentSegment, DocumentReferenceInfo,
    RangeReferenceInfo, DocumentAllocationRequest35mm
)

logger = logging.getLogger(__name__)

class DocumentManager:
    """
    Service for managing documents in the microfilm system.
    
    This service is responsible for operations related to documents,
    such as lookup, splitting, and status tracking.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the document manager.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def get_document_info(self, doc_id, project_id=None):
        """
        Get comprehensive information about a document.
        
        Args:
            doc_id: ID of the document
            project_id: Optional project ID to filter by
            
        Returns:
            Dictionary with document information
        """
        try:
            # Build query
            query = Q(doc_id=doc_id)
            if project_id:
                query &= Q(project_id=project_id)
            
            # Get document
            document = Document.objects.filter(query).first()
            
            if not document:
                raise ValueError(f"Document {doc_id} not found")
            
            # Base document info
            doc_info = {
                "id": document.pk,
                "doc_id": document.doc_id,
                "project_id": document.project_id,
                "archive_id": document.project.archive_id if document.project else None,
                "path": document.path,
                "pages": document.pages,
                "is_oversized": document.is_oversized,
                "segments": [],
                "allocation_requests": []
            }
            
            # Get segments
            segments = DocumentSegment.objects.filter(document=document).order_by('roll__film_type', 'start_page')
            
            for segment in segments:
                segment_info = {
                    "segment_id": segment.pk,
                    "roll_id": segment.roll_id,
                    "film_number": segment.roll.film_number if segment.roll else None,
                    "film_type": segment.roll.film_type if segment.roll else None,
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
                doc_info["segments"].append(segment_info)
            
            # Get allocation requests for 35mm (if applicable)
            if document.is_oversized:
                allocation_requests = DocumentAllocationRequest35mm.objects.filter(
                    document=document
                ).order_by('start_page')
                
                for request in allocation_requests:
                    request_info = {
                        "request_id": request.pk,
                        "project_id": request.project_id,
                        "start_page": request.start_page,
                        "end_page": request.end_page,
                        "pages": request.pages,
                        "processed": request.processed
                    }
                    doc_info["allocation_requests"].append(request_info)
            
            # Get reference info
            doc_info["reference_info"] = self._get_reference_info(document)
            
            return doc_info
            
        except Exception as e:
            self.logger.error(f"Error getting document info: {str(e)}")
            raise
    
    def _get_reference_info(self, document):
        """
        Get reference information for a document.
        
        Args:
            document: Document instance
            
        Returns:
            Dictionary with reference information
        """
        reference_info = {
            "references": []
        }
        
        # Get document references
        doc_refs = DocumentReferenceInfo.objects.filter(document=document)
        
        for doc_ref in doc_refs:
            ref_info = {
                "id": doc_ref.pk,
                "roll_id": doc_ref.roll_id,
                "film_number": doc_ref.roll.film_number if doc_ref.roll else None,
                "is_split": doc_ref.is_split,
                "ranges": []
            }
            
            # Get ranges for this reference
            ranges = RangeReferenceInfo.objects.filter(document_reference=doc_ref).order_by('position')
            
            for range_obj in ranges:
                range_info = {
                    "id": range_obj.pk,
                    "range_start": range_obj.range_start,
                    "range_end": range_obj.range_end,
                    "position": range_obj.position,
                    "frame_start": range_obj.frame_start,
                    "blip": range_obj.blip,
                    "blipend": range_obj.blipend
                }
                ref_info["ranges"].append(range_info)
            
            reference_info["references"].append(ref_info)
        
        return reference_info
    
    def lookup_document_by_blip(self, blip):
        """
        Look up a document by its blip code.
        
        Args:
            blip: Blip code to search for
            
        Returns:
            Dictionary with document and segment information
        """
        try:
            # Try to find the segment with this blip
            segment = DocumentSegment.objects.filter(
                Q(blip=blip) | Q(blipend=blip)
            ).first()
            
            if not segment:
                # Try to find in range reference info
                range_ref = RangeReferenceInfo.objects.filter(
                    Q(blip=blip) | Q(blipend=blip)
                ).first()
                
                if not range_ref:
                    raise ValueError(f"No document found with blip {blip}")
                
                doc_ref = range_ref.document_reference
                document = doc_ref.document
                
                # Build response
                result = {
                    "found_in": "reference_info",
                    "blip": blip,
                    "document": {
                        "id": document.pk,
                        "doc_id": document.doc_id,
                        "project_id": document.project_id,
                        "archive_id": document.project.archive_id if document.project else None,
                        "path": document.path,
                        "pages": document.pages,
                        "is_oversized": document.is_oversized
                    },
                    "reference": {
                        "id": doc_ref.pk,
                        "roll_id": doc_ref.roll_id,
                        "film_number": doc_ref.roll.film_number if doc_ref.roll else None,
                        "is_split": doc_ref.is_split
                    },
                    "range": {
                        "id": range_ref.pk,
                        "range_start": range_ref.range_start,
                        "range_end": range_ref.range_end,
                        "position": range_ref.position,
                        "frame_start": range_ref.frame_start,
                        "blip": range_ref.blip,
                        "blipend": range_ref.blipend
                    }
                }
                
                return result
            
            # Get document
            document = segment.document
            
            # Build response
            result = {
                "found_in": "segment",
                "blip": blip,
                "document": {
                    "id": document.pk,
                    "doc_id": document.doc_id,
                    "project_id": document.project_id,
                    "archive_id": document.project.archive_id if document.project else None,
                    "path": document.path,
                    "pages": document.pages,
                    "is_oversized": document.is_oversized
                },
                "segment": {
                    "id": segment.pk,
                    "roll_id": segment.roll_id,
                    "film_number": segment.roll.film_number if segment.roll else None,
                    "film_type": segment.roll.film_type if segment.roll else None,
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
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error looking up document by blip: {str(e)}")
            raise
    
    @transaction.atomic
    def split_oversized_document(self, doc_id, project_id, page_ranges):
        """
        Split an oversized document into multiple allocation requests.
        
        Args:
            doc_id: ID of the document
            project_id: Project ID
            page_ranges: List of (start_page, end_page) tuples
            
        Returns:
            List of created allocation requests
        """
        try:
            # Get document
            document = Document.objects.filter(
                doc_id=doc_id,
                project_id=project_id
            ).first()
            
            if not document:
                raise ValueError(f"Document {doc_id} not found in project {project_id}")
            
            # Mark document as oversized
            document.is_oversized = True
            document.save()
            
            # Get project
            project = Project.objects.get(pk=project_id)
            
            # Make sure project has_oversized flag is set
            if not project.has_oversized:
                project.has_oversized = True
                project.save()
            
            # Delete existing allocation requests
            DocumentAllocationRequest35mm.objects.filter(
                document=document,
                project=project
            ).delete()
            
            self.logger.info(f"Splitting document {doc_id} into {len(page_ranges)} ranges")
            
            # Create new allocation requests
            created_requests = []
            
            for start_page, end_page in page_ranges:
                # Validate range
                if start_page < 1 or end_page > document.pages or start_page > end_page:
                    raise ValueError(f"Invalid page range ({start_page}-{end_page}) for document with {document.pages} pages")
                
                pages = end_page - start_page + 1
                
                # Create allocation request
                request = DocumentAllocationRequest35mm.objects.create(
                    document=document,
                    project=project,
                    start_page=start_page,
                    end_page=end_page,
                    pages=pages,
                    processed=False
                )
                
                created_requests.append(request)
                
                self.logger.debug(f"Created allocation request for pages {start_page}-{end_page} ({pages} pages)")
            
            return created_requests
            
        except Exception as e:
            self.logger.error(f"Error splitting oversized document: {str(e)}")
            # Transaction will be rolled back automatically
            raise
    
    @transaction.atomic
    def bulk_import_documents(self, project_id, document_list):
        """
        Bulk import documents for a project.
        
        Args:
            project_id: ID of the project
            document_list: List of document dictionaries
            
        Returns:
            Dictionary of statistics
        """
        try:
            # Get project
            project = Project.objects.get(pk=project_id)
            
            self.logger.info(f"Bulk importing {len(document_list)} documents for project {project.archive_id}")
            
            # Track statistics
            stats = {
                "total": len(document_list),
                "created": 0,
                "updated": 0,
                "errors": 0,
                "regular": 0,
                "oversized": 0
            }
            
            # Process each document
            for doc_data in document_list:
                try:
                    doc_id = doc_data.get("doc_id")
                    if not doc_id:
                        self.logger.warning("Skipping document with no doc_id")
                        stats["errors"] += 1
                        continue
                    
                    doc_pages = doc_data.get("pages", 0)
                    doc_path = doc_data.get("path", "")
                    is_oversized = doc_data.get("is_oversized", False)
                    
                    # Try to find or create the document
                    document, created = Document.objects.get_or_create(
                        doc_id=doc_id,
                        project=project,
                        defaults={
                            "path": doc_path,
                            "pages": doc_pages,
                            "is_oversized": is_oversized
                        }
                    )
                    
                    if created:
                        stats["created"] += 1
                    else:
                        # Update existing document
                        document.path = doc_path
                        document.pages = doc_pages
                        document.is_oversized = is_oversized
                        document.save()
                        stats["updated"] += 1
                    
                    if is_oversized:
                        stats["oversized"] += 1
                        
                        # Ensure project has_oversized flag is set
                        if not project.has_oversized:
                            project.has_oversized = True
                            project.save()
                        
                        # Create allocation request for oversized document
                        if "page_ranges" in doc_data and doc_data["page_ranges"]:
                            # Multiple page ranges
                            page_ranges = doc_data["page_ranges"]
                            self.split_oversized_document(doc_id, project_id, page_ranges)
                        else:
                            # Single full document range
                            request, created = DocumentAllocationRequest35mm.objects.get_or_create(
                                document=document,
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
                    else:
                        stats["regular"] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error importing document {doc_id}: {str(e)}")
                    stats["errors"] += 1
            
            self.logger.info(f"Imported {stats['created']} new documents, updated {stats['updated']} documents")
            self.logger.info(f"Total: {stats['regular']} regular, {stats['oversized']} oversized")
            
            return stats
            
        except Project.DoesNotExist:
            self.logger.error(f"Project with ID {project_id} not found")
            raise ValueError(f"Project with ID {project_id} not found")
        except Exception as e:
            self.logger.error(f"Error bulk importing documents: {str(e)}")
            # Transaction will be rolled back automatically
            raise
    
    def get_document_path(self, document, project=None):
        """
        Get the absolute path to a document.
        
        Args:
            document: Document instance or doc_id
            project: Optional project
            
        Returns:
            Absolute path to the document
        """
        try:
            # If document is a string, assume it's a doc_id
            if isinstance(document, str):
                doc_id = document
                
                # Build query
                query = Q(doc_id=doc_id)
                if project:
                    query &= Q(project=project)
                
                # Get document
                document = Document.objects.filter(query).first()
                
                if not document:
                    raise ValueError(f"Document {doc_id} not found")
            
            # Get document path
            doc_path = document.path
            
            # If path is relative, make it absolute
            if doc_path and not os.path.isabs(doc_path):
                # Check if DOCUMENT_ROOT is defined in settings
                if hasattr(settings, 'DOCUMENT_ROOT'):
                    doc_path = os.path.join(settings.DOCUMENT_ROOT, doc_path)
                else:
                    # Try to use project location as a hint
                    project = document.project
                    if project and project.location:
                        # Find a base path based on location
                        location_path = os.path.join('/archives', project.location)
                        if os.path.exists(location_path):
                            doc_path = os.path.join(location_path, doc_path)
            
            if not doc_path:
                raise ValueError(f"Document {document.doc_id} has no path")
            
            return doc_path
            
        except Exception as e:
            self.logger.error(f"Error getting document path: {str(e)}")
            raise 