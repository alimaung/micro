from django.db import models
from django.contrib.auth.models import User

class FilmType(models.TextChoices):
    """Type of film used for microfilming."""
    FILM_16MM = "16mm", "16mm"
    FILM_35MM = "35mm", "35mm"

class Project(models.Model):
    # Core project identification
    archive_id = models.CharField(max_length=20, help_text="Format: RRDxxx-yyyy")
    location = models.CharField(max_length=10, help_text="Location code (e.g., OU, DW)")
    doc_type = models.CharField(max_length=50, blank=True, null=True)
    
    # Path information
    project_path = models.CharField(max_length=500)
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
        return f"{self.archive_id} ({self.location})"
    
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
    roll_id = models.PositiveIntegerField(unique=True, blank=True, null=True)  # Not primary key
    film_number = models.CharField(max_length=50, blank=True, null=True, help_text="Film number assigned to this roll")
    film_type = models.CharField(max_length=10, choices=FilmType.choices, help_text="Type of film (16mm or 35mm)")
    
    # Capacity and usage
    capacity = models.IntegerField(help_text="Total capacity of the roll in pages")
    pages_used = models.IntegerField(default=0, help_text="Number of pages used on this roll")
    pages_remaining = models.IntegerField(default=0, help_text="Number of pages remaining on this roll")
    
    # Status and metadata
    status = models.CharField(max_length=20, default="active", help_text="Status of the roll (active, used, etc.)")
    has_split_documents = models.BooleanField(default=False, help_text="Whether any documents are split across rolls")
    creation_date = models.DateTimeField(auto_now_add=True)
    
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
        return f"Roll {self.roll_id}: {self.film_number or 'No film number'} ({self.film_type})"
    
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
