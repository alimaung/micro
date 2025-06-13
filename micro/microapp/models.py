from django.db import models
from django.contrib.auth.models import User
import uuid
from pathlib import Path
from django.utils import timezone

class FilmType(models.TextChoices):
    """Type of film used for microfilming."""
    FILM_16MM = "16mm", "16mm"
    FILM_35MM = "35mm", "35mm"

class Project(models.Model):
    # Core project identification
    archive_id = models.CharField(max_length=20, help_text="Format: RRDxxx-yyyy")
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Project name")
    location = models.CharField(max_length=10, help_text="Location code (e.g., OU, DW)")
    doc_type = models.CharField(max_length=50, blank=True, null=True)
    
    # Path information
    project_path = models.CharField(max_length=500)
    folder_path = models.CharField(max_length=500, blank=True, null=True, help_text="Main folder path for the project")
    project_folder_name = models.CharField(max_length=255)
    pdf_folder_path = models.CharField(max_length=500, blank=True, null=True)
    comlist_path = models.CharField(max_length=500, blank=True, null=True)
    output_dir = models.CharField(max_length=500, blank=True, null=True)
    
    # Project flags
    has_pdf_folder = models.BooleanField(default=False)
    
    # Processing status
    processing_complete = models.BooleanField(default=False)
    
    # Processing settings from project setup
    retain_sources = models.BooleanField(default=True)
    add_to_database = models.BooleanField(default=True)
    
    # Process results (to be populated in later steps)
    has_oversized = models.BooleanField(default=False, null=True, blank=True)
    total_pages = models.IntegerField(null=True, blank=True)
    total_pages_with_refs = models.IntegerField(null=True, blank=True)
    
    # Timestamps and ownership
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    
    # Add fields from microfilm Project model that don't exist yet
    documents_with_oversized = models.IntegerField(default=0)
    total_oversized = models.IntegerField(default=0)
    
    # Additional metadata for film number allocation
    index_path = models.CharField(max_length=500, blank=True, null=True)
    data_dir = models.CharField(max_length=500, blank=True, null=True)
    
    # Film allocation status flags
    film_allocation_complete = models.BooleanField(default=False)
    distribution_complete = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name or self.archive_id} ({self.location})"
    
    @property
    def location_code(self):
        """
        Get the numeric location code used for film number allocation.
        Returns: "1" for OU, "2" for DW, "3" for other locations
        """
        location_map = {
            "OU": "1",
            "DW": "2"
        }
        return location_map.get(self.location, "3")
    
    @property
    def has_document_folder(self):
        """Check if a document folder has been found."""
        return bool(self.pdf_folder_path)
    
    @property
    def documents_path(self):
        """Get the path where documents are located."""
        return self.pdf_folder_path or self.project_path

class Document(models.Model):
    """Represents a PDF document in a microfilming project."""
    # Core identifying information
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    doc_id = models.CharField(max_length=100, help_text="Document ID (usually numeric, extracted from filename)")
    path = models.CharField(max_length=500, help_text="Full path to the PDF file")
    com_id = models.IntegerField(blank=True, null=True, help_text="COM ID from comlist Excel file")
    
    # Page information
    pages = models.IntegerField(default=0, help_text="Total number of pages in the document")
    
    # Oversized page information
    has_oversized = models.BooleanField(default=False, help_text="Whether document contains any oversized pages")
    total_oversized = models.IntegerField(default=0, help_text="Count of oversized pages in the document")
    total_references = models.IntegerField(default=0, help_text="Number of reference sheets for this document")
    
    # Film allocation information
    is_split = models.BooleanField(default=False, help_text="Whether document is split across film rolls")
    roll_count = models.IntegerField(default=1, help_text="Number of rolls this document spans")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['project', 'doc_id']
        ordering = ['doc_id']
    
    def __str__(self):
        return f"{self.doc_id} ({self.pages} pages)"
    
    @property
    def total_pages_with_refs(self):
        """Get the total number of pages including reference sheets."""
        return self.pages + self.total_references

class DocumentDimension(models.Model):
    """Stores detailed page dimension information for a document."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='dimensions')
    page_idx = models.IntegerField(help_text="Page index (0-based)")
    width = models.FloatField(help_text="Page width in points")
    height = models.FloatField(help_text="Page height in points")
    percent_over = models.FloatField(help_text="Percentage by which the page exceeds standard dimensions")
    
    class Meta:
        ordering = ['document', 'page_idx']
    
    def __str__(self):
        return f"Page {self.page_idx+1} of {self.document.doc_id}"

class DocumentRange(models.Model):
    """Represents a range of pages in a document (typically for oversized pages)."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='ranges')
    start_page = models.IntegerField(help_text="Start page number (1-based)")
    end_page = models.IntegerField(help_text="End page number (1-based)")
    
    class Meta:
        ordering = ['document', 'start_page']
    
    def __str__(self):
        return f"{self.document.doc_id}: pages {self.start_page}-{self.end_page}"

class ReferencePage(models.Model):
    """Stores information about reference pages inserted into a document."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='reference_pages')
    position = models.IntegerField(help_text="Position where reference sheet should be inserted")
    
    class Meta:
        ordering = ['document', 'position']
    
    def __str__(self):
        return f"Reference page at position {self.position} in {self.document.doc_id}"

class Roll(models.Model):
    """Represents a roll of microfilm with its capacity and contents."""
    # Basic roll information
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='rolls')
    roll_id = models.PositiveIntegerField(blank=True, null=True)  # Not primary key
    roll_number = models.CharField(max_length=50, blank=True, null=True, help_text="Roll number for this roll")
    film_number = models.CharField(max_length=50, blank=True, null=True, help_text="Film number assigned to this roll")
    film_type = models.CharField(max_length=10, choices=FilmType.choices, help_text="Type of film (16mm or 35mm)")
    
    # Capacity and usage
    capacity = models.IntegerField(help_text="Total capacity of the roll in pages")
    pages_used = models.IntegerField(default=0, help_text="Number of pages used on this roll")
    pages_remaining = models.IntegerField(default=0, help_text="Number of pages remaining on this roll")
    
    # Status and metadata
    status = models.CharField(max_length=20, default="active", help_text="Status of the roll (active, used, filmed, etc.)")
    has_split_documents = models.BooleanField(default=False, help_text="Whether any documents are split across rolls")
    creation_date = models.DateTimeField(auto_now_add=True)
    filmed_at = models.DateTimeField(blank=True, null=True, help_text="When this roll was filmed")
    
    # Output directory path
    output_directory = models.CharField(max_length=500, blank=True, null=True, 
                                       help_text="Path to the roll's output directory where documents are distributed")
    
    # Filming status tracking
    filming_status = models.CharField(max_length=20, choices=[
        ('ready', 'Ready to Film'),
        ('filming', 'Currently Filming'),
        ('completed', 'Filming Completed'),
        ('error', 'Filming Error'),
    ], default='ready', help_text="Current filming status of this roll")
    filming_session_id = models.CharField(max_length=100, blank=True, null=True, 
                                         help_text="ID of the current/last filming session")
    filming_started_at = models.DateTimeField(blank=True, null=True, 
                                             help_text="When filming started for this roll")
    filming_completed_at = models.DateTimeField(blank=True, null=True, 
                                               help_text="When filming was completed for this roll")
    filming_progress_percent = models.FloatField(default=0.0, 
                                                help_text="Filming progress percentage (0-100)")
    
    # Development status tracking
    development_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Development'),
        ('developing', 'Currently Developing'),
        ('completed', 'Development Completed'),
        ('failed', 'Development Failed'),
    ], default='pending', help_text="Current development status of this roll")
    development_started_at = models.DateTimeField(blank=True, null=True, 
                                                 help_text="When development started for this roll")
    development_completed_at = models.DateTimeField(blank=True, null=True, 
                                                   help_text="When development was completed for this roll")
    development_progress_percent = models.FloatField(default=0.0, 
                                                    help_text="Development progress percentage (0-100)")
    
    # Partial roll information
    is_partial = models.BooleanField(default=False, help_text="Whether this is a partial roll")
    remaining_capacity = models.IntegerField(default=0, help_text="Remaining capacity when roll becomes partial")
    usable_capacity = models.IntegerField(default=0, help_text="Usable capacity accounting for padding")
    
    # Roll source tracking (for temp rolls and roll reuse)
    film_number_source = models.CharField(max_length=20, blank=True, null=True, 
                                         help_text="Source of film number (new, temp_roll, active)")
    source_temp_roll = models.ForeignKey('TempRoll', blank=True, null=True, on_delete=models.SET_NULL, 
                                        related_name='rolls_from_this_temp')
    created_temp_roll = models.OneToOneField('TempRoll', blank=True, null=True, on_delete=models.SET_NULL, 
                                           related_name='roll_that_created_this_temp')
    
    class Meta:
        ordering = ['project', 'film_type', 'roll_id']
    
    def __str__(self):
        return f"Roll {self.roll_number or self.roll_id}: {self.film_number or 'No film number'} ({self.film_type})"
    
    @property
    def is_full(self):
        """Check if the roll is full (no remaining capacity)."""
        return self.pages_remaining <= 0
    
    @property
    def utilization(self):
        """Calculate the utilization percentage of this roll."""
        return (self.pages_used / self.capacity) * 100 if self.capacity > 0 else 0
    
    def generate_blip(self, doc_index, frame_start):
        """Generate a blip for a document on this roll."""
        if not self.film_number:
            raise ValueError("Cannot generate blip without a film number")
        
        return f"{self.film_number}-{doc_index:04d}.{frame_start:05d}"
    
    @property
    def has_output_directory(self):
        """Check if the roll has an output directory set."""
        return bool(self.output_directory)
    
    @property
    def output_directory_exists(self):
        """Check if the output directory exists on the filesystem."""
        if not self.output_directory:
            return False
        return Path(self.output_directory).exists()

class TempRoll(models.Model):
    """Represents a temporary roll with remaining capacity that can be used for future allocations."""
    # Basic information
    temp_roll_id = models.AutoField(primary_key=True)
    film_type = models.CharField(max_length=10, choices=FilmType.choices, help_text="Type of film (16mm or 35mm)")
    
    # Capacity
    capacity = models.IntegerField(help_text="Total remaining capacity in pages")
    usable_capacity = models.IntegerField(help_text="Usable capacity (after padding)")
    
    # Status and metadata
    status = models.CharField(max_length=20, default="available", help_text="Status (available, used)")
    creation_date = models.DateTimeField(auto_now_add=True)
    
    # Relationships to other rolls
    source_roll = models.ForeignKey(Roll, blank=True, null=True, on_delete=models.SET_NULL, 
                                   related_name='temp_rolls_created')
    used_by_roll = models.ForeignKey(Roll, blank=True, null=True, on_delete=models.SET_NULL,
                                    related_name='temp_rolls_used')
    
    class Meta:
        ordering = ['-creation_date']
    
    def __str__(self):
        return f"Temp Roll {self.temp_roll_id}: {self.film_type} ({self.usable_capacity} pages)"
    
    def can_accommodate(self, pages_needed):
        """Check if this temp roll can accommodate the specified number of pages."""
        return self.status == "available" and self.usable_capacity >= pages_needed

class DocumentSegment(models.Model):
    """Represents a segment of a document on a film roll."""
    # Relationships
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='segments')
    roll = models.ForeignKey(Roll, on_delete=models.CASCADE, related_name='document_segments')
    
    # Page and frame information
    pages = models.IntegerField(help_text="Number of pages in this segment")
    start_page = models.IntegerField(help_text="Start page in original document (1-based)")
    end_page = models.IntegerField(help_text="End page in original document (1-based)")
    start_frame = models.IntegerField(help_text="Start frame on film roll (1-based)")
    end_frame = models.IntegerField(help_text="End frame on film roll (1-based)")
    
    # Position and metadata
    document_index = models.IntegerField(help_text="Position of this document on the roll")
    has_oversized = models.BooleanField(default=False, help_text="Whether this segment contains oversized pages")
    
    # Blip information
    blip = models.CharField(max_length=50, blank=True, null=True, help_text="Blip code for start of document")
    blipend = models.CharField(max_length=50, blank=True, null=True, help_text="Blip code for end of document")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['roll', 'document_index']
        unique_together = ['roll', 'document_index']
    
    def __str__(self):
        return f"{self.document.doc_id} on Roll {self.roll.roll_id}: pages {self.start_page}-{self.end_page}"

class RollReferenceInfo(models.Model):
    """Stores reference information for a roll."""
    roll = models.OneToOneField(Roll, on_delete=models.CASCADE, related_name='reference_info')
    is_new_roll = models.BooleanField(default=True, help_text="Whether this is a new roll or reused")
    previous_project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL,
                                        related_name='rolls_reused_in_other_projects')
    last_blipend = models.CharField(max_length=50, blank=True, null=True, help_text="Last blipend on this roll")
    last_frame_position = models.IntegerField(default=1, help_text="Last frame position used on this roll")
    
    def __str__(self):
        return f"Reference info for Roll {self.roll.roll_id}"

class DocumentReferenceInfo(models.Model):
    """Stores reference information for a document."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='reference_info')
    roll = models.ForeignKey(Roll, on_delete=models.CASCADE, related_name='document_references')
    is_split = models.BooleanField(default=False, help_text="Whether document is split across rolls")
    
    def __str__(self):
        return f"Reference info for {self.document.doc_id}"

class RangeReferenceInfo(models.Model):
    """Stores reference information for a range of pages."""
    document_reference = models.ForeignKey(DocumentReferenceInfo, on_delete=models.CASCADE, related_name='ranges')
    range_start = models.IntegerField(help_text="Start page of range")
    range_end = models.IntegerField(help_text="End page of range")
    position = models.IntegerField(help_text="Position in document's ranges")
    frame_start = models.IntegerField(blank=True, null=True, help_text="Starting frame for this range")
    blip = models.CharField(max_length=50, blank=True, null=True, help_text="Blip code for this range")
    blipend = models.CharField(max_length=50, blank=True, null=True, help_text="End blip code for this range")
    
    class Meta:
        ordering = ['document_reference', 'position']
    
    def __str__(self):
        return f"Range {self.range_start}-{self.range_end} in {self.document_reference.document.doc_id}"

class FilmAllocation(models.Model):
    """Represents the allocation of documents to film rolls."""
    # Project relationship
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='film_allocation_info')
    
    # Statistics for 16mm
    total_rolls_16mm = models.IntegerField(default=0)
    total_pages_16mm = models.IntegerField(default=0)
    total_partial_rolls_16mm = models.IntegerField(default=0)
    total_split_documents_16mm = models.IntegerField(default=0)
    
    # Statistics for 35mm
    total_rolls_35mm = models.IntegerField(default=0)
    total_pages_35mm = models.IntegerField(default=0)
    total_partial_rolls_35mm = models.IntegerField(default=0)
    total_split_documents_35mm = models.IntegerField(default=0)
    
    # Metadata
    creation_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Film allocation for {self.project.archive_id}"
    
    def update_statistics(self):
        """Update all statistics based on related rolls."""
        # Update 16mm statistics
        rolls_16mm = self.project.rolls.filter(film_type=FilmType.FILM_16MM)
        self.total_rolls_16mm = rolls_16mm.count()
        self.total_pages_16mm = rolls_16mm.aggregate(models.Sum('pages_used'))['pages_used__sum'] or 0
        self.total_partial_rolls_16mm = rolls_16mm.filter(is_partial=True).count()
        
        # Update 35mm statistics
        rolls_35mm = self.project.rolls.filter(film_type=FilmType.FILM_35MM)
        self.total_rolls_35mm = rolls_35mm.count()
        self.total_pages_35mm = rolls_35mm.aggregate(models.Sum('pages_used'))['pages_used__sum'] or 0
        self.total_partial_rolls_35mm = rolls_35mm.filter(is_partial=True).count()
        
        # Calculate split documents
        doc_counts = DocumentSegment.objects.filter(
            roll__in=rolls_16mm
        ).values('document').annotate(
            roll_count=models.Count('roll', distinct=True)
        ).filter(roll_count__gt=1).count()
        self.total_split_documents_16mm = doc_counts
        
        doc_counts_35mm = DocumentSegment.objects.filter(
            roll__in=rolls_35mm
        ).values('document').annotate(
            roll_count=models.Count('roll', distinct=True)
        ).filter(roll_count__gt=1).count()
        self.total_split_documents_35mm = doc_counts_35mm
        
        self.save()

class DocumentAllocationRequest35mm(models.Model):
    """Tracks requests to allocate documents to 35mm film rolls."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='doc_allocation_requests_35mm')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='allocation_requests_35mm')
    pages = models.IntegerField(help_text="Number of pages to allocate")
    start_page = models.IntegerField(help_text="Start page in original document")
    end_page = models.IntegerField(help_text="End page in original document")
    processed = models.BooleanField(default=False, help_text="Whether this request has been processed")
    
    class Meta:
        ordering = ['project', 'document__doc_id', 'start_page']
    
    def __str__(self):
        return f"35mm allocation request: {self.document.doc_id} pages {self.start_page}-{self.end_page}"

class DistributionResult(models.Model):
    """Stores results from the document distribution process."""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='distribution_result')
    
    # Standard workflow results
    processed_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    output_dir = models.CharField(max_length=500, blank=True, null=True)
    
    # Oversized workflow results
    reference_sheets = models.IntegerField(default=0, help_text="Total reference sheets generated")
    documents_with_references = models.IntegerField(default=0, help_text="Documents with reference sheets")
    oversized_documents_extracted = models.IntegerField(default=0)
    processed_35mm_documents = models.IntegerField(default=0)
    copied_35mm_documents = models.IntegerField(default=0)
    processed_16mm_documents = models.IntegerField(default=0)
    copied_16mm_documents = models.IntegerField(default=0)
    
    # Process tracking
    completed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="success", 
                             choices=[("success", "Success"), 
                                      ("error", "Error"), 
                                      ("partial", "Partial Success")])
    
    def __str__(self):
        return f"Distribution results for {self.project.archive_id}"


class ReferenceSheet(models.Model):
    """Represents a reference sheet generated for oversized pages."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='reference_sheets')
    document_range = models.ForeignKey(DocumentRange, on_delete=models.CASCADE, 
                                     related_name='reference_sheet', null=True)
    
    # Range information (also stored directly for convenience)
    range_start = models.IntegerField(help_text="Start page of oversized range")
    range_end = models.IntegerField(help_text="End page of oversized range")
    
    # Reference sheet information
    path = models.CharField(max_length=500, help_text="Path to reference sheet PDF")
    blip_35mm = models.CharField(max_length=50, blank=True, null=True, 
                                help_text="Blip code for 35mm film")
    film_number_35mm = models.CharField(max_length=50, blank=True, null=True,
                                      help_text="Film number for 35mm roll")
    human_range = models.CharField(max_length=100, blank=True, null=True,
                                 help_text="Human-readable page range (e.g. '1 von 5')")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['document', 'range_start']
    
    def __str__(self):
        return f"Reference for {self.document.doc_id} pages {self.range_start}-{self.range_end}"


class ReadablePageDescription(models.Model):
    """Stores human-readable page descriptions for document ranges."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='readable_page_descriptions')
    range_index = models.IntegerField(help_text="Index of the range in document's ranges")
    description = models.CharField(max_length=100, help_text="Human-readable description e.g. '1 von 5'")
    
    class Meta:
        ordering = ['document', 'range_index']
        unique_together = ['document', 'range_index']
    
    def __str__(self):
        return f"{self.document.doc_id}: Range {self.range_index} - {self.description}"


class AdjustedRange(models.Model):
    """Maps between original document ranges and adjusted ranges after reference insertion."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='adjusted_ranges')
    original_start = models.IntegerField(help_text="Original start page")
    original_end = models.IntegerField(help_text="Original end page")
    adjusted_start = models.IntegerField(help_text="Adjusted start page after reference insertion")
    adjusted_end = models.IntegerField(help_text="Adjusted end page after reference insertion")
    
    class Meta:
        ordering = ['document', 'original_start']
    
    def __str__(self):
        return f"{self.document.doc_id}: {self.original_start}-{self.original_end} → {self.adjusted_start}-{self.adjusted_end}"


class ProcessedDocument(models.Model):
    """Tracks processed versions of documents (with references, extracted pages, etc.)"""
    DOCUMENT_TYPES = [
        ('16mm_with_refs', '16mm with references'),
        ('35mm_with_refs', '35mm with references'),
        ('extracted_oversized', 'Extracted oversized pages'),
        ('standard', 'Standard document'),
        ('split', 'Split document')
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='processed_versions')
    path = models.CharField(max_length=500, help_text="Path to processed document file")
    processing_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    
    # For split documents or specific page ranges
    start_page = models.IntegerField(null=True, blank=True, help_text="Start page if this is a document segment")
    end_page = models.IntegerField(null=True, blank=True, help_text="End page if this is a document segment")
    
    # Roll allocation information
    roll = models.ForeignKey(Roll, on_delete=models.CASCADE, related_name='processed_documents', null=True, blank=True)
    segment = models.ForeignKey(DocumentSegment, on_delete=models.CASCADE, related_name='processed_document', 
                              null=True, blank=True)
    
    # Status information
    processed_at = models.DateTimeField(auto_now_add=True)
    copied_to_output = models.BooleanField(default=False, help_text="Whether copied to output directory")
    output_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path in output directory")
    
    class Meta:
        ordering = ['document', 'processing_type', 'start_page']
    
    def __str__(self):
        if self.start_page and self.end_page:
            return f"{self.document.doc_id} ({self.processing_type}): pages {self.start_page}-{self.end_page}"
        return f"{self.document.doc_id} ({self.processing_type})"

class FilmingSession(models.Model):
    """Tracks SMA filming sessions with progress and status."""
    SESSION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
        ('terminated', 'Terminated'),
    ]
    
    WORKFLOW_STATE_CHOICES = [
        ('initialization', 'Initialization'),
        ('monitoring', 'Independent Monitoring'),
        ('advanced_finish', 'Advanced Finish'),
        ('completed', 'Completed'),
    ]
    
    # Session identification
    session_id = models.CharField(max_length=100, unique=True, help_text="Unique session identifier")
    
    # Relationships
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='filming_sessions')
    roll = models.ForeignKey(Roll, on_delete=models.CASCADE, related_name='filming_sessions', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='filming_sessions', null=True, blank=True)
    
    # Film configuration
    film_type = models.CharField(max_length=10, choices=FilmType.choices, default=FilmType.FILM_16MM, help_text="Film type (16mm or 35mm)")
    
    # Session status and workflow
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='pending')
    workflow_state = models.CharField(max_length=20, choices=WORKFLOW_STATE_CHOICES, default='initialization')
    
    # Progress tracking
    total_documents = models.IntegerField(default=0, help_text="Total documents to process")
    processed_documents = models.IntegerField(default=0, help_text="Documents processed so far")
    progress_percent = models.FloatField(default=0.0, help_text="Progress percentage (0-100)")
    
    # Timing information
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True, help_text="Total session duration")
    
    # Recovery and error handling
    recovery_mode = models.BooleanField(default=False, help_text="Whether this session is in recovery mode")
    error_message = models.TextField(blank=True, null=True, help_text="Error message if session failed")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['status']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['workflow_state']),
        ]
    
    def __str__(self):
        return f"Filming Session {self.session_id} - {self.project.archive_id} ({self.status})"
    
    @property
    def is_active(self):
        """Check if the session is currently active (running or paused)."""
        return self.status in ['running', 'paused']
    
    @property
    def is_completed(self):
        """Check if the session has completed successfully."""
        return self.status == 'completed'
    
    def update_progress(self, processed_docs, total_docs=None):
        """Update session progress."""
        if total_docs:
            self.total_documents = total_docs
        self.processed_documents = processed_docs
        if self.total_documents > 0:
            self.progress_percent = (self.processed_documents / self.total_documents) * 100
        self.save(update_fields=['processed_documents', 'total_documents', 'progress_percent', 'updated_at'])


class FilmingSessionLog(models.Model):
    """Stores log entries for filming sessions."""
    LOG_LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    # Relationships
    session = models.ForeignKey(FilmingSession, on_delete=models.CASCADE, related_name='logs')
    
    # Log information
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES, default='info')
    message = models.TextField(help_text="Log message content")
    workflow_state = models.CharField(max_length=20, blank=True, null=True, help_text="Workflow state when log was created")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', '-created_at']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return f"{self.session.session_id} [{self.level}]: {self.message[:50]}..."


class DevelopmentSession(models.Model):
    """Tracks film development sessions."""
    DEVELOPMENT_STATUS_CHOICES = [
        ('pending', 'Pending Development'),
        ('developing', 'Currently Developing'),
        ('completed', 'Development Completed'),
        ('failed', 'Development Failed'),
    ]
    
    # Session identification
    session_id = models.CharField(max_length=100, unique=True, help_text="Unique development session identifier")
    
    # Relationships
    roll = models.ForeignKey(Roll, on_delete=models.CASCADE, related_name='development_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='development_sessions', null=True, blank=True)
    
    # Development status
    status = models.CharField(max_length=20, choices=DEVELOPMENT_STATUS_CHOICES, default='pending')
    
    # Timing information (30 minute development cycle)
    development_duration_minutes = models.IntegerField(default=30, help_text="Development duration in minutes")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Progress tracking
    progress_percent = models.FloatField(default=0.0, help_text="Development progress percentage (0-100)")
    
    # Chemical usage tracking
    chemical_usage_area = models.FloatField(default=0.0, help_text="Film area processed in m²")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['status']),
            models.Index(fields=['roll']),
        ]
    
    def __str__(self):
        return f"Development Session {self.session_id} - Roll {self.roll.film_number} ({self.status})"
    
    @property
    def is_active(self):
        """Check if the development session is currently active."""
        return self.status == 'developing'
    
    @property
    def is_completed(self):
        """Check if the development session has completed successfully."""
        return self.status == 'completed'
    
    def calculate_chemical_usage(self):
        """Calculate chemical usage based on actual pages used plus leader/trailer."""
        # Total frames = actual pages used + 100 for leader/trailer
        total_frames = self.roll.pages_used + 100
        
        # Each frame is 1cm wide
        film_length_cm = total_frames * 1.0  # 1cm per frame
        film_length_m = film_length_cm / 100.0  # Convert to meters
        
        if self.roll.film_type == FilmType.FILM_16MM:
            # 16mm film height is 16mm = 1.6cm
            film_height_m = 0.016  # 16mm in meters
        else:  # 35mm
            # 35mm film height is 35mm = 3.5cm  
            film_height_m = 0.035  # 35mm in meters
        
        # Calculate area: length × height
        self.chemical_usage_area = film_length_m * film_height_m
        return self.chemical_usage_area

    def calculate_development_duration(self):
        """Calculate development duration based on actual film length.
        
        Development time = film length in meters (1 minute per meter).
        A full roll of 30.5m takes 30.5 minutes to develop.
        """
        # Total frames = actual pages used + 100 for leader/trailer
        total_frames = self.roll.pages_used + 100
        
        # Each frame is 1cm wide
        film_length_cm = total_frames * 1.0  # 1cm per frame
        film_length_m = film_length_cm / 100.0  # Convert to meters
        
        # Development time = 1 minute per meter of film
        development_minutes = film_length_m
        
        return development_minutes

    @property
    def actual_development_duration_minutes(self):
        """Get the actual development duration based on film length."""
        return self.calculate_development_duration()


class ChemicalBatch(models.Model):
    """Tracks chemical batches used in development."""
    CHEMICAL_TYPES = [
        ('developer', 'Developer'),
        ('fixer', 'Fixer'),
        ('cleaner1', 'Cleaner 1'),
        ('cleaner2', 'Cleaner 2'),
    ]
    
    # Chemical information
    chemical_type = models.CharField(max_length=20, choices=CHEMICAL_TYPES)
    batch_id = models.CharField(max_length=50, help_text="Batch identifier")
    
    # Capacity and usage (based on chemical_monitor.py logic)
    max_area = models.FloatField(default=10.0, help_text="Maximum film area this batch can process (m²)")
    used_area = models.FloatField(default=0.0, help_text="Film area already processed (m²)")
    
    # Roll tracking
    used_16mm_rolls = models.IntegerField(default=0, help_text="Number of 16mm rolls processed")
    used_35mm_rolls = models.IntegerField(default=0, help_text="Number of 35mm rolls processed")
    
    # Status and dates
    is_active = models.BooleanField(default=True, help_text="Whether this batch is currently active")
    created_at = models.DateTimeField(auto_now_add=True)
    replaced_at = models.DateTimeField(null=True, blank=True, help_text="When this batch was replaced")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['chemical_type', 'is_active']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_chemical_type_display()} Batch {self.batch_id}"
    
    @property
    def remaining_capacity(self):
        """Calculate remaining capacity in m²."""
        return max(0, self.max_area - self.used_area)
    
    @property
    def capacity_percent(self):
        """Calculate remaining capacity as percentage."""
        return (self.remaining_capacity / self.max_area) * 100 if self.max_area > 0 else 0
    
    @property
    def is_critical(self):
        """Check if chemical level is critical (< 10% remaining)."""
        return self.capacity_percent < 10
    
    @property
    def is_low(self):
        """Check if chemical level is low (< 20% remaining)."""
        return self.capacity_percent < 20
    
    def add_roll_usage(self, film_type, area_used):
        """Add usage for a film roll with actual area used."""
        if film_type == FilmType.FILM_16MM:
            self.used_16mm_rolls += 1
        else:  # 35mm
            self.used_35mm_rolls += 1
        
        # Add the actual area used
        self.used_area += area_used
        
        # Cap at maximum
        self.used_area = min(self.used_area, self.max_area)
        self.save()
    
    def can_process_roll(self, area_needed):
        """Check if this batch can process a roll requiring the given area."""
        return (self.used_area + area_needed) <= self.max_area


class DevelopmentLog(models.Model):
    """Stores log entries for development sessions."""
    LOG_LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    # Relationships
    session = models.ForeignKey(DevelopmentSession, on_delete=models.CASCADE, related_name='logs')
    
    # Log information
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES, default='info')
    message = models.TextField(help_text="Log message content")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', '-created_at']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return f"{self.session.session_id} [{self.level}]: {self.message[:50]}..."


class DensityMeasurement(models.Model):
    """Stores film density measurements taken during development for quality assurance."""
    
    # Relationships
    session = models.ForeignKey(DevelopmentSession, on_delete=models.CASCADE, related_name='density_measurements')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='density_measurements', null=True, blank=True)
    
    # Measurement data
    density_value = models.FloatField(help_text="Measured density value (0.0 - 2.0)")
    measurement_time_minutes = models.IntegerField(help_text="Time in minutes when measurement was taken (e.g., 10, 20, 30)")
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about the measurement")
    
    # Quality assessment
    is_within_optimal_range = models.BooleanField(default=False, help_text="Whether measurement is within optimal range (1.2-1.4)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['session', 'measurement_time_minutes']
        unique_together = ['session', 'measurement_time_minutes']
        indexes = [
            models.Index(fields=['session', 'measurement_time_minutes']),
            models.Index(fields=['density_value']),
            models.Index(fields=['is_within_optimal_range']),
        ]
    
    def __str__(self):
        return f"Density {self.density_value} at {self.measurement_time_minutes}min - {self.session.session_id}"
    
    def save(self, *args, **kwargs):
        """Override save to automatically set is_within_optimal_range."""
        # Optimal range is 1.2 - 1.4
        self.is_within_optimal_range = 1.2 <= self.density_value <= 1.4
        super().save(*args, **kwargs)
    
    @property
    def quality_status(self):
        """Return quality status based on density value."""
        if self.density_value < 1.0:
            return 'too_low'
        elif self.density_value < 1.2:
            return 'low'
        elif self.density_value <= 1.4:
            return 'optimal'
        elif self.density_value <= 1.6:
            return 'high'
        else:
            return 'too_high'
    
    @property
    def quality_color(self):
        """Return color code for UI display."""
        status = self.quality_status
        colors = {
            'too_low': '#dc3545',    # Red
            'low': '#ffc107',        # Yellow
            'optimal': '#28a745',    # Green
            'high': '#ffc107',       # Yellow
            'too_high': '#dc3545'    # Red
        }
        return colors.get(status, '#6c757d')


class FilmLabel(models.Model):
    """Tracks generated film labels with their status and file paths."""
    LABEL_STATUS_CHOICES = [
        ('generated', 'Generated'),
        ('downloaded', 'Downloaded'),
        ('queued', 'Queued for Print'),
        ('printed', 'Printed'),
        ('completed', 'Completed'),
    ]
    
    VERSION_CHOICES = [
        ('normal', 'Normal'),
        ('angled', 'Angled'),
    ]
    
    # Relationships
    roll = models.ForeignKey(Roll, on_delete=models.CASCADE, related_name='film_labels')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='film_labels')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='film_labels', null=True, blank=True)
    
    # Label identification
    label_id = models.CharField(max_length=100, unique=True, help_text="Unique label identifier")
    version = models.CharField(max_length=10, choices=VERSION_CHOICES, default='normal', help_text="Label version (normal or angled)")
    
    # Label content information
    film_number = models.CharField(max_length=50, help_text="Film number on the label")
    archive_id = models.CharField(max_length=20, help_text="Archive ID on the label")
    doc_type = models.CharField(max_length=50, help_text="Document type on the label")
    
    # File paths
    pdf_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path to saved PDF file")
    cache_key = models.CharField(max_length=100, blank=True, null=True, help_text="Cache key for temporary storage")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=LABEL_STATUS_CHOICES, default='generated')
    
    # Timestamps
    generated_at = models.DateTimeField(auto_now_add=True)
    downloaded_at = models.DateTimeField(null=True, blank=True, help_text="When label was first downloaded")
    queued_at = models.DateTimeField(null=True, blank=True, help_text="When label was added to print queue")
    printed_at = models.DateTimeField(null=True, blank=True, help_text="When label was printed")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="When label process was completed")
    
    # Print tracking
    download_count = models.IntegerField(default=0, help_text="Number of times label was downloaded")
    print_count = models.IntegerField(default=0, help_text="Number of times label was printed")
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['label_id']),
            models.Index(fields=['roll', 'status']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['generated_at']),
            models.Index(fields=['roll', 'version']),
        ]
        unique_together = ['roll', 'version']  # Ensure only one label per version per roll
    
    def __str__(self):
        return f"Label {self.label_id} - {self.film_number} ({self.version}, {self.status})"
    
    @property
    def is_completed(self):
        """Check if the label process is completed (generated and printed)."""
        return self.status == 'completed' or (self.printed_at is not None)
    
    @property
    def labels_directory(self):
        """Get the labels directory path for this project."""
        if self.project.project_path:
            return Path(self.project.project_path) / '.labels'
        return None
    
    def mark_downloaded(self):
        """Mark the label as downloaded."""
        if not self.downloaded_at:
            self.downloaded_at = timezone.now()
        self.download_count += 1
        if self.status == 'generated':
            self.status = 'downloaded'
        self.save(update_fields=['downloaded_at', 'download_count', 'status'])
    
    def mark_queued(self):
        """Mark the label as queued for printing."""
        if not self.queued_at:
            self.queued_at = timezone.now()
        self.status = 'queued'
        self.save(update_fields=['queued_at', 'status'])
    
    def mark_printed(self):
        """Mark the label as printed and completed."""
        if not self.printed_at:
            self.printed_at = timezone.now()
        self.print_count += 1
        # Automatically mark as completed when printed (final step)
        if not self.completed_at:
            self.completed_at = timezone.now()
        self.status = 'completed'
        self.save(update_fields=['printed_at', 'print_count', 'completed_at', 'status'])
    
    def mark_completed(self):
        """Mark the label process as completed."""
        if not self.completed_at:
            self.completed_at = timezone.now()
        self.status = 'completed'
        self.save(update_fields=['completed_at', 'status'])


class HandoffRecord(models.Model):
    """Tracks handoff emails sent for projects with validation results and status."""
    HANDOFF_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent Successfully'),
        ('failed', 'Send Failed'),
        ('acknowledged', 'Acknowledged by Recipient'),
        ('completed', 'Handoff Completed'),
    ]
    
    VALIDATION_STATUS_CHOICES = [
        ('not_validated', 'Not Validated'),
        ('validated', 'Validated'),
        ('has_warnings', 'Has Warnings'),
        ('has_errors', 'Has Errors'),
    ]
    
    # Relationships
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='handoff_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='handoff_records', 
                           help_text="User who initiated the handoff")
    
    # Handoff identification
    handoff_id = models.CharField(max_length=100, unique=True, help_text="Unique handoff identifier")
    
    # Email details
    recipient_email = models.EmailField(help_text="Email address of the recipient")
    recipient_name = models.CharField(max_length=255, blank=True, null=True, help_text="Name of the recipient")
    subject = models.CharField(max_length=500, help_text="Email subject line")
    custom_message = models.TextField(blank=True, null=True, help_text="Custom message added to the email")
    
    # Validation summary at time of handoff
    validation_status = models.CharField(max_length=20, choices=VALIDATION_STATUS_CHOICES, default='not_validated')
    total_documents = models.IntegerField(default=0, help_text="Total documents in handoff")
    validated_documents = models.IntegerField(default=0, help_text="Documents that passed validation")
    warning_documents = models.IntegerField(default=0, help_text="Documents with warnings")
    error_documents = models.IntegerField(default=0, help_text="Documents with errors")
    
    # Film roll summary (16mm only as per filtering)
    total_rolls = models.IntegerField(default=0, help_text="Total 16mm rolls included")
    film_numbers = models.TextField(blank=True, null=True, help_text="Comma-separated list of film numbers")
    
    # File attachments
    excel_file_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path to generated Excel file")
    dat_file_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path to generated DAT file")
    excel_file_size = models.BigIntegerField(default=0, help_text="Size of Excel file in bytes")
    dat_file_size = models.BigIntegerField(default=0, help_text="Size of DAT file in bytes")
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=HANDOFF_STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When handoff was initiated")
    sent_at = models.DateTimeField(null=True, blank=True, help_text="When email was successfully sent")
    acknowledged_at = models.DateTimeField(null=True, blank=True, help_text="When recipient acknowledged receipt")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="When handoff was marked as completed")
    
    # Error tracking
    error_message = models.TextField(blank=True, null=True, help_text="Error message if handoff failed")
    retry_count = models.IntegerField(default=0, help_text="Number of retry attempts")
    last_retry_at = models.DateTimeField(null=True, blank=True, help_text="When last retry was attempted")
    
    # Metadata
    outlook_message_id = models.CharField(max_length=255, blank=True, null=True, 
                                        help_text="Outlook message ID for tracking")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of sender")
    user_agent = models.TextField(blank=True, null=True, help_text="User agent string")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['handoff_id']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['sent_at']),
            models.Index(fields=['recipient_email']),
            models.Index(fields=['validation_status']),
        ]
    
    def __str__(self):
        return f"Handoff {self.handoff_id} - {self.project.archive_id} to {self.recipient_email} ({self.status})"
    
    @property
    def is_successful(self):
        """Check if the handoff was sent successfully."""
        return self.status in ['sent', 'acknowledged', 'completed']
    
    @property
    def has_validation_issues(self):
        """Check if there were validation issues at time of handoff."""
        return self.validation_status in ['has_warnings', 'has_errors']
    
    @property
    def validation_summary(self):
        """Get a human-readable validation summary."""
        if self.validation_status == 'not_validated':
            return "Not validated"
        elif self.validation_status == 'validated':
            return f"All {self.total_documents} documents validated"
        elif self.validation_status == 'has_warnings':
            return f"{self.warning_documents} warnings, {self.validated_documents} validated"
        elif self.validation_status == 'has_errors':
            return f"{self.error_documents} errors, {self.warning_documents} warnings, {self.validated_documents} validated"
        return "Unknown status"
    
    @property
    def total_file_size_mb(self):
        """Get total file size in MB."""
        total_bytes = (self.excel_file_size or 0) + (self.dat_file_size or 0)
        return round(total_bytes / (1024 * 1024), 2)
    
    def mark_sent(self, outlook_message_id=None):
        """Mark the handoff as successfully sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if outlook_message_id:
            self.outlook_message_id = outlook_message_id
        self.save(update_fields=['status', 'sent_at', 'outlook_message_id'])
    
    def mark_failed(self, error_message):
        """Mark the handoff as failed with error message."""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.last_retry_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'retry_count', 'last_retry_at'])
    
    def mark_acknowledged(self):
        """Mark the handoff as acknowledged by recipient."""
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.save(update_fields=['status', 'acknowledged_at'])
    
    def mark_completed(self):
        """Mark the handoff as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def get_film_numbers_list(self):
        """Get film numbers as a list."""
        if self.film_numbers:
            return [fn.strip() for fn in self.film_numbers.split(',') if fn.strip()]
        return []
    
    def set_film_numbers_list(self, film_numbers_list):
        """Set film numbers from a list."""
        self.film_numbers = ', '.join(str(fn) for fn in film_numbers_list if fn)
    
    def update_validation_summary(self, validation_results):
        """Update validation summary from validation results."""
        if not validation_results:
            self.validation_status = 'not_validated'
            return
        
        self.total_documents = validation_results.get('total', 0)
        self.validated_documents = validation_results.get('validated', 0)
        self.warning_documents = validation_results.get('warnings', 0)
        self.error_documents = validation_results.get('errors', 0)
        
        # Determine validation status
        if self.error_documents > 0:
            self.validation_status = 'has_errors'
        elif self.warning_documents > 0:
            self.validation_status = 'has_warnings'
        elif self.validated_documents > 0:
            self.validation_status = 'validated'
        else:
            self.validation_status = 'not_validated'
    
    def update_file_info(self, excel_path=None, dat_path=None):
        """Update file paths and sizes."""
        if excel_path:
            self.excel_file_path = excel_path
            try:
                self.excel_file_size = Path(excel_path).stat().st_size
            except (OSError, FileNotFoundError):
                self.excel_file_size = 0
        
        if dat_path:
            self.dat_file_path = dat_path
            try:
                self.dat_file_size = Path(dat_path).stat().st_size
            except (OSError, FileNotFoundError):
                self.dat_file_size = 0


class HandoffValidationSnapshot(models.Model):
    """Stores detailed validation results at the time of handoff for audit purposes."""
    # Relationships
    handoff_record = models.ForeignKey(HandoffRecord, on_delete=models.CASCADE, related_name='validation_snapshots')
    
    # Document details
    document_id = models.CharField(max_length=100, help_text="Document ID (filename)")
    roll_number = models.CharField(max_length=50, help_text="Roll/film number")
    barcode = models.CharField(max_length=100, help_text="Document barcode")
    com_id = models.CharField(max_length=50, blank=True, null=True, help_text="COM ID at time of handoff")
    temp_blip = models.CharField(max_length=50, blank=True, null=True, help_text="Temporary blip code")
    film_blip = models.CharField(max_length=50, blank=True, null=True, help_text="Film log blip code")
    
    # Validation status
    validation_status = models.CharField(max_length=20, help_text="Validation status (validated, warning, error)")
    validation_message = models.TextField(blank=True, null=True, help_text="Validation message or error details")
    
    # Issues identified
    missing_com_id = models.BooleanField(default=False, help_text="Whether COM ID was missing")
    missing_film_blip = models.BooleanField(default=False, help_text="Whether film blip was missing")
    blip_mismatch = models.BooleanField(default=False, help_text="Whether blips didn't match")
    other_issues = models.TextField(blank=True, null=True, help_text="Other validation issues")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['handoff_record', 'document_id']
        indexes = [
            models.Index(fields=['handoff_record', 'validation_status']),
            models.Index(fields=['validation_status']),
            models.Index(fields=['missing_com_id']),
            models.Index(fields=['missing_film_blip']),
            models.Index(fields=['blip_mismatch']),
        ]
    
    def __str__(self):
        return f"{self.document_id} - {self.validation_status} (Handoff {self.handoff_record.handoff_id})"
