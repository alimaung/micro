"""
Film number manager service for microfilm processing.

This service handles the allocation of film numbers to rolls and the
generation of blip codes for documents.
"""

import json
import logging
from datetime import datetime
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.conf import settings
from django.core.cache import cache

from microapp.models import (
    Project, Roll, TempRoll, Document, DocumentSegment,
    FilmAllocation, RollReferenceInfo, DocumentReferenceInfo,
    RangeReferenceInfo, DocumentAllocationRequest35mm, FilmType
)

# Constants for roll capacities and padding
CAPACITY_16MM = 2900
CAPACITY_35MM = 690
TEMP_ROLL_PADDING_16MM = 100
TEMP_ROLL_PADDING_35MM = 100
TEMP_ROLL_MIN_USABLE_PAGES = 150

logger = logging.getLogger(__name__)

class FilmNumberManager:
    """
    Service for handling film number allocation operations.
    
    This service is responsible for assigning film numbers to rolls
    and updating index data with film numbers and blips.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the film number manager.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.current_project = None
        self.debug = settings.DEBUG  # Add debug flag from Django settings
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug("FilmNumberManager initialized in debug mode")
    @transaction.atomic
    def allocate_film_numbers(self, project_id, project_data=None, analysis_data=None, allocation_data=None, index_data=None):
        """
        Allocate film numbers to all rolls in the project.
        
        Args:
            project_id: ID of the project
            project_data: Project data from frontend
            analysis_data: Document analysis data from frontend
            allocation_data: Film allocation data from frontend
            index_data: Optional index data to update
            
        Returns:
            Tuple of (updated project, updated index data)
        """
        try:
            # Get basic project from database for DB operations
            project = Project.objects.get(pk=project_id)
            self.logger.info(f"Starting film number allocation for project {project.archive_id}")
            
            # Update has_oversized flag from analysis data if provided
            if analysis_data:
                # Try to extract the hasOversized flag from different possible locations
                has_oversized = False
                
                if 'analysisResults' in analysis_data:
                    has_oversized = analysis_data['analysisResults'].get('hasOversized', False)
                elif 'hasOversized' in analysis_data:
                    has_oversized = analysis_data['hasOversized']
                elif 'oversizedPages' in analysis_data and analysis_data['oversizedPages'] > 0:
                    has_oversized = True
                
                # Update project if needed
                if has_oversized != project.has_oversized:
                    self.logger.info(f"Updating project has_oversized flag from {project.has_oversized} to {has_oversized}")
                    project.has_oversized = has_oversized
                    project.save(update_fields=['has_oversized'])
            
            # If frontend data is provided, use it to reconstruct the complete project state
            if project_data and allocation_data:
                self.logger.info("Using data provided from frontend for film number allocation")
                
                # Create or update film allocation record for this project
                film_allocation, created = FilmAllocation.objects.get_or_create(
                    project=project,
                    defaults={
                        'total_rolls_16mm': allocation_data.get('allocationResults', {}).get('results', {}).get('total_rolls_16mm', 0),
                        'total_rolls_35mm': allocation_data.get('allocationResults', {}).get('results', {}).get('total_rolls_35mm', 0),
                        'total_pages_16mm': allocation_data.get('allocationResults', {}).get('results', {}).get('total_pages_16mm', 0),
                        'total_pages_35mm': allocation_data.get('allocationResults', {}).get('results', {}).get('total_pages_35mm', 0)
                    }
                )
                
                # Create rolls from allocation data if they don't exist in DB
                self._create_rolls_from_allocation_data(project, allocation_data)
                
                # If analysis data is provided and documents don't exist, create them
                if analysis_data:
                    self._create_documents_from_analysis_data(project, analysis_data)
                    
            else:
                # Check if project has a film allocation in database
                try:
                    film_allocation = project.film_allocation_info
                except FilmAllocation.DoesNotExist:
                    film_allocation = None
                    
                if not film_allocation:
                    self.logger.error("No film allocation found for project and no allocation data provided")
                    raise ValueError("No film allocation found for project")
                    
            # Store current project for document lookups
            self.current_project = project
            
            # Process 16mm rolls
            self._process_16mm_rolls(project)
            
            # Process 35mm rolls if project has oversized pages
            if project.has_oversized:
                self._process_35mm_rolls(project)
            else:
                self.logger.info(f"\033[31mNo 35mm rolls to process for project {project}\033[0m")
                
            # Update index data with film numbers if provided
            if index_data:
                updated_index = self._update_index(index_data, project)
            else:
                updated_index = None
            
            # Update film allocation statistics
            if hasattr(project, 'film_allocation_info'):
                project.film_allocation_info.update_statistics()
            
            # Mark film allocation as complete
            project.film_allocation_complete = True
            project.save()
            
            self.logger.info(f"Film number allocation completed successfully for project {project.archive_id}")
            
            return project, updated_index
            
        except Exception as e:
            self.logger.error(f"Error allocating film numbers: {str(e)}")
            # Transaction will be rolled back automatically
            raise
        finally:
            # Clear current project reference
            self.current_project = None
    
    def _process_16mm_rolls(self, project):
        """
        Process 16mm rolls for film number assignment.
        
        Args:
            project: Project with film allocation
        """
        # Get 16mm rolls that don't have film numbers yet
        rolls_16mm = Roll.objects.filter(
            project=project,
            film_type=FilmType.FILM_16MM,
            film_number__isnull=True
        )
        
        if not rolls_16mm.exists():
            self.logger.info("No 16mm rolls to process")
            return
        
        # Log statistics
        self.logger.info(f"Processing {rolls_16mm.count()} 16mm rolls")
            
        # Process each 16mm roll
        for roll in rolls_16mm:
            self._process_roll(roll, project.location_code)
    
    def _process_35mm_rolls(self, project):
        """
        Process 35mm document allocation requests in strict alphabetical order.
        
        Args:
            project: Project with film allocation
        """
        
        self.logger.info(f"\033[32mStarting 35mm roll processing for project {project.archive_id}\033[0m")
        
        # ADDED: Debug check for all 35mm rolls
        all_35mm_rolls = Roll.objects.filter(
            #project=project,
            film_type=FilmType.FILM_35MM
        )
        self.logger.info(f"\033[35mDEBUG: Found {all_35mm_rolls.count()} 35mm rolls at start of _process_35mm_rolls\033[0m")
        for r in all_35mm_rolls:
            self.logger.info(f"\033[35mDEBUG: Roll pk={r.pk}, roll_id={r.roll_id}, film_number={r.film_number}, created={r.creation_date}\033[0m")
        # Check if there are any allocation requests
        allocation_requests = DocumentAllocationRequest35mm.objects.filter(
            project=project,
            processed=False
        ).order_by('document__doc_id', 'start_page')
        
        if not allocation_requests.exists():
            self.logger.info("No 35mm document allocation requests to process")
            return
        
        # Log statistics
        self.logger.info(f"Processing {allocation_requests.count()} document requests for 35mm film")
            
        # Get location for finding existing rolls
        location = project.location
        
        # Initialize reference info container in project if it doesn't exist
        try:
            # For each roll that already exists, ensure it has reference info
            for roll in Roll.objects.filter(project=project, film_type=FilmType.FILM_35MM):
                RollReferenceInfo.objects.get_or_create(roll=roll, defaults={
                    'is_new_roll': True,
                    'last_frame_position': 1
                })
        except Exception as e:
            self.logger.error(f"Error initializing reference info: {str(e)}")
        
        # Dictionary to track rolls by film number for reuse
        film_number_to_roll = {}
        
        # Track document indices within rolls for frame numbers
        roll_doc_indices = {}
        
        # Track frame start positions for each roll
        roll_frame_positions = {}
        
        # Map to track document ID to original roll ID 
        # We'll use this to maintain consistent roll IDs from frontend data
        doc_to_roll_id = {}
        # Try to populate this map from allocation requests
        try:
            # Find the original allocation data if it's stored in the project
            cache_key = f"allocation_data_{project.pk}"
            allocation_data = cache.get(cache_key)
            
            if allocation_data and 'allocationResults' in allocation_data:
                results = allocation_data['allocationResults'].get('results', {})
                # If we have 35mm rolls in the allocation data, use those to map documents to rolls
                if 'rolls_35mm' in results:
                    for roll_data in results['rolls_35mm']:
                        roll_id = roll_data.get('roll_id')
                        if roll_id:
                            for seg in roll_data.get('document_segments', []):
                                doc_id = seg.get('doc_id')
                                if doc_id:
                                    doc_to_roll_id[doc_id] = roll_id
                                    self.logger.info(f"Mapped document {doc_id} to roll_id {roll_id} from allocation data")
        except Exception as e:
            self.logger.warning(f"Could not load allocation data for document-to-roll mapping: {str(e)}")
        
        # Process each document allocation request in order
        # This preserves the alphabetical ordering
        for doc_request in allocation_requests:
            document = doc_request.document
            doc_id = document.doc_id
            doc_pages = doc_request.pages
            doc_path = document.path
            page_range = (doc_request.start_page, doc_request.end_page)
            
            self.logger.debug(f"Processing allocation request for document {doc_id} with {doc_pages} pages")
            
            # First try to find an active roll with enough capacity
            active_roll = self._find_active_35mm_roll(doc_pages, location)
            
            if active_roll:
                # We found an existing roll with enough space
                roll_db_id, film_number, remaining_capacity = active_roll
                roll = Roll.objects.get(pk=roll_db_id)
                
                # Get or create reference info for this roll
                roll_ref_info, created = RollReferenceInfo.objects.get_or_create(
                    roll=roll,
                    defaults={'is_new_roll': False}
                )
                
                # Get the next document index for this roll
                if roll_db_id in roll_doc_indices:
                    doc_index = roll_doc_indices[roll_db_id] + 1
                    roll_doc_indices[roll_db_id] = doc_index
                else:
                    doc_index = self._get_last_document_index(roll) + 1
                    roll_doc_indices[roll_db_id] = doc_index
                
                # Get or initialize frame start position
                if roll_db_id not in roll_frame_positions:
                    # Try to find the highest frame position used
                    last_segment = DocumentSegment.objects.filter(
                        roll=roll
                    ).order_by('-end_frame').first()
                    
                    if last_segment:
                        # Use the next frame after the last segment's end frame
                        next_frame_start = last_segment.end_frame + 1
                        self.logger.debug(f"Found last segment on roll {roll_db_id} ending at frame {last_segment.end_frame}")
                        self.logger.debug(f"Next document will start at frame {next_frame_start}")
                        roll_frame_positions[roll_db_id] = next_frame_start
                    else:
                        # If no segments found, use roll_ref_info's last_frame_position
                        roll_frame_positions[roll_db_id] = roll_ref_info.last_frame_position
                
                frame_start = roll_frame_positions[roll_db_id]
                # Calculate frame_end as the last frame of this document
                frame_end = frame_start + doc_pages - 1  # Subtract 1 because end frame is inclusive

                self.logger.debug(f"Using frame position: start={frame_start}, end={frame_end} for document {doc_id}")
                
                # Generate blip with correct frame start
                blip = self._generate_blip(film_number, doc_index, frame_start)
                self.logger.debug(f"Generated start blip: {blip}")
                
                # Generate blip with frame end
                blipend = self._generate_blip(film_number, doc_index, frame_end)
                self.logger.debug(f"Generated end blip: {blipend}")
                
                # Create document segment for this allocation
                segment = DocumentSegment.objects.create(
                    document=document,
                    roll=roll,
                    pages=doc_pages,
                    start_page=page_range[0],
                    end_page=page_range[1],
                    start_frame=frame_start,
                    end_frame=frame_end,
                    document_index=doc_index,
                    has_oversized=True,
                    blip=blip,
                    blipend=blipend
                )
                
                # Store blip info in reference model
                doc_ref_info, created = DocumentReferenceInfo.objects.get_or_create(
                    document=document,
                    roll=roll,
                    defaults={'is_split': False}
                )
                
                range_ref_info = RangeReferenceInfo.objects.create(
                    document_reference=doc_ref_info,
                    range_start=page_range[0],
                    range_end=page_range[1],
                    position=RangeReferenceInfo.objects.filter(document_reference=doc_ref_info).count(),
                    frame_start=frame_start,
                    blip=blip,
                    blipend=blipend
                )
                
                # Update roll usage
                roll.pages_used += doc_pages
                roll.pages_remaining -= doc_pages
                roll.save()
                
                # Update reference info
                roll_ref_info.last_frame_position = frame_end + 1
                roll_ref_info.last_blipend = blipend
                roll_ref_info.save()
                
                self.logger.info(f"Added document {doc_id} with {doc_pages} pages to existing 35mm roll {film_number}")
                
                # Update frame position for next document
                roll_frame_positions[roll_db_id] = frame_end + 1
                self.logger.debug(f"Updated frame position for roll {roll_db_id} to {roll_frame_positions[roll_db_id]}")
                
                # Mark request as processed
                doc_request.processed = True
                doc_request.save()
            else:
                # No existing roll with enough space, create a new roll
                self.logger.info(f"No active roll found for document {doc_id}, creating new roll")
                
                # Get a new film number
                film_number = self._get_next_film_number(project.location_code)
                
                # Try to find the original roll_id from our mapping
                roll_id_to_use = doc_to_roll_id.get(doc_id)
                if roll_id_to_use is None:
                    # If no mapping exists, use 1 as default
                    self.logger.info(f"No original roll_id found for document {doc_id}, using default roll_id=1")
                    roll_id_to_use = 1
                else:
                    self.logger.info(f"Using original roll_id={roll_id_to_use} for document {doc_id} from allocation data")
                
                # Create a new roll
                roll = Roll.objects.create(
                    project=project,
                    roll_id=roll_id_to_use,  # Use the original roll_id from allocation data when possible
                    film_number=film_number,
                    film_type=FilmType.FILM_35MM,
                    capacity=CAPACITY_35MM,
                    pages_used=doc_pages,
                    pages_remaining=CAPACITY_35MM - doc_pages,
                    status="active",
                    film_number_source="new"
                )
                
                # Create reference info for this roll
                roll_ref_info = RollReferenceInfo.objects.create(
                    roll=roll,
                    is_new_roll=True,
                    last_frame_position=1
                )
                
                # Initialize doc index
                doc_index = 1
                roll_doc_indices[roll.pk] = doc_index
                
                # Initialize frame position
                frame_start = 1
                frame_end = frame_start + doc_pages - 1
                roll_frame_positions[roll.pk] = frame_start
                
                # Generate blips
                blip = self._generate_blip(film_number, doc_index, frame_start)
                blipend = self._generate_blip(film_number, doc_index, frame_end)
                
                # Create document segment
                segment = DocumentSegment.objects.create(
                    document=document,
                    roll=roll,
                    pages=doc_pages,
                    start_page=page_range[0],
                    end_page=page_range[1],
                    start_frame=frame_start,
                    end_frame=frame_end,
                    document_index=doc_index,
                    has_oversized=True,
                    blip=blip,
                    blipend=blipend
                )
                
                # Create reference info
                doc_ref_info = DocumentReferenceInfo.objects.create(
                    document=document,
                    roll=roll,
                    is_split=False
                )
                
                range_ref_info = RangeReferenceInfo.objects.create(
                    document_reference=doc_ref_info,
                    range_start=page_range[0],
                    range_end=page_range[1],
                    position=0,
                    frame_start=frame_start,
                    blip=blip,
                    blipend=blipend
                )
                
                # Update reference info
                roll_ref_info.last_frame_position = frame_end + 1
                roll_ref_info.last_blipend = blipend
                roll_ref_info.save()
                
                self.logger.info(f"Created new 35mm roll {film_number} and added document {doc_id}")
                
                # Update frame position for next document
                roll_frame_positions[roll.pk] = frame_end + 1
                
                # Mark request as processed
                doc_request.processed = True
                doc_request.save()
                
    def _process_roll(self, roll, location_code):
        """
        Process a single roll for film number assignment.
        Used for 16mm rolls.
        
        Args:
            roll: Roll to process
            location_code: Location code for film number
        """
        # Skip if film number already assigned
        if roll.film_number:
            self.logger.debug(f"Roll {roll.roll_id} already has film number {roll.film_number}")
            return
        
        # Skip 35mm rolls as they are handled in _process_35mm_rolls
        if roll.film_type == FilmType.FILM_35MM:
            self.logger.debug(f"Skipping 35mm roll {roll.roll_id} - handled separately")
            return
        
        # Check if this is a partial roll
        if roll.is_partial:
            self.logger.info("\033[31mProcessing partial roll\033[0m")
            # Try to find a suitable temp roll
            temp_roll = self._find_suitable_temp_roll(roll.pages_used, roll.film_type)
            self.logger.info(f"\033[31mtemp roll: {temp_roll}\033[0m")
            if temp_roll:
                temp_roll_id, source_roll_id, usable_capacity = temp_roll
                temp_roll_obj = TempRoll.objects.get(pk=temp_roll_id)
                
                # Get new film number
                film_number = self._get_next_film_number(location_code)
                self.logger.info(f"Processing partial roll with film number: {film_number}")
                
                # Update roll with film number
                roll.film_number = film_number
                roll.source_temp_roll = temp_roll_obj
                roll.film_number_source = "temp_roll"
                
                # IMPORTANT FIX: Set the roll's capacity to the temp roll's usable capacity
                # instead of using the total capacity
                roll.capacity = temp_roll_obj.usable_capacity
                self.logger.info(f"\033[31mSetting roll capacity to temp roll usable capacity: {temp_roll_obj.usable_capacity}\033[0m")
                
                # Calculate remaining capacity
                remaining_capacity = temp_roll_obj.usable_capacity - roll.pages_used
                roll.pages_remaining = remaining_capacity
                self.logger.info(f"\033[31mTemp roll usable capacity: {temp_roll_obj.usable_capacity}, Used: {roll.pages_used}, Remaining: {remaining_capacity}\033[0m")
                
                # Save roll
                roll.save()
                
                # Mark temp roll as used
                temp_roll_obj.status = "used"
                temp_roll_obj.used_by_roll = roll
                temp_roll_obj.save()
                
                # If enough remaining capacity, create new temp roll
                if roll.film_type == FilmType.FILM_16MM:
                    padding = TEMP_ROLL_PADDING_16MM
                else:
                    padding = TEMP_ROLL_PADDING_35MM
                
                usable_remainder = remaining_capacity - padding
                
                if usable_remainder >= TEMP_ROLL_MIN_USABLE_PAGES:
                    # Create new temp roll
                    self.logger.info(f"\033[31mCreating new temp roll from remainder with {remaining_capacity} usable capacity and {usable_remainder} usable capacity\033[0m")
                    new_temp_roll = self._create_temp_roll_from_remainder(
                        temp_roll_obj,
                        remaining_capacity,
                        usable_remainder,  # FIXED: Use the calculated usable remainder
                        roll
                    )
                    
                    if new_temp_roll:
                        # Update roll with created temp roll
                        roll.created_temp_roll = new_temp_roll
                        roll.save()
                else:
                    self.logger.info(f"\033[31mNot enough usable capacity remaining to create a new temp roll: {usable_remainder} < {TEMP_ROLL_MIN_USABLE_PAGES}\033[0m")
            else:
                # No suitable temp roll, assign new film number
                self.logger.info("\033[31mNo suitable temp roll, assigning new film number\033[0m")
                film_number = self._get_next_film_number(location_code)
                self.logger.info(f"\033[31mNew film number: {film_number}\033[0m")
                roll.film_number = film_number
                roll.film_number_source = "new"
                
                # Save roll
                roll.save()
                
                # If partial roll with enough capacity, create temp roll
                if roll.is_partial and roll.pages_remaining >= TEMP_ROLL_MIN_USABLE_PAGES + (TEMP_ROLL_PADDING_16MM if roll.film_type == FilmType.FILM_16MM else TEMP_ROLL_PADDING_35MM):
                    # Calculate usable capacity
                    if roll.film_type == FilmType.FILM_16MM:
                        padding = TEMP_ROLL_PADDING_16MM
                    else:
                        padding = TEMP_ROLL_PADDING_35MM
                    
                    usable_capacity = roll.pages_remaining - padding
                    
                    self.logger.info(f"\033[31mCreating temp roll with capacity={roll.pages_remaining}, usable_capacity={usable_capacity}\033[0m")
                    new_temp_roll = self._create_temp_roll(
                        roll.film_type,
                        roll.pages_remaining,
                        usable_capacity,
                        roll
                    )
                    
                    if new_temp_roll:
                        # Update roll with created temp roll
                        roll.created_temp_roll = new_temp_roll
                        roll.save()
        else:
            # Full roll, assign new film number
            film_number = self._get_next_film_number(location_code)
            roll.film_number = film_number
            roll.film_number_source = "new"
            
            # Save roll
            roll.save()
        
        # Process document segments for this roll
        self._process_document_segments(roll)
    
    def _process_document_segments(self, roll):
        """
        Process document segments for a roll, generating blips.
        
        Args:
            roll: Roll to process
        """
        # Get document segments for this roll without blips
        segments = DocumentSegment.objects.filter(
            roll=roll, 
            blip__isnull=True
        ).order_by('document_index')
        
        if not segments.exists():
            return
        
        for segment in segments:
            # Generate blip
            blip = self._generate_blip(roll.film_number, segment.document_index, segment.start_frame)
            
            # Generate end blip
            blipend = self._generate_blip(roll.film_number, segment.document_index, segment.end_frame)
            
            # Update segment with blips
            segment.blip = blip
            segment.blipend = blipend
            segment.save()
            
            self.logger.debug(f"Generated blips for document {segment.document.doc_id} on roll {roll.roll_id}")
            
            # Create or update reference info if needed
            if roll.film_type == FilmType.FILM_35MM:
                doc_ref_info, created = DocumentReferenceInfo.objects.get_or_create(
                    document=segment.document,
                    roll=roll,
                    defaults={'is_split': False}
                )
                
                range_ref_info, created = RangeReferenceInfo.objects.get_or_create(
                    document_reference=doc_ref_info,
                    range_start=segment.start_page,
                    range_end=segment.end_page,
                    defaults={
                        'position': RangeReferenceInfo.objects.filter(document_reference=doc_ref_info).count(),
                        'frame_start': segment.start_frame,
                        'blip': blip,
                        'blipend': blipend
                    }
                )
                
                if not created:
                    range_ref_info.frame_start = segment.start_frame
                    range_ref_info.blip = blip
                    range_ref_info.blipend = blipend
                    range_ref_info.save()
    
    def _generate_blip(self, film_number, doc_index, frame_start):
        """
        Generate a blip string for a document.
        
        Args:
            film_number: Film number
            doc_index: Document index on roll
            frame_start: Starting frame
            
        Returns:
            Blip string
        """
        blip = f"{film_number}-{doc_index:04d}.{frame_start:05d}"
        self.logger.debug(f"Generated blip: {blip} (doc_index={doc_index}, frame={frame_start})")
        return blip
    
    def _get_next_film_number(self, location_code):
        """
        Get the next available film number.
        
        Args:
            location_code: Location code
            
        Returns:
            Next film number
        """
        # Default prefix based on location
        prefix = location_code
        self.logger.info(f"\033[31mGetting next film number for prefix: {prefix}\033[0m")
        
        # Get the highest existing number with this prefix
        highest_roll = Roll.objects.filter(
            film_number__startswith=prefix
        ).order_by('-film_number').first()
        
        self.logger.info(f"\033[31mHighest roll: {highest_roll}\033[0m")
        if highest_roll and highest_roll.film_number:
            try:
                # Extract sequence number and increment
                sequence = int(highest_roll.film_number[len(prefix):])
                next_sequence = sequence + 1
            except (ValueError, IndexError):
                # If parsing fails, start from 1
                next_sequence = 1
        else:
            # No existing numbers, start from 1
            next_sequence = 1
        
        # Format new film number
        film_number = f"{prefix}{next_sequence:07d}"
        
        self.logger.debug(f"Generated next film number: {film_number}")
        
        return film_number
    
    def _find_suitable_temp_roll(self, pages_needed, film_type):
        """
        Find a suitable temporary roll with enough capacity.
        
        Args:
            pages_needed: Number of pages needed
            film_type: Type of film
            
        Returns:
            Tuple of (temp_roll_id, source_roll_id, usable_capacity) if found, None otherwise
        """
        temp_roll = TempRoll.objects.filter(
            film_type=film_type,
            status="available",
            usable_capacity__gte=pages_needed
        ).order_by('usable_capacity').first()
        
        self.logger.info("\033[31mProcessing _find_suitable_temp_roll\033[0m")
        
        if temp_roll:
            self.logger.debug(f"Found suitable temp roll: ID={temp_roll.pk}, capacity={temp_roll.usable_capacity}")
            return temp_roll.pk, temp_roll.source_roll_id if temp_roll.source_roll else None, temp_roll.usable_capacity
        
        return None
    
    def _create_temp_roll_from_remainder(self, original_temp_roll, remaining_capacity, usable_capacity, roll):
        """
        Create a new temporary roll from the remainder of another temp roll.
        
        Args:
            original_temp_roll: Original temp roll
            remaining_capacity: Total remaining capacity
            usable_capacity: Usable capacity (after padding)
            roll: Roll that used the original temp roll
            
        Returns:
            New temp roll if created, None otherwise
        """
        try:
            # Create new temp roll with the remaining capacity from the original temp roll
            self.logger.info(f"\033[31mCreating new temp roll with remaining_capacity={remaining_capacity}, usable_capacity={usable_capacity}\033[0m")
            
            new_temp_roll = TempRoll.objects.create(
                film_type=original_temp_roll.film_type,
                capacity=remaining_capacity,  # This is the actual remaining capacity
                usable_capacity=usable_capacity,  # This is the capacity after padding
                status="created",  # Created but not yet available until filming completes
                source_roll=roll
            )
            
            self.logger.debug(f"Created new temp roll {new_temp_roll.pk} with {usable_capacity} usable capacity")
            
            return new_temp_roll
            
        except Exception as e:
            self.logger.error(f"Error creating temp roll from remainder: {str(e)}")
            return None
    
    def _create_temp_roll(self, film_type, capacity, usable_capacity, source_roll):
        """
        Create a new temporary roll.
        
        Args:
            film_type: Type of film
            capacity: Total capacity
            usable_capacity: Usable capacity (after padding)
            source_roll: Source roll
            
        Returns:
            New temp roll if created, None otherwise
        """
        try:
            self.logger.info(f"\033[31mCreating new temp roll with capacity={capacity}, usable_capacity={usable_capacity}\033[0m")
            
            temp_roll = TempRoll.objects.create(
                film_type=film_type,
                capacity=capacity,
                usable_capacity=usable_capacity,
                status="created",  # Created but not yet available until filming completes
                source_roll=source_roll
            )
            
            self.logger.debug(f"Created temp roll {temp_roll.pk} with {usable_capacity} usable capacity")
            
            return temp_roll
            
        except Exception as e:
            self.logger.error(f"Error creating temp roll: {str(e)}")
            return None
    
    def _find_active_35mm_roll(self, pages_needed, location=None):
        """
        Find an active 35mm roll with enough capacity across all projects.
        
        Args:
            pages_needed: Number of pages needed
            location: Optional location filter
            
        Returns:
            Tuple of (roll_id, film_number, remaining_capacity) if found, None otherwise
        """
        query = Q(
            film_type=FilmType.FILM_35MM,
            status="active",
            pages_remaining__gte=pages_needed
        )
        
        # Only filter by location if specified
        if location:
            query &= Q(project__location=location)
        
        roll = Roll.objects.filter(query).order_by('-creation_date').first()
        
        if roll:
            self.logger.debug(f"Found active 35mm roll: ID={roll.pk}, film_number={roll.film_number}, remaining={roll.pages_remaining}")
            
            # Add this to debug roll history and document assignments
            segments = DocumentSegment.objects.filter(roll=roll).order_by('document_index')
            self.logger.debug(f"Roll {roll.pk} (film {roll.film_number}) has {segments.count()} existing documents")
            
            for segment in segments:
                self.logger.debug(f"  - {segment.document.doc_id}: blip={segment.blip} (pages {segment.start_page}-{segment.end_page})")
            
            return roll.pk, roll.film_number, roll.pages_remaining
        
        return None
    
    def _get_last_document_index(self, roll):
        """
        Get the highest document index used on a roll.
        
        Args:
            roll: Roll to check
            
        Returns:
            The highest document index found, or 0 if none
        """
        # Count documents on this roll to get a simple increasing index
        return DocumentSegment.objects.filter(roll=roll).count()
    
    def _update_index(self, index_data, project):
        """
        Update index data with film numbers.
        
        Args:
            index_data: Index data to update
            project: Project with film allocation
            
        Returns:
            Updated index data
        """
        self.logger.info("Updating index data with film numbers")
        
        if not index_data or "index" not in index_data:
            self.logger.error("Invalid index data structure")
            return index_data
        
        # Get the most recently created 16mm roll with a film number
        # This is likely the roll we just created and need for the index
        latest_16mm_roll = Roll.objects.filter(
            project=project,
            film_type=FilmType.FILM_16MM,
            film_number__isnull=False
        ).order_by('-creation_date').first()
        
        # Get the most recently created 35mm roll with a film number
        latest_35mm_roll = Roll.objects.filter(
            project=project,
            film_type=FilmType.FILM_35MM,
            film_number__isnull=False
        ).order_by('-creation_date').first()
        
        # Standard mapping as before (but we may not use it)
        roll_film_numbers = {}
        for roll in Roll.objects.filter(project=project).exclude(film_number__isnull=True):
            roll_film_numbers[str(roll.roll_id)] = roll.film_number
        
        self.logger.info(f"Roll film numbers: {roll_film_numbers}")
        
        # Track what we've updated
        updated_count = 0
        missing_count = 0
        
        # Update each index entry
        for entry_idx, entry in enumerate(index_data["index"]):
            if len(entry) >= 4 and entry[2]:
                roll_id, frame_start, frame_end = entry[2]
                roll_id_str = str(roll_id)
                
                self.logger.info(f"Processing index entry with roll ID: {roll_id_str}")
                
                # Get document index (use 5th element if available, default to 1)
                doc_index = entry[4] if len(entry) >= 5 else 1
                
                # Try standard lookup
                if roll_id_str in roll_film_numbers:
                    film_number = roll_film_numbers[roll_id_str]
                    
                    # Update the final_index with blip
                    blip = self._generate_blip(film_number, doc_index, frame_start)
                    entry[3] = blip
                    updated_count += 1
                    self.logger.info(f"Found film number {film_number} for roll {roll_id_str}")
                
                # If roll ID is 1 and we're likely dealing with a new 16mm roll
                elif roll_id_str == "1" and latest_16mm_roll and latest_16mm_roll.film_number:
                    film_number = latest_16mm_roll.film_number
                    
                    # Update the final_index with blip
                    blip = self._generate_blip(film_number, doc_index, frame_start)
                    entry[3] = blip
                    updated_count += 1
                    self.logger.info(f"Using latest 16mm film number {film_number} for roll {roll_id_str}")
                
                # If roll ID is 1 and we might be dealing with a 35mm roll (fallback)
                elif roll_id_str == "1" and latest_35mm_roll and latest_35mm_roll.film_number:
                    film_number = latest_35mm_roll.film_number
                    
                    # Update the final_index with blip
                    blip = self._generate_blip(film_number, doc_index, frame_start)
                    entry[3] = blip
                    updated_count += 1
                    self.logger.info(f"Using latest 35mm film number {film_number} for roll {roll_id_str}")
                
                else:
                    self.logger.warning(f"No film number found for roll {roll_id_str}")
                    missing_count += 1
        
        self.logger.info(f"Updated {updated_count} index entries with film numbers")
        if missing_count > 0:
            self.logger.warning(f"Could not update {missing_count} index entries due to missing film numbers")
        
        self.logger.info("Examining all rolls for this project:")
        for roll in Roll.objects.filter(project=project):
            self.logger.info(f"Roll pk={roll.pk}, roll_id={roll.roll_id}, film_number={roll.film_number}")
        
        return index_data

    def _create_rolls_from_allocation_data(self, project, allocation_data):
        """Create roll records from allocation data if they don't exist."""
        # Store allocation data in cache for later retrieval in _process_35mm_rolls
        try:
            # Cache the allocation data for 24 hours (86400 seconds)
            cache_key = f"allocation_data_{project.pk}"
            cache.set(cache_key, allocation_data, 86400)
            self.logger.info(f"Stored allocation data in cache with key {cache_key}")
        except Exception as e:
            self.logger.warning(f"Could not cache allocation data: {str(e)}")
        
        results = allocation_data.get('allocationResults', {}).get('results', {})
        
        # Process 16mm rolls
        for roll_data in results.get('rolls_16mm', []):
            #self.logger.info(f"\033[33mProcessing 16mm roll {roll_data}\033[0m")
            roll_id = roll_data.get('roll_id')
            film_type = FilmType.FILM_16MM
            capacity = roll_data.get('capacity', CAPACITY_16MM)
            pages_used = roll_data.get('pages_used', 0)
            pages_remaining = roll_data.get('pages_remaining', capacity - pages_used)
            
            # Check if roll already exists
            existing_roll = Roll.objects.filter(
                project=project,
                roll_id=roll_id,
                film_type=film_type
            ).first()
            
            if not existing_roll:
                # Create new roll
                roll = Roll.objects.create(
                    project=project,
                    film_type=film_type,
                    capacity=capacity,
                    pages_used=pages_used,
                    pages_remaining=pages_remaining,
                    status='active',
                    is_partial=roll_data.get('is_partial', False),
                    creation_date=datetime.now()
                )
                
                # Create document segments
                for seg_data in roll_data.get('document_segments', []):
                    # Get or create document
                    doc_id = seg_data.get('doc_id')
                    document, created = Document.objects.get_or_create(
                        project=project,
                        doc_id=doc_id,
                        defaults={
                            'path': seg_data.get('path', ''),
                            'pages': seg_data.get('pages', 0),
                            'has_oversized': seg_data.get('has_oversized', False)
                        }
                    )
                    
                    # Create segment
                    DocumentSegment.objects.create(
                        roll=roll,
                        document=document,
                        document_index=seg_data.get('document_index', 1),
                        pages=seg_data.get('pages', 0),
                        start_page=seg_data.get('page_range', [1, 1])[0],
                        end_page=seg_data.get('page_range', [1, 1])[1],
                        start_frame=seg_data.get('frame_range', [1, 1])[0],
                        end_frame=seg_data.get('frame_range', [1, 1])[1],
                        has_oversized=seg_data.get('has_oversized', False)
                    )
                
                self.logger.info(f"Created 16mm roll {roll_id} from allocation data")
        
        # For 35mm, ONLY create allocation requests, NOT actual roll objects
        doc_requests = results.get('doc_allocation_requests_35mm', [])
        self.logger.info(f"Processing {len(doc_requests)} 35mm document allocation requests from allocation data")
        
        # Additionally, also process any 35mm rolls if they exist
        # This is to ensure roll_id consistency for 35mm rolls that come from frontend
        for roll_data in results.get('rolls_35mm', []):
            # We don't create the actual roll here, just log that we received it
            # The reason is that 35mm rolls are created on-demand during the allocation process
            roll_id = roll_data.get('roll_id')
            if roll_id == 'None' or roll_id is None:
                self.logger.info(f"Received 35mm roll with None roll_id, will use numeric ID during allocation")
            else:
                self.logger.info(f"Received 35mm roll with roll_id={roll_id}")
        
        for req_data in doc_requests:
            doc_id = req_data.get('doc_id')
            document, created = Document.objects.get_or_create(
                project=project,
                doc_id=doc_id,
                defaults={
                    'path': req_data.get('path', ''),
                    'pages': req_data.get('pages', 0),
                    'has_oversized': req_data.get('has_oversized', True)
                }
            )
            
            self.logger.info(f"Processing allocation request for document {doc_id}")
            
            # Reset or create allocation request
            exists = DocumentAllocationRequest35mm.objects.filter(
                project=project,
                document=document,
                start_page=req_data.get('page_range', [1, 1])[0],
                end_page=req_data.get('page_range', [1, 1])[1]
            ).exists()
            
            if exists:
                # Reset processed flag
                DocumentAllocationRequest35mm.objects.filter(
                    project=project,
                    document=document,
                    start_page=req_data.get('page_range', [1, 1])[0],
                    end_page=req_data.get('page_range', [1, 1])[1]
                ).update(processed=False)
                self.logger.info(f"Reset existing allocation request for document {doc_id}")
            else:
                # Create new request
                DocumentAllocationRequest35mm.objects.create(
                    project=project,
                    document=document,
                    start_page=req_data.get('page_range', [1, 1])[0],
                    end_page=req_data.get('page_range', [1, 1])[1],
                    pages=req_data.get('pages', 0),
                    processed=False
                )
                self.logger.info(f"Created new allocation request for document {doc_id}")

    def _create_documents_from_analysis_data(self, project, analysis_data):
        """
        Create document records from analysis data if they don't exist.
        
        Args:
            project: Project to create documents for
            analysis_data: Analysis data from frontend
        """
        documents = analysis_data.get('analysisResults', {}).get('documents', [])
        
        for doc_data in documents:
            doc_id = doc_data.get('name')
            
            # Check if document already exists
            existing_doc = Document.objects.filter(
                project=project,
                doc_id=doc_id
            ).first()
            
            if not existing_doc:
                # Create new document
                document = Document.objects.create(
                    project=project,
                    doc_id=doc_id,
                    path=doc_data.get('path', ''),
                    pages=doc_data.get('pages', 0),
                    has_oversized=doc_data.get('hasOversized', False)
                )
                
                self.logger.info(f"Created document {doc_id} from analysis data") 

    def prepare_reference_sheet_data(self, project):
        """Prepare data for reference sheets using accurate roll information.
        
        Args:
            project: Project with oversized documents
            
        Returns:
            Dictionary mapping document IDs to lists of reference sheet data
        """
        results = {}
        
        # Use reference info if available
        if hasattr(project, 'reference_info') and project.reference_info and project.reference_info.get('documents'):
            self.logger.info(f"Using reference info model with {len(project.reference_info['documents'])} documents")
            
            for doc_id, doc_info in project.reference_info['documents'].items():
                results[doc_id] = []
                
                # Get the roll info
                roll_info = project.reference_info['rolls'].get(doc_info.roll_id)
                if not roll_info:
                    self.logger.warning(f"No roll info found for document {doc_id} roll {doc_info.roll_id}")
                    continue
                    
                # Add each range with its precise blip
                for range_info in doc_info.ranges:
                    results[doc_id].append({
                        'range': (range_info.range_start, range_info.range_end),
                        'blip_35mm': range_info.blip,
                        'film_number_35mm': roll_info.film_number,
                        'reference_position': range_info.position + 1
                    })
        else:
            # If no reference info, query database directly
            if self.logger:
                self.logger.info("No reference info model found, querying database directly")
            
            for document in project.documents.all():
                if not document.has_oversized or not hasattr(document, 'ranges') or not document.ranges.exists():
                    continue
                    
                doc_id = document.doc_id
                results[doc_id] = []
                
                # Process each range
                for i, range_data in enumerate(document.ranges.all()):
                    range_start = range_data.start_page
                    range_end = range_data.end_page
                    
                    # Get document segments for this document - specifically from 35mm rolls
                    segments = DocumentSegment.objects.filter(
                        document=document,
                        roll__film_type=FilmType.FILM_35MM,  # Explicitly filter for 35mm rolls
                        start_page__lte=range_start,
                        end_page__gte=range_end
                    )
                    
                    if segments.exists():
                        segment = segments.first()
                        film_number = segment.roll.film_number
                        blip = segment.blip
                        
                        results[doc_id].append({
                            'range': (range_start, range_end),
                            'blip_35mm': blip,
                            'film_number_35mm': film_number,
                            'reference_position': i + 1
                        })
                    else:
                        # Fallback: Try to find any 35mm segment for this document
                        any_35mm_segment = DocumentSegment.objects.filter(
                            document=document,
                            roll__film_type=FilmType.FILM_35MM
                        ).first()
                        
                        if any_35mm_segment:
                            film_number = any_35mm_segment.roll.film_number
                            blip = any_35mm_segment.blip
                            
                            # Adjust blip for specific range if needed
                            adjusted_blip = self._calculate_range_specific_blip_from_base(
                                blip, i, [], range_start, range_end
                            )
                            
                            results[doc_id].append({
                                'range': (range_start, range_end),
                                'blip_35mm': adjusted_blip,
                                'film_number_35mm': film_number,
                                'reference_position': i + 1
                            })
                
        return results
        
    def prepare_reference_sheet_data_with_frontend(self, project, film_number_results=None):
        """Prepare reference sheet data using frontend data while ensuring cross-project continuity.
        
        This method works in several stages:
        1. Process frontend data directly without relying on database
        2. Generate blips for document segments as needed
        3. Calculate range-specific blips for each document range
        
        Args:
            project: Project with oversized documents
            film_number_results: Film number results from frontend
            
        Returns:
            Dictionary mapping document IDs to lists of reference sheet data
        """
        self.logger.info(f"[TRACE] Entering prepare_reference_sheet_data_with_frontend for project {project.archive_id}")
        
        # If no frontend data, can't proceed
        if not film_number_results:
            self.logger.warning("[TRACE] No film_number_results provided, cannot proceed")
            return {}
        
        if 'results' not in film_number_results:
            self.logger.warning("[TRACE] film_number_results does not contain 'results' key, cannot proceed")
            self.logger.info(f"[TRACE] film_number_results keys: {list(film_number_results.keys())}")
            return {}
        
        # We'll build our results from frontend data
        results = {}
        document_ranges = {}
        
        # Process 35mm rolls from frontend data
        rolls_35mm = film_number_results.get('results', {}).get('rolls_35mm', [])
        self.logger.info(f"[TRACE] Processing {len(rolls_35mm)} 35mm rolls from frontend data")
        
        # Log details about the 35mm rolls
        for i, roll in enumerate(rolls_35mm):
            film_number = roll.get('film_number')
            roll_id = roll.get('roll_id')
            doc_segments = roll.get('document_segments', [])
            self.logger.info(f"[TRACE] Roll #{i+1}: film_number={film_number}, roll_id={roll_id}, segments={len(doc_segments)}")
            
            # Log details about each segment
            for j, segment in enumerate(doc_segments):
                doc_id = segment.get('doc_id')
                range_start = segment.get('start_page')
                range_end = segment.get('end_page')
                blip = segment.get('blip')
                self.logger.info(f"[TRACE]   Segment #{j+1}: doc_id={doc_id}, range={range_start}-{range_end}, blip={blip}")
        
        # Track if this is a continuation roll
        is_continuation = {}
        
        # First pass: collect all ranges for each document
        self.logger.info("[TRACE] First pass: collecting ranges for each document")
        for roll in rolls_35mm:
            film_number = roll.get('film_number')
            roll_id = roll.get('roll_id')
            
            self.logger.info(f"[TRACE] Processing roll {roll_id} with film number {film_number}")
            
            # Check if this is a continuation roll
            is_continuation[roll_id] = roll.get('is_continuation', False)
            
            # Process document segments
            doc_segments = roll.get('document_segments', [])
            for segment in doc_segments:
                doc_id = segment.get('doc_id')
                if not doc_id:
                    self.logger.warning("[TRACE] Segment missing doc_id, skipping")
                    continue
                    
                # Initialize document in results if needed
                if doc_id not in results:
                    self.logger.info(f"[TRACE] Initializing results for document {doc_id}")
                    results[doc_id] = []
                    document_ranges[doc_id] = []
                
                # Extract segment information
                range_start = segment.get('start_page', 1)
                range_end = segment.get('end_page', 1)
                document_index = segment.get('document_index', 0)
                
                self.logger.info(f"[TRACE] Adding range ({range_start}, {range_end}) for document {doc_id}")
                
                # Add range to document
                document_ranges[doc_id].append((range_start, range_end))
                
                # Get existing blip from segment or calculate one
                blip = segment.get('blip')
                self.logger.info(f"[TRACE] Found blip in segment: {blip}")
                
                # If no blip, need to generate one
                if not blip:
                    self.logger.info("[TRACE] No blip in segment, will generate one")
                    # If we're in a continuation roll, try to get the next frame position
                    if is_continuation.get(roll_id, False):
                        self.logger.info("[TRACE] This is a continuation roll, finding highest frame")
                        # Find the highest frame number in existing segments
                        max_frame = 0
                        for r in rolls_35mm:
                            if r.get('roll_id') == roll_id:
                                for s in r.get('document_segments', []):
                                    if s.get('frame_range') and len(s.get('frame_range')) >= 2:
                                        max_frame = max(max_frame, s.get('frame_range')[1])
                        
                        self.logger.info(f"[TRACE] Highest frame found: {max_frame}")
                        # Use next frame after max_frame, or default to document_index + 1
                        frame_start = max_frame + 1 if max_frame > 0 else document_index + 1
                    else:
                        # Start with document_index + 1 for new rolls
                        frame_start = document_index + 1
                        self.logger.info(f"[TRACE] Using frame_start={frame_start} for new roll")
                    
                    # Generate blip
                    blip = self._generate_blip(film_number, document_index + 1, frame_start)
                    self.logger.info(f"[TRACE] Generated blip {blip} for document {doc_id}, range {range_start}-{range_end}")
        
        # Second pass: calculate range-specific blips for each document
        self.logger.info("[TRACE] Second pass: calculating range-specific blips")
        for doc_id, ranges in document_ranges.items():
            self.logger.info(f"[TRACE] Processing ranges for document {doc_id}: {ranges}")
            
            # Look for segments in frontend data that match this document
            for roll in rolls_35mm:
                film_number = roll.get('film_number')
                
                for segment in roll.get('document_segments', []):
                    if segment.get('doc_id') == doc_id:
                        range_start = segment.get('start_page', 1)
                        range_end = segment.get('end_page', 1)
                        document_index = segment.get('document_index', 0)
                        
                        self.logger.info(f"[TRACE] Found matching segment for document {doc_id}, range {range_start}-{range_end}")
                        
                        # Check which range index this corresponds to
                        range_idx = -1
                        for i, (r_start, r_end) in enumerate(ranges):
                            if r_start == range_start and r_end == range_end:
                                range_idx = i
                                break
                        
                        if range_idx == -1:
                            self.logger.warning(f"[TRACE] Could not find range ({range_start}, {range_end}) in document ranges")
                            continue
                        
                        # Get the base blip from segment
                        base_blip = segment.get('blip')
                        self.logger.info(f"[TRACE] Base blip from segment: {base_blip}")
                        
                        # If no blip, generate base blip
                        if not base_blip:
                            frame_start = segment.get('frame_range', [1, None])[0] if segment.get('frame_range') else 1
                            base_blip = self._generate_blip(film_number, document_index + 1, frame_start)
                            self.logger.info(f"[TRACE] Generated base blip: {base_blip}")
                        
                        # Get all oversized positions from ranges
                        oversized_positions = []
                        for r_start, r_end in ranges:
                            for pos in range(r_start, r_end + 1):
                                oversized_positions.append(pos)
                        oversized_positions = sorted(oversized_positions)
                        self.logger.info(f"[TRACE] Oversized positions: {oversized_positions}")
                        
                        # Generate range-specific blip by calculating correct frame
                        # using the base blip as a starting point
                        range_blip = self._calculate_range_specific_blip_from_base(
                            base_blip, range_idx, oversized_positions, range_start, range_end
                        )
                        
                        self.logger.info(f"[TRACE] Calculated range-specific blip: base={base_blip}, result={range_blip} (range_idx={range_idx})")
                        
                        results[doc_id].append({
                            'range': (range_start, range_end),
                            'blip_35mm': range_blip,
                            'film_number_35mm': film_number,
                            'reference_position': range_idx + 1
                        })
                        self.logger.info(f"[TRACE] Added blip data for document {doc_id}, range {range_start}-{range_end}")
        
        # Check if any document has missing ranges
        self.logger.info("[TRACE] Checking for missing ranges")
        for doc_id, ranges in document_ranges.items():
            result_ranges = [data['range'] for data in results.get(doc_id, [])]
            for range_data in ranges:
                if range_data not in result_ranges:
                    self.logger.warning(f"[TRACE] Missing blip for document {doc_id}, range {range_data}")
        
        # Fall back to database approach if no results from frontend
        if not any(len(sheets) > 0 for sheets in results.values()):
            self.logger.info("[TRACE] No blip data generated from frontend, trying database as fallback")
            db_results = self.prepare_reference_sheet_data(project)
            
            # Log what was found in the database
            self.logger.info(f"[TRACE] Database fallback returned data for {len(db_results)} documents")
            if any(len(sheets) > 0 for sheets in db_results.values()):
                self.logger.info(f"[TRACE] Using database records as fallback")
                return db_results
            else:
                self.logger.warning("[TRACE] No blip data found in database either")
        
        self.logger.info(f"[TRACE] Final results contain data for {len(results)} documents")
        for doc_id, entries in results.items():
            self.logger.info(f"[TRACE] Document {doc_id} has {len(entries)} blip entries in final results")
        
        self.logger.info("[TRACE] Exiting prepare_reference_sheet_data_with_frontend")
        return results
    
    def _calculate_range_specific_blip_from_base(self, base_blip, range_idx, oversized_positions, range_start, range_end):
        """Calculate a range-specific blip from a base blip.
        
        Args:
            base_blip: Base blip for the document (e.g., 10000002-0001.00001)
            range_idx: Index of the current range within the document's ranges
            oversized_positions: List of all oversized page positions in the document
            range_start: Start page of the current range
            range_end: End page of the current range
            
        Returns:
            String with the adjusted blip
        """
        try:
            # Parse base blip
            parts = base_blip.split('-')
            film_num = parts[0]
            rest = parts[1].split('.')
            doc_index = rest[0]
            base_frame = int(rest[1])
            
            # Count oversized pages and reference sheets before this range
            os_count = 0
            ref_count = 0
            
            # Count oversized pages before this range
            for os_pos in oversized_positions:
                if os_pos < range_start:
                    os_count += 1
            
            # Each range before this one gets a reference sheet
            ref_count = range_idx
            
            # Calculate frame position: base + oversized pages + reference sheets before this range
            target_frame = base_frame + os_count + ref_count
            
            # Create range-specific blip
            range_blip = f"{film_num}-{doc_index}.{target_frame:05d}"
            
            self.logger.info(f"Calculated range-specific blip: base={base_blip}, result={range_blip} (os_count={os_count}, ref_count={ref_count})")
            
            return range_blip
            
        except Exception as e:
            self.logger.warning(f"Error calculating range blip: {str(e)}")
            return base_blip 