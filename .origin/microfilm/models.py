from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
from datetime import datetime
from enum import Enum

class FilmType(Enum):
    """Type of film used for microfilming."""
    FILM_16MM = "16mm"
    FILM_35MM = "35mm"

@dataclass
class DocumentSegment:
    """
    Represents a segment of a document on a film roll.
    
    This can be an entire document or a portion of a document
    that has been split across multiple rolls.
    """
    # Document identification
    doc_id: str                   # Document ID
    path: Path                    # Path to the PDF file
    
    # Page information
    pages: int                    # Number of pages in this segment
    page_range: Tuple[int, int]   # Range of pages from the original document (start, end)
    
    # Frame information
    frame_range: Tuple[int, int]  # Range of frames on the film roll (start, end)
    
    # Position information
    document_index: int           # Position of this document on the roll
    
    # Oversized information
    has_oversized: bool = False   # Whether this segment contains oversized pages
    
    @property
    def start_page(self) -> int:
        """Get the start page of this segment in the original document."""
        return self.page_range[0]
    
    @property
    def end_page(self) -> int:
        """Get the end page of this segment in the original document."""
        return self.page_range[1]
    
    @property
    def start_frame(self) -> int:
        """Get the start frame of this segment on the film roll."""
        return self.frame_range[0]
    
    @property
    def end_frame(self) -> int:
        """Get the end frame of this segment on the film roll."""
        return self.frame_range[1]

@dataclass
class FilmRoll:
    """
    Represents a roll of microfilm with its capacity and contents.
    
    Contains information about the film roll, including its capacity,
    usage statistics, and the documents allocated to it.
    """
    # Core information
    roll_id: int                # Unique identifier for this roll
    film_type: FilmType         # Type of film (16mm or 35mm)
    capacity: int               # Total capacity of the roll in pages
    
    # Usage statistics
    pages_used: int = 0         # Number of pages used on this roll
    pages_remaining: int = 0    # Number of pages remaining on this roll
    
    # Document allocation
    document_segments: List[DocumentSegment] = field(default_factory=list)  # Document segments on this roll
    
    # Film number and status
    film_number: Optional[str] = None  # Film number assigned to this roll
    status: str = "active"       # Status of the roll (active, used, etc.)
    
    # Split document tracking
    has_split_documents: bool = False  # Whether any documents are split across rolls
    
    # Partial roll information
    is_partial: bool = False    # Whether this is a partial roll
    remaining_capacity: int = 0  # Remaining capacity when roll becomes partial
    usable_capacity: int = 0     # Usable capacity accounting for padding
    
    # Metadata
    creation_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_document_segment(self, doc_id: str, path: Path, pages: int, 
                            page_range: Tuple[int, int], has_oversized: bool = False) -> DocumentSegment:
        """
        Add a document segment to this roll.
        
        Args:
            doc_id: Document ID
            path: Path to the PDF file
            pages: Number of pages in this segment
            page_range: Range of pages from the original document (start, end)
            has_oversized: Whether this segment contains oversized pages
            
        Returns:
            The created document segment
        """
        # Calculate next document index
        document_index = len(self.document_segments) + 1
        
        # Calculate frame range
        start_frame = self.pages_used + 1
        end_frame = start_frame + pages - 1
        
        # Create segment
        segment = DocumentSegment(
            doc_id=doc_id,
            path=path,
            pages=pages,
            page_range=page_range,
            frame_range=(start_frame, end_frame),
            document_index=document_index,
            has_oversized=has_oversized
        )
        
        # Update roll statistics
        self.pages_used += pages
        self.pages_remaining -= pages
        
        # Add segment to roll
        self.document_segments.append(segment)
        
        return segment
    
    def get_document_segments(self, doc_id: str) -> List[DocumentSegment]:
        """
        Get all segments of a document on this roll.
        
        Args:
            doc_id: Document ID
            
        Returns:
            List of document segments for the specified document
        """
        return [segment for segment in self.document_segments if segment.doc_id == doc_id]
    
    def is_document_on_roll(self, doc_id: str) -> bool:
        """
        Check if a document is on this roll.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if the document is on this roll, False otherwise
        """
        return any(segment.doc_id == doc_id for segment in self.document_segments)
    
    @property
    def is_full(self) -> bool:
        """Check if the roll is full (no remaining capacity)."""
        return self.pages_remaining <= 0
    
    @property
    def utilization(self) -> float:
        """Calculate the utilization percentage of this roll."""
        return (self.pages_used / self.capacity) * 100 if self.capacity > 0 else 0
    
    @property
    def document_ids(self) -> List[str]:
        """Get the list of document IDs on this roll."""
        return list(set(segment.doc_id for segment in self.document_segments))

    def generate_blip(self, doc_index: int, frame_start: int) -> str:
        """
        Generate a blip for a document on this roll.
        
        Args:
            doc_index: Document index on the roll
            frame_start: Starting frame number
            
        Returns:
            Blip string in the format "{film_number}-{doc_index:04d}.{frame_start:05d}"
        """
        if not self.film_number:
            raise ValueError("Cannot generate blip without a film number")
        
        return f"{self.film_number}-{doc_index:04d}.{frame_start:05d}"

@dataclass
class FilmAllocation:
    """
    Represents the allocation of documents to film rolls.
    
    Contains information about how documents are allocated to film rolls,
    including statistics and the rolls themselves.
    """
    # Project information
    archive_id: str             # Archive ID of the project
    project_name: str           # Name of the project
    
    # Film rolls
    rolls_16mm: List[FilmRoll] = field(default_factory=list)  # 16mm film rolls
    rolls_35mm: List[FilmRoll] = field(default_factory=list)  # 35mm film rolls
    
    # Split document tracking
    split_documents_16mm: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)  # Details of split docs on 16mm
    split_documents_35mm: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)  # Details of split docs on 35mm
    
    # Partial roll tracking
    partial_rolls_16mm: List[Dict[str, Any]] = field(default_factory=list)  # Partial 16mm rolls
    partial_rolls_35mm: List[Dict[str, Any]] = field(default_factory=list)  # Partial 35mm rolls
    
    # Statistics
    total_rolls_16mm: int = 0   # Total number of 16mm rolls
    total_pages_16mm: int = 0   # Total pages allocated to 16mm
    total_partial_rolls_16mm: int = 0  # Number of partial 16mm rolls
    total_split_documents_16mm: int = 0  # Number of documents split across 16mm rolls
    
    total_rolls_35mm: int = 0   # Total number of 35mm rolls
    total_pages_35mm: int = 0   # Total pages allocated to 35mm
    total_partial_rolls_35mm: int = 0  # Number of partial 35mm rolls
    total_split_documents_35mm: int = 0  # Number of documents split across 35mm rolls
    
    # Metadata
    creation_date: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    
    # Add this to the FilmAllocation class
    doc_allocation_requests_35mm = []  # For storing document allocation requests
    
    def get_document_rolls(self, doc_id: str, film_type: FilmType) -> List[FilmRoll]:
        """
        Get all rolls containing segments of a document.
        
        Args:
            doc_id: Document ID
            film_type: Type of film
            
        Returns:
            List of film rolls containing the document
        """
        if film_type == FilmType.FILM_16MM:
            rolls = self.rolls_16mm
        else:
            rolls = self.rolls_35mm
        
        return [roll for roll in rolls if roll.is_document_on_roll(doc_id)]
    
    def update_statistics(self) -> None:
        """Update all statistics for this allocation."""
        # Update 16mm statistics
        self.total_rolls_16mm = len(self.rolls_16mm)
        self.total_pages_16mm = sum(roll.pages_used for roll in self.rolls_16mm)
        self.total_partial_rolls_16mm = len(self.partial_rolls_16mm)
        self.total_split_documents_16mm = len(self.split_documents_16mm)
        
        # Update 35mm statistics
        self.total_rolls_35mm = len(self.rolls_35mm)
        self.total_pages_35mm = sum(roll.pages_used for roll in self.rolls_35mm)
        self.total_partial_rolls_35mm = len(self.partial_rolls_35mm)
        self.total_split_documents_35mm = len(self.split_documents_35mm)

@dataclass
class Document:
    """
    Represents a PDF document in a microfilming project.
    
    Contains metadata about the document and its pages, especially information
    about oversized pages and processing status.
    """
    # Core identifying information
    doc_id: str              # Document ID (usually numeric, extracted from filename)
    path: Path               # Full path to the PDF file
    
    # Page information
    pages: int = 0           # Total number of pages in the document
    
    # Oversized page information
    has_oversized: bool = False  # Whether document contains any oversized pages
    total_oversized: int = 0     # Count of oversized pages in the document
    
    # Detailed page information
    dimensions: List[Tuple[float, float, int, float]] = field(default_factory=list)  # (width, height, page_idx, percent_over)
    ranges: List[Tuple[int, int]] = field(default_factory=list)  # (start_page, end_page) ranges of oversized pages
    
    # Reference sheet information
    reference_pages: List[int] = field(default_factory=list)  # Positions where reference sheets should be inserted
    total_references: int = 0  # Number of reference sheets for this document
    
    # Additional reference information
    references: Dict[str, Any] = field(default_factory=dict)  # Complete reference info including adjusted ranges
    readable_pages: List[str] = field(default_factory=list)  # Human-readable page descriptions
    adjusted_ranges: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # Original to adjusted page mapping
    
    # Film allocation information
    is_split: bool = False   # Whether document is split across film rolls
    roll_count: int = 1      # Number of rolls this document spans
    
    # COM ID from Excel file
    com_id: Optional[int] = None  # COM ID from comlist Excel file
    
    @property
    def total_pages_with_refs(self) -> int:
        """Get the total number of pages including reference sheets."""
        return self.pages + self.total_references

@dataclass
class Project:
    """
    Represents a microfilming project with its metadata and processing status.
    
    A Project is the central entity in the microfilm processing system,
    containing all the necessary information about a specific archiving job.
    """
    # Core identifying information
    archive_id: str           # Format: RRDxxx-xxxx (e.g., "RRD018-2024")
    location: str             # Location code (e.g., "OU" or "DW")
    
    # Path information
    project_path: Path        # Path to the parent folder (project root)
    project_folder_name: str  # Name of the project folder
    
    # Document folder information
    document_folder_path: Optional[Path] = None  # Path to subfolder containing documents
    document_folder_name: Optional[str] = None   # Name of the document subfolder
    
    # Document type information
    doc_type: str = ""        # Document type (e.g., "FAIR")
    
    # Processing state
    has_oversized: bool = False      # Whether project contains oversized pages
    total_pages: int = 0             # Total number of pages across all documents
    total_pages_with_refs: int = 0   # Total pages including reference sheets
    total_oversized: int = 0         # Total number of oversized pages
    documents_with_oversized: int = 0  # Number of documents with oversized pages
    
    # Output location
    output_dir: Optional[Path] = None  # Path to output directory
    
    # External resources
    comlist_path: Optional[Path] = None  # Path to the COM list Excel file
    
    # Document collection
    documents: List[Document] = field(default_factory=list)  # List of documents in the project
    
    # Film allocation
    film_allocation: Optional[FilmAllocation] = None  # Film allocation for this project
    
    # Distribution results
    distribution_results = None  # Will store results of document distribution
    
    @property
    def location_code(self) -> str:
        """
        Get the numeric location code used for film number allocation.
        
        Returns:
            "1" for OU, "2" for DW, "3" for other locations
        """
        location_map = {
            "OU": "1",
            "DW": "2"
        }
        return location_map.get(self.location, "3")
    
    @property
    def has_document_folder(self) -> bool:
        """Check if a document folder has been found."""
        return self.document_folder_path is not None
    
    @property
    def documents_path(self) -> Path:
        """
        Get the path where documents are located.
        
        Returns:
            Path to the document folder if found, otherwise the project path
        """
        return self.document_folder_path or self.project_path
    
    @property
    def is_initialized(self) -> bool:
        """
        Check if the project is properly initialized.
        
        Returns:
            True if the project has required fields populated
        """
        return bool(
            self.archive_id and 
            self.location and 
            self.project_path and 
            self.project_folder_name
        )

class FilmNumber:
    """
    Represents a film number assigned to a film roll.
    
    Film numbers follow a specific format based on location:
    - OU location: Film numbers start with '1' (e.g., 10000001)
    - DW location: Film numbers start with '2' (e.g., 20000001)
    - Other locations: Film numbers start with '3' (e.g., 30000001)
    """
    
    def __init__(self, number: str, location_code: str = None, source: str = "new"):
        """
        Initialize a FilmNumber object.
        
        Args:
            number: The film number string
            location_code: The location code this film number belongs to
            source: Source of this film number ('new', 'temp_roll', or 'active')
        """
        self.number = number
        self.location_code = location_code
        self.source = source
    
    @classmethod
    def from_location(cls, location_code: str, sequence_number: int) -> 'FilmNumber':
        """
        Create a film number based on location code and sequence number.
        
        Args:
            location_code: Location code ('OU', 'DW', etc.)
            sequence_number: Sequential number to use
            
        Returns:
            FilmNumber object with properly formatted number
        """
        prefix = '1'  # Default (OU)
        
        if location_code == 'DW':
            prefix = '2'
        elif location_code not in ('OU', 'DW'):
            prefix = '3'  # Other locations
            
        # Format: [prefix][7-digit sequential number]
        number = f"{prefix}{sequence_number:07d}"
        return cls(number, location_code)
    
    def __str__(self) -> str:
        return self.number


class TempRoll:
    """
    Represents a temporary roll with remaining capacity that can be used for future allocations.
    
    Temp rolls are created from partial rolls and can be reused across projects.
    """
    
    def __init__(
        self,
        temp_roll_id: int,
        film_type: FilmType,
        total_capacity: int,
        usable_capacity: int,
        source_roll_id: int = None,
        creation_date: str = None
    ):
        """
        Initialize a TempRoll object.
        
        Args:
            temp_roll_id: Database ID for this temp roll
            film_type: Type of film (16mm or 35mm)
            total_capacity: Total remaining capacity in pages
            usable_capacity: Usable capacity (after padding)
            source_roll_id: ID of the roll this temp roll was created from
            creation_date: Date this temp roll was created
        """
        self.temp_roll_id = temp_roll_id
        self.film_type = film_type
        self.total_capacity = total_capacity
        self.usable_capacity = usable_capacity
        self.source_roll_id = source_roll_id
        self.creation_date = creation_date
        self.status = "available"
        self.used_by_roll_id = None
    
    def mark_used(self, used_by_roll_id: int) -> None:
        """
        Mark this temp roll as used by a specific roll.
        
        Args:
            used_by_roll_id: ID of the roll that used this temp roll
        """
        self.status = "used"
        self.used_by_roll_id = used_by_roll_id
    
    def can_accommodate(self, pages_needed: int) -> bool:
        """
        Check if this temp roll can accommodate the specified number of pages.
        
        Args:
            pages_needed: Number of pages needed
            
        Returns:
            True if this temp roll has sufficient capacity, False otherwise
        """
        return (
            self.status == "available" and 
            self.usable_capacity >= pages_needed
        )
    
    def get_remaining_after_use(self, pages_used: int) -> int:
        """
        Calculate remaining capacity after using specified pages.
        
        Args:
            pages_used: Number of pages to use
            
        Returns:
            Remaining capacity in pages
        """
        if not self.can_accommodate(pages_used):
            return 0
        return self.usable_capacity - pages_used


class DocumentBlip:
    """
    Represents a blip generated for a document on a film roll.
    
    Blips follow the format: "{film_number}-{doc_index:04d}.{frame_start:05d}"
    Example: "10000001-0001.00001"
    """
    
    def __init__(self, film_number: str, doc_index: int, frame_start: int):
        """
        Initialize a DocumentBlip object.
        
        Args:
            film_number: Film number for this document
            doc_index: Document index (position on roll)
            frame_start: Starting frame number for this document
        """
        self.film_number = film_number
        self.doc_index = doc_index
        self.frame_start = frame_start
        self.blip = self._generate_blip()
    
    def _generate_blip(self) -> str:
        """
        Generate a blip string based on film number, document index, and frame start.
        
        Returns:
            Formatted blip string
        """
        return f"{self.film_number}-{self.doc_index:04d}.{self.frame_start:05d}"
    
    def __str__(self) -> str:
        return self.blip


# Extend FilmAllocation to support film number tracking
class FilmAllocationWithNumbers(FilmAllocation):
    """
    Extended version of FilmAllocation that includes film number tracking.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize with parent class constructor"""
        super().__init__(*args, **kwargs)
        # Add film number mappings
        self.film_numbers = {}  # Dict mapping roll_id to film number
    
    def assign_film_number(self, roll_id: str, film_number: str, source: str = "new") -> None:
        """
        Assign a film number to a specific roll.
        
        Args:
            roll_id: ID of the roll to assign the number to
            film_number: Film number to assign
            source: Source of this film number ('new', 'temp_roll', or 'active')
        """
        # Find the roll and assign number
        roll = self.get_roll_by_id(roll_id)
        if roll:
            roll.film_number = film_number
            roll.film_number_source = source
            # Also add to the mapping
            self.film_numbers[roll_id] = film_number
    
    def get_film_number(self, roll_id: str) -> Optional[str]:
        """
        Get the film number assigned to a specific roll.
        
        Args:
            roll_id: ID of the roll
            
        Returns:
            Film number if assigned, None otherwise
        """
        return self.film_numbers.get(roll_id)
    
    def get_roll_by_id(self, roll_id: str) -> Optional[FilmRoll]:
        """
        Get a film roll by its ID.
        
        Args:
            roll_id: ID of the roll
            
        Returns:
            FilmRoll object if found, None otherwise
        """
        # Search in 16mm rolls
        for roll in self.rolls_16mm:
            if roll.roll_id == roll_id:
                return roll
                
        # Search in 35mm rolls
        for roll in self.rolls_35mm:
            if roll.roll_id == roll_id:
                return roll
                
        return None

class RollReferenceInfo:
    def __init__(self, roll_id, film_number):
        self.roll_id = roll_id
        self.film_number = film_number
        self.is_new_roll = False
        self.previous_project_id = None
        self.last_blipend = None
        self.last_frame_position = 1
        self.documents = {}  # Map of doc_id to DocumentReferenceInfo

class DocumentReferenceInfo:
    def __init__(self, doc_id, roll_id):
        self.doc_id = doc_id
        self.roll_id = roll_id
        self.ranges = []  # List of RangeReferenceInfo objects
        self.is_split = False

class RangeReferenceInfo:
    def __init__(self, range_start, range_end, position):
        self.range_start = range_start
        self.range_end = range_end
        self.position = position  # Index in document's ranges
        self.frame_start = None
        self.blip = None
        self.blipend = None
