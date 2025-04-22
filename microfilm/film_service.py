"""
Film service module for handling film allocation operations.

This module provides a service layer for film-related operations,
including allocating documents to film rolls and calculating film statistics.
"""

import math
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime

from models import Project, Document, FilmAllocation, FilmRoll, FilmType, DocumentSegment

class FilmService:
    """
    Service for handling all film allocation operations.
    
    This service handles the allocation of documents to film rolls,
    calculating film statistics, and managing film numbers.
    """
    
    # Constants for film capacity
    CAPACITY_16MM = 2900  # Pages per 16mm film roll
    CAPACITY_35MM = 110   # Pages per 35mm film roll
    
    # Constants for partial roll padding
    PADDING_16MM = 150     # Padding for 16mm partial rolls
    PADDING_35MM = 150     # Padding for 35mm partial rolls
    
    def __init__(self, logger=None):
        """
        Initialize the film service.
        
        Args:
            logger: Optional logger instance.
        """
        self.logger = logger
    
    def allocate_film(self, project: Project) -> Project:
        """
        Allocate documents to film rolls based on project characteristics.
        
        This method decides whether to use the standard allocation for
        projects without oversized pages or the specialized allocation
        for projects with oversized pages.
        
        Args:
            project: The project with processed documents
            
        Returns:
            Project with film allocation information
        """
        self.logger.section("Film Allocation")
        self.logger.film_info(f"Starting film allocation for project {project.archive_id}")
        
        # Log document and page counts
        self.logger.film_info(f"Total documents: {len(project.documents)}")
        self.logger.film_info(f"Total pages: {project.total_pages}")
        self.logger.film_info(f"Total pages with references: {project.total_pages_with_refs}")
        
        # Check if we have any documents to allocate
        if not project.documents:
            self.logger.film_warning("No documents to allocate")
            # Create an empty film allocation to prevent errors
            project.film_allocation = FilmAllocation(
                archive_id=project.archive_id,
                project_name=project.project_folder_name
            )
            return project
        
        # Create film allocation based on whether there are oversized pages
        if project.has_oversized:
            self.logger.film_info("Project has oversized pages, using specialized allocation")
            project = self._allocate_with_oversized(project)
        else:
            self.logger.film_info("Project has no oversized pages, using standard allocation")
            project = self._allocate_no_oversized(project)
        
        # Calculate and log statistics
        self._log_allocation_statistics(project.film_allocation)
        
        return project
    
    def _allocate_no_oversized(self, project: Project) -> Project:
        """
        Allocate documents to 16mm film rolls when there are no oversized pages.
        
        Args:
            project: The project with processed documents
            
        Returns:
            Project with film allocation information
        """
        self.logger.section("16MM Film Allocation - No Oversizes")
        
        # Create film allocation object
        film_allocation = FilmAllocation(
            archive_id=project.archive_id,
            project_name=project.project_folder_name
        )
        
        # Track which documents are split across rolls
        split_documents: Set[str] = set()
        
        # Sort documents alphabetically by ID
        sorted_documents = sorted(project.documents, key=lambda d: d.doc_id)
        
        self.logger.film_info(f"Processing {len(sorted_documents)} documents in alphabetical order")
        
        # Initialize the first roll
        current_roll_id = 1
        current_roll = FilmRoll(
            roll_id=current_roll_id,
            film_type=FilmType.FILM_16MM,
            capacity=self.CAPACITY_16MM,
            pages_remaining=self.CAPACITY_16MM
        )
        
        # Add roll to allocation
        film_allocation.rolls_16mm.append(current_roll)
        
        self.logger.film_info(f"Created 16mm roll {current_roll_id} with capacity {self.CAPACITY_16MM}")
        
        # Process each document in alphabetical order
        for doc_idx, document in enumerate(sorted_documents):
            # Get document pages (including references if any)
            doc_pages = document.total_pages_with_refs
            
            # Check if document exceeds roll capacity (needs splitting)
            if doc_pages > self.CAPACITY_16MM:
                self.logger.film_info(f"Document {document.doc_id} exceeds roll capacity, will be split across rolls")
                
                # Document requires splitting
                pages_left_to_allocate = doc_pages
                start_page = 1
                doc_roll_count = 0
                
                # Continue allocating pages until the entire document is allocated
                while pages_left_to_allocate > 0:
                    current_roll = film_allocation.rolls_16mm[-1]  # Get the last roll
                    
                    # Calculate how many pages can fit in the current roll
                    pages_to_allocate = min(pages_left_to_allocate, current_roll.pages_remaining)
                    
                    if pages_to_allocate > 0:
                        end_page = start_page + pages_to_allocate - 1
                        
                        # Add document segment to roll using the improved method
                        current_roll.add_document_segment(
                            doc_id=document.doc_id,
                            path=document.path,
                            pages=pages_to_allocate,
                            page_range=(start_page, end_page),
                            has_oversized=document.has_oversized
                        )
                        
                        # Update tracking variables
                        pages_left_to_allocate -= pages_to_allocate
                        start_page = end_page + 1
                        doc_roll_count += 1
                    
                    # If we need more space and there are still pages to allocate, create a new roll
                    if pages_left_to_allocate > 0:
                        # Mark the document as split
                        split_documents.add(document.doc_id)
                        current_roll.has_split_documents = True
                        
                        self.logger.film_info(f"Document {document.doc_id} needs more rolls for allocation")
                        
                        # Create a new roll
                        current_roll_id += 1
                        new_roll = FilmRoll(
                            roll_id=current_roll_id,
                            film_type=FilmType.FILM_16MM,
                            capacity=self.CAPACITY_16MM,
                            pages_remaining=self.CAPACITY_16MM
                        )
                        
                        # Add roll to allocation
                        film_allocation.rolls_16mm.append(new_roll)
                        
                        self.logger.film_info(f"Created new roll {current_roll_id} with capacity {self.CAPACITY_16MM}")
                
                # After allocating all pages, update document
                document.is_split = doc_roll_count > 1
                document.roll_count = doc_roll_count
                
                if document.is_split:
                    self.logger.film_info(f"Document {document.doc_id} is split across {doc_roll_count} rolls")
            else:
                # Normal sized document - don't split unless necessary
                current_roll = film_allocation.rolls_16mm[-1]  # Get the last roll
                
                # Check if this document fits completely in the current roll
                if doc_pages <= current_roll.pages_remaining:
                    # It fits completely - allocate it
                    current_roll.add_document_segment(
                        doc_id=document.doc_id,
                        path=document.path,
                        pages=doc_pages,
                        page_range=(1, doc_pages),
                        has_oversized=document.has_oversized
                    )
                    
                    # Document fits on a single roll
                    document.is_split = False
                    document.roll_count = 1
                else:
                    # Document doesn't fit in current roll - need to create a new roll
                    self.logger.film_info(f"Document {document.doc_id} doesn't fit in current roll, creating new roll")
                    
                    # Mark current roll as partial
                    current_roll.is_partial = True
                    current_roll.remaining_capacity = current_roll.pages_remaining
                    current_roll.usable_capacity = current_roll.pages_remaining - self.PADDING_16MM
                    
                    self.logger.film_info(f"Created partial roll {current_roll.roll_id} with {current_roll.remaining_capacity} pages remaining")
                    
                    # Create a new roll
                    current_roll_id += 1
                    new_roll = FilmRoll(
                        roll_id=current_roll_id,
                        film_type=FilmType.FILM_16MM,
                        capacity=self.CAPACITY_16MM,
                        pages_remaining=self.CAPACITY_16MM
                    )
                    
                    # Add roll to allocation
                    film_allocation.rolls_16mm.append(new_roll)
                    
                    self.logger.film_info(f"Created new roll {current_roll_id} with capacity {self.CAPACITY_16MM}")
                    
                    # Now add the document to the new roll
                    new_roll.add_document_segment(
                        doc_id=document.doc_id,
                        path=document.path,
                        pages=doc_pages,
                        page_range=(1, doc_pages),
                        has_oversized=document.has_oversized
                    )
                    
                    # Document fits on a single roll (the new one)
                    document.is_split = False
                    document.roll_count = 1
        
        # Check if the last roll is a partial roll
        if film_allocation.rolls_16mm[-1].pages_remaining > 0:
            last_roll = film_allocation.rolls_16mm[-1]
            last_roll.is_partial = True
            last_roll.remaining_capacity = last_roll.pages_remaining
            last_roll.usable_capacity = last_roll.pages_remaining - self.PADDING_16MM
            
            self.logger.film_info(f"Last roll {last_roll.roll_id} is partial with {last_roll.remaining_capacity} pages remaining")
        
        # Add detailed information about split documents
        for doc_id in split_documents:
            film_allocation.split_documents_16mm[doc_id] = []
            
            # Find all rolls containing this document
            for roll in film_allocation.rolls_16mm:
                segments = roll.get_document_segments(doc_id)
                for segment in segments:
                    film_allocation.split_documents_16mm[doc_id].append({
                        "roll": roll.roll_id,
                        "pageRange": segment.page_range,
                        "frameRange": segment.frame_range
                    })
        
        # Add information about partial rolls
        for roll in film_allocation.rolls_16mm:
            if roll.is_partial:
                film_allocation.partial_rolls_16mm.append({
                    "roll_id": roll.roll_id,
                    "remainingCapacity": roll.remaining_capacity,
                    "usableCapacity": roll.usable_capacity,
                    "isAvailable": True,
                    "creation_date": roll.creation_date
                })
        
        # Update statistics
        film_allocation.update_statistics()
        
        self.logger.film_success(f"16mm allocation complete")
        self.logger.film_info(f"Total rolls: {film_allocation.total_rolls_16mm}")
        self.logger.film_info(f"Total pages: {film_allocation.total_pages_16mm}")
        self.logger.film_info(f"Total partial rolls: {film_allocation.total_partial_rolls_16mm}")
        self.logger.film_info(f"Total split documents: {film_allocation.total_split_documents_16mm}")
        
        # Set film allocation in project
        project.film_allocation = film_allocation
        
        return project
    
    def _allocate_with_oversized(self, project: Project) -> Project:
        """
        Allocate documents to film rolls when there are oversized pages.
        Uses 16mm for all pages and 35mm for oversized pages.
        
        Args:
            project: The project with processed documents
            
        Returns:
            Project with film allocation information
        """
        self.logger.section("Film Allocation - With Oversized Pages")
        
        self.logger.film_info(f"Starting specialized allocation for project with oversized pages")
        self.logger.film_info(f"Project has {project.total_oversized} oversized pages in {project.documents_with_oversized} documents")
        
        # Create film allocation object
        film_allocation = FilmAllocation(
            archive_id=project.archive_id,
            project_name=project.project_folder_name
        )
        
        self.logger.film_info(f"Created film allocation object for project {project.archive_id}")
        self.logger.film_info(f"Proceeding with dual film allocation (16mm for all pages, 35mm for oversized)")
        
        # Allocate documents to 16mm film
        self.logger.film_info(f"Step 1: Allocating all documents to 16mm film")
        project = self._allocate_16mm_with_oversized(project, film_allocation)
        
        # Allocate oversized pages to 35mm film
        self.logger.film_info(f"Step 2: Allocating oversized pages to 35mm film")
        project = self._allocate_35mm_strict(project, film_allocation)
        
        # Ensure project has the film allocation
        project.film_allocation = film_allocation
        
        self.logger.film_success(f"Completed specialized allocation for project with oversized pages")
        
        return project
    
    def _allocate_16mm_with_oversized(self, project: Project, film_allocation: FilmAllocation) -> Project:
        """
        Allocate all documents to 16mm film when project has oversized pages.
        
        This is similar to _allocate_no_oversized but handles the complexities
        of documents with oversized pages and reference sheets.
        
        Args:
            project: The project with processed documents
            film_allocation: The film allocation to update
            
        Returns:
            Project with updated film allocation
        """
        self.logger.section("16MM Film Allocation - With Oversized Pages")
        
        self.logger.film_info(f"Allocating {len(project.documents)} documents to 16mm film")
        self.logger.film_info(f"Total regular pages: {project.total_pages}")
        self.logger.film_info(f"Total reference pages: {project.total_pages_with_refs - project.total_pages}")
        
        # Track which documents are split across rolls
        split_documents: Set[str] = set()
        
        # Sort documents alphabetically by ID
        sorted_documents = sorted(project.documents, key=lambda d: d.doc_id)
        
        # Initialize the first roll if needed
        if not film_allocation.rolls_16mm:
            current_roll_id = 1
            current_roll = FilmRoll(
                roll_id=current_roll_id,
                film_type=FilmType.FILM_16MM,
                capacity=self.CAPACITY_16MM,
                pages_remaining=self.CAPACITY_16MM
            )
            
            # Add roll to allocation
            film_allocation.rolls_16mm.append(current_roll)
            
            self.logger.film_info(f"Created 16mm roll {current_roll_id} with capacity {self.CAPACITY_16MM}")
        else:
            current_roll_id = len(film_allocation.rolls_16mm)
            current_roll = film_allocation.rolls_16mm[-1]
            
        # Process each document in alphabetical order
        for doc_idx, document in enumerate(sorted_documents):
            # Get document pages (including references if any)
            doc_pages = document.total_pages_with_refs
            
            self.logger.film_info(f"Processing document {document.doc_id} with {doc_pages} total pages (including references)")
            
            # Check if document exceeds roll capacity (needs splitting)
            if doc_pages > self.CAPACITY_16MM:
                self.logger.film_info(f"Document {document.doc_id} exceeds roll capacity, will be split across rolls")
                
                # Document requires splitting
                pages_left_to_allocate = doc_pages
                start_page = 1
                doc_roll_count = 0
                
                # Continue allocating pages until the entire document is allocated
                while pages_left_to_allocate > 0:
                    current_roll = film_allocation.rolls_16mm[-1]  # Get the last roll
                    
                    # Calculate how many pages can fit in the current roll
                    pages_to_allocate = min(pages_left_to_allocate, current_roll.pages_remaining)
                    
                    if pages_to_allocate > 0:
                        end_page = start_page + pages_to_allocate - 1
                        
                        # Add document segment to roll using the structured method
                        current_roll.add_document_segment(
                            doc_id=document.doc_id,
                            path=document.path,
                            pages=pages_to_allocate,
                            page_range=(start_page, end_page),
                            has_oversized=document.has_oversized
                        )
                        
                        self.logger.film_info(f"Added {pages_to_allocate} pages of document {document.doc_id} to roll {current_roll.roll_id}")
                        
                        # Update tracking variables
                        pages_left_to_allocate -= pages_to_allocate
                        start_page = end_page + 1
                        doc_roll_count += 1
                    
                    # If we need more space and there are still pages to allocate, create a new roll
                    if pages_left_to_allocate > 0:
                        # Mark the document as split
                        split_documents.add(document.doc_id)
                        current_roll.has_split_documents = True
                        
                        self.logger.film_info(f"Document {document.doc_id} needs more rolls for allocation, {pages_left_to_allocate} pages remaining")
                        
                        # Create a new roll
                        current_roll_id += 1
                        new_roll = FilmRoll(
                            roll_id=current_roll_id,
                            film_type=FilmType.FILM_16MM,
                            capacity=self.CAPACITY_16MM,
                            pages_remaining=self.CAPACITY_16MM
                        )
                        
                        # Add roll to allocation
                        film_allocation.rolls_16mm.append(new_roll)
                        
                        self.logger.film_info(f"Created new roll {current_roll_id} with capacity {self.CAPACITY_16MM}")
                
                # After allocating all pages, update document
                document.is_split = doc_roll_count > 1
                document.roll_count = doc_roll_count
                
                if document.is_split:
                    self.logger.film_info(f"Document {document.doc_id} is split across {doc_roll_count} rolls")
            else:
                # Normal sized document - don't split unless necessary
                current_roll = film_allocation.rolls_16mm[-1]  # Get the last roll
                
                # Check if this document fits completely in the current roll
                if doc_pages <= current_roll.pages_remaining:
                    # It fits completely - allocate it
                    current_roll.add_document_segment(
                        doc_id=document.doc_id,
                        path=document.path,
                        pages=doc_pages,
                        page_range=(1, doc_pages),
                        has_oversized=document.has_oversized
                    )
                    
                    self.logger.film_info(f"Added document {document.doc_id} with {doc_pages} pages to roll {current_roll.roll_id}")
                    
                    # Document fits on a single roll
                    document.is_split = False
                    document.roll_count = 1
                else:
                    # Document doesn't fit in current roll - need to create a new roll
                    self.logger.film_info(f"Document {document.doc_id} doesn't fit in current roll (needs {doc_pages}, {current_roll.pages_remaining} available), creating new roll")
                    
                    # Mark current roll as partial
                    current_roll.is_partial = True
                    current_roll.remaining_capacity = current_roll.pages_remaining
                    current_roll.usable_capacity = current_roll.pages_remaining - self.PADDING_16MM
                    
                    film_allocation.partial_rolls_16mm.append({
                        "roll_id": current_roll.roll_id,
                        "remainingCapacity": current_roll.remaining_capacity,
                        "usableCapacity": current_roll.usable_capacity,
                        "isAvailable": True,
                        "creation_date": current_roll.creation_date
                    })
                    
                    self.logger.film_info(f"Marked roll {current_roll.roll_id} as partial with {current_roll.remaining_capacity} pages remaining")
                    
                    # Create a new roll
                    current_roll_id += 1
                    new_roll = FilmRoll(
                        roll_id=current_roll_id,
                        film_type=FilmType.FILM_16MM,
                        capacity=self.CAPACITY_16MM,
                        pages_remaining=self.CAPACITY_16MM
                    )
                    
                    # Add roll to allocation
                    film_allocation.rolls_16mm.append(new_roll)
                    
                    self.logger.film_info(f"Created new roll {current_roll_id} with capacity {self.CAPACITY_16MM}")
                    
                    # Now add the document to the new roll
                    new_roll.add_document_segment(
                        doc_id=document.doc_id,
                        path=document.path,
                        pages=doc_pages,
                        page_range=(1, doc_pages),
                        has_oversized=document.has_oversized
                    )
                    
                    self.logger.film_info(f"Added document {document.doc_id} with {doc_pages} pages to new roll {new_roll.roll_id}")
                    
                    # Document fits on a single roll (the new one)
                    document.is_split = False
                    document.roll_count = 1
        
        # Check if the last roll is a partial roll
        if film_allocation.rolls_16mm and film_allocation.rolls_16mm[-1].pages_remaining > 0:
            last_roll = film_allocation.rolls_16mm[-1]
            
            # Only mark as partial if not already marked
            if not last_roll.is_partial:
                last_roll.is_partial = True
                last_roll.remaining_capacity = last_roll.pages_remaining
                last_roll.usable_capacity = last_roll.pages_remaining - self.PADDING_16MM
                
                film_allocation.partial_rolls_16mm.append({
                    "roll_id": last_roll.roll_id,
                    "remainingCapacity": last_roll.remaining_capacity,
                    "usableCapacity": last_roll.usable_capacity,
                    "isAvailable": True,
                    "creation_date": last_roll.creation_date
                })
                
                self.logger.film_info(f"Last roll {last_roll.roll_id} is partial with {last_roll.remaining_capacity} pages remaining")
        
        # Add detailed information about split documents
        for doc_id in split_documents:
            film_allocation.split_documents_16mm[doc_id] = []
            
            # Find all rolls containing this document
            for roll in film_allocation.rolls_16mm:
                segments = roll.get_document_segments(doc_id)
                for segment in segments:
                    film_allocation.split_documents_16mm[doc_id].append({
                        "roll": roll.roll_id,
                        "pageRange": segment.page_range,
                        "frameRange": segment.frame_range
                    })
        
        # Update statistics
        film_allocation.update_statistics()
        
        self.logger.film_success(f"16mm allocation complete with oversized support")
        self.logger.film_info(f"Total 16mm rolls: {film_allocation.total_rolls_16mm}")
        self.logger.film_info(f"Total 16mm pages: {film_allocation.total_pages_16mm}")
        self.logger.film_info(f"Total partial 16mm rolls: {film_allocation.total_partial_rolls_16mm}")
        self.logger.film_info(f"Total split documents on 16mm: {film_allocation.total_split_documents_16mm}")
        
        return project
    
    def _allocate_35mm_strict(self, project: Project, film_allocation: FilmAllocation) -> Project:
        """
        Allocate oversized pages to 35mm film in strict alphabetical order.
        Creates document allocation requests instead of rolls directly.
        
        Args:
            project: The project with processed documents
            film_allocation: The film allocation to update
            
        Returns:
            Project with updated film allocation
        """
        self.logger.section("35MM Film Allocation")
        
        # Check if there are any oversized pages
        if project.total_oversized > 0:
            self.logger.film_info(f"Found {project.total_oversized} oversized pages in {project.documents_with_oversized} documents")
            
            # Get documents with oversized pages
            oversized_docs = [doc for doc in project.documents if doc.has_oversized]
            
            # Sort documents alphabetically by ID
            sorted_oversized_docs = sorted(oversized_docs, key=lambda d: d.doc_id)
            
            self.logger.film_info(f"Processing {len(sorted_oversized_docs)} oversized documents in alphabetical order")
            
            # Initialize the document allocation requests
            film_allocation.doc_allocation_requests_35mm = []
            
            # Track which documents will need to be split across rolls
            large_docs = []
            
            # Process each document with oversized pages
            for document in sorted_oversized_docs:
                self.logger.film_info(f"Processing document {document.doc_id} with {document.total_oversized} oversized pages")
                
                # Calculate total oversized pages to allocate (including reference pages)
                total_oversized_with_refs = document.total_oversized + document.total_references
                
                self.logger.film_debug(f"Document {document.doc_id} has {document.total_oversized} oversized pages and {document.total_references} reference pages")
                
                # If document exceeds CAPACITY_35MM, it will need to be split later
                if total_oversized_with_refs > self.CAPACITY_35MM:
                    large_docs.append(document)
                    self.logger.film_info(f"Document {document.doc_id} exceeds 35mm roll capacity, will be handled as a large document")
                    continue
                
                # Create an allocation request for regular-sized document
                film_allocation.doc_allocation_requests_35mm.append({
                    "doc_id": document.doc_id,
                    "path": document.path,
                    "pages": total_oversized_with_refs,
                    "page_range": (1, total_oversized_with_refs),
                    "has_oversized": True
                })
            
            # Now handle documents that need to be split
            for document in large_docs:
                total_oversized_with_refs = document.total_oversized + document.total_references
                self.logger.film_info(f"Splitting large document {document.doc_id} with {total_oversized_with_refs} pages")
                
                # Split document into chunks that fit on a roll
                pages_left = total_oversized_with_refs
                start_page = 1
                
                while pages_left > 0:
                    # Calculate how many pages to allocate in this chunk
                    pages_to_allocate = min(pages_left, self.CAPACITY_35MM)
                    end_page = start_page + pages_to_allocate - 1
                            
                    # Create allocation request for this segment
                    film_allocation.doc_allocation_requests_35mm.append({
                        "doc_id": document.doc_id,
                        "path": document.path,
                        "pages": pages_to_allocate,
                        "page_range": (start_page, end_page),
                        "has_oversized": True
                    })
                    
                    self.logger.film_debug(f"Created allocation request for {document.doc_id} pages {start_page}-{end_page}")
                    
                    # Update for next iteration
                    pages_left -= pages_to_allocate
                    start_page = end_page + 1
            
            self.logger.film_success(f"Created {len(film_allocation.doc_allocation_requests_35mm)} allocation requests for 35mm film")
        else:
            self.logger.film_info("No oversized pages to allocate to 35mm film")
            film_allocation.doc_allocation_requests_35mm = []
        
        return project
    
    def _log_allocation_statistics(self, film_allocation: FilmAllocation) -> None:
        """
        Log detailed statistics about the film allocation.
        
        Args:
            film_allocation: The film allocation with statistics
        """
        if film_allocation is None:
            self.logger.film_warning("No film allocation to log statistics for")
            return
            
        self.logger.section("Film Allocation Statistics")
        
        # Log 16mm statistics
        self.logger.film_info("16mm Film Statistics:")
        self.logger.film_info(f"- Total rolls: {film_allocation.total_rolls_16mm}")
        self.logger.film_info(f"- Total pages: {film_allocation.total_pages_16mm}")
        self.logger.film_info(f"- Partial rolls: {film_allocation.total_partial_rolls_16mm}")
        self.logger.film_info(f"- Split documents: {film_allocation.total_split_documents_16mm}")
        
        # Log 35mm statistics if applicable
        if film_allocation.total_rolls_35mm > 0:
            self.logger.film_info("35mm Film Statistics:")
            self.logger.film_info(f"- Total rolls: {film_allocation.total_rolls_35mm}")
            self.logger.film_info(f"- Total pages: {film_allocation.total_pages_35mm}")
            self.logger.film_info(f"- Partial rolls: {film_allocation.total_partial_rolls_35mm}")
            self.logger.film_info(f"- Split documents: {film_allocation.total_split_documents_35mm}") 